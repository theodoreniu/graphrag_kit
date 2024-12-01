
import pandas as pd
import streamlit as st
import os

from graphrag.query.indexer_adapters import (
    read_indexer_entities,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from libs.pgvector import PgVectorStore
from theodoretools.fs import list_subdirectories
import libs.config as config
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from libs.azure_ai_search import AzureAISearch

PG = 'PostgreSQL Vector'
MILVUS = 'milvus'
LANCE = 'lance'
AI_SEARCH = 'Azure AI Search'


def store_vector(project_name: str):

    if not config.disable_aisearch and st.button(f'Store data on {AI_SEARCH}', key=f"store_vector_aisearch_{project_name}"):
            store_vector_pgvector(project_name=project_name, db=AI_SEARCH)

    if not config.disable_pgvector and st.button(f'Store data on {PG}', key=f"store_vector_pg_{project_name}"):
            store_vector_pgvector(project_name=project_name, db=PG)
            
    # if st.button('Store LanceDB', key=f"store_vector_lance_{project_name}"):
    #         store_vector_pgvector(project_name=project_name, db=LANCE)
    # if st.button('Store Milvus', key=f"store_vector_milvus_{project_name}"):
    #         store_vector_pgvector(project_name=project_name, db=MILVUS)


def store_vector_pgvector(project_name: str, db: str=PG):
    base_path = f"/app/projects/{project_name}"
    
    subdirectories = list_subdirectories(path=f"{base_path}/output")
    if len(subdirectories) == 0:
        st.error("Your need to build index first.")
        return
    
    with st.spinner(f'Reading ...'):
        create_final_entities = f"{base_path}/output/create_final_entities.parquet"
        if not os.path.exists(create_final_entities):
            st.error(f"No {create_final_entities} by graphrag.index, please check log.")
            return
    
    with st.spinner(f'Processing ...'):
        community_level = 2
        input_dir = f"{base_path}/output"
        entity_df = pd.read_parquet(f"{input_dir}/create_final_nodes.parquet")
        entity_embedding_df = pd.read_parquet(f"{input_dir}/create_final_entities.parquet")
        entities = read_indexer_entities(entity_df, entity_embedding_df, community_level)

        embedding_store = get_embedding_store(db=db, project_name=project_name)

        if db == PG:
            embedding_store.truncate_table()
            st.write(f"Your table is truncated")

        st.write(f"Starting to store embeddings ...")
        store_entity_semantic_embeddings(
            entities=entities,
            vectorstore=embedding_store
        )
        st.success(f"Semantic embeddings stored") 


def get_embedding_store(db:str, project_name:str):
    if db == PG:
        return get_pg_vector_store(project_name)
    if db == MILVUS:
        return get_mivlus_store(project_name)
    if db == LANCE:
        return get_lancedb_store(project_name)
    if db == AI_SEARCH:
        return get_ai_search_store(project_name)
    
    raise Exception(f"Unknown db {db}")


def get_pg_vector_store(project_name: str):
        collection_name = f"entity_embeddings_{project_name}"
        embedding_store = PgVectorStore(
            collection_name=collection_name,
        )
        embedding_store.connect(
            host=os.getenv('POSTGRES_HOST'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            port=os.getenv('POSTGRES_PORT', '5432'),
        )

        return embedding_store


def get_lancedb_store(project_name: str):
        db_uri = '/data/lancedb'
        collection_name = f"entity_embeddings_{project_name}"
        embedding_store = LanceDBVectorStore(
            db_uri=db_uri,
            collection_name=collection_name,
            overwrite=True,
        )
        embedding_store.connect(
            db_uri=db_uri
        )
        return embedding_store


def get_ai_search_store(project_name: str):
        collection_name = f"entity_embeddings_{project_name}"
        embedding_store = AzureAISearch(
             collection_name=collection_name
        )
        embedding_store.connect(
            url=config.ai_search_url,
            api_key=config.ai_search_key,
        )
        return embedding_store


def get_mivlus_store(project_name: str):
    raise Exception("Not implemented yet")
