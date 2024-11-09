# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A package containing the Azure AI Search  vector store implementation."""
import json
from graphrag.vector_stores.azure_ai_search import AzureAISearch
from graphrag.vector_stores.base import (
    VectorStoreDocument,
)
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)
from libs.common import debug

class AzureAISearch(AzureAISearch):
    """The Azure AI Search vector storage implementation."""

    def load_documents(
        self, documents: list[VectorStoreDocument], overwrite: bool = True
    ) -> None:
        """Load documents into an Azure AI Search index."""
        if overwrite:
            if self.collection_name in self.index_client.list_index_names():
                self.index_client.delete_index(self.collection_name)

            # Configure vector search profile
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="HnswAlg",
                        parameters=HnswParameters(
                            metric=VectorSearchAlgorithmMetric.COSINE
                        ),
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name=self.vector_search_profile_name,
                        algorithm_configuration_name="HnswAlg",
                    )
                ],
            )
            # Configure the index
            index = SearchIndex(
                name=self.collection_name,
                fields=[
                    SimpleField(
                        name="id",
                        type=SearchFieldDataType.String,
                        key=True,
                    ),
                    SearchField(
                        name="vector",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=self.vector_size,
                        vector_search_profile_name=self.vector_search_profile_name,
                    ),
                    SearchableField(name="text", type=SearchFieldDataType.String),
                    SimpleField(
                        name="attributes",
                        type=SearchFieldDataType.String,
                    ),
                ],
                vector_search=vector_search,
            )
            self.index_client.create_or_update_index(
                index,
            )

        batch = [
            {
                "id": doc.id,
                "vector": doc.vector,
                "text": doc.text,
                "attributes": json.dumps(doc.attributes),
            }
            for doc in documents
            if doc.vector is not None
        ]


        # save the batch by self.db_connection.upload_documents(batch) each 100 items
        batch_size = 200
        num_batches = len(batch) // batch_size + (1 if len(batch) % batch_size!= 0 else 0)

        for i in range(num_batches):
            start_index = i * batch_size
            end_index = min((i + 1) * batch_size, len(batch))
            current_batch = batch[start_index:end_index]
            self.db_connection.upload_documents(current_batch)
            debug(f"Uploaded {len(current_batch)} items")

        if len(batch) > 0:
            self.db_connection.upload_documents(batch)
