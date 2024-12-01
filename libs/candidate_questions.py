
import pandas as pd
import tiktoken

from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
import libs.config as config
from libs.store_vector import get_embedding_store
from graphrag.query.llm.base import BaseLLMCallback

async def run_candidate_questions(
        project_name: str,
        db:str, 
        question_history: list[str],
        callbacks: list[BaseLLMCallback] | None = None,
        ):
    input_dir = f"/app/projects/{project_name}/output/artifacts"

    # Load tables to dataframes

    COMMUNITY_REPORT_TABLE = "create_final_community_reports"
    ENTITY_TABLE = "create_final_nodes"
    ENTITY_EMBEDDING_TABLE = "create_final_entities"
    RELATIONSHIP_TABLE = "create_final_relationships"
    COVARIATE_TABLE = "create_final_covariates"
    TEXT_UNIT_TABLE = "create_final_text_units"
    COMMUNITY_LEVEL = 2

    # Read entities

    # read nodes table to get community and degree data
    entity_df = pd.read_parquet(f"{input_dir}/{ENTITY_TABLE}.parquet")
    entity_embedding_df = pd.read_parquet(f"{input_dir}/{ENTITY_EMBEDDING_TABLE}.parquet")

    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)

    # load description embeddings to an in-memory lancedb vectorstore
    # to connect to a remote db, specify url and port values.
    embedding_store = get_embedding_store(db=db,project_name=project_name)

    print(f"Entity count: {len(entity_df)}")
    entity_df.head()

    # Read relationships
    relationship_df = pd.read_parquet(f"{input_dir}/{RELATIONSHIP_TABLE}.parquet")
    relationships = read_indexer_relationships(relationship_df)

    print(f"Relationship count: {len(relationship_df)}")
    relationship_df.head()

    # NOTE: covariates are turned off by default, because they generally need prompt tuning to be valuable
    # Please see the GRAPHRAG_CLAIM_* settings
    # covariate_df = pd.read_parquet(f"{input_dir}/{COVARIATE_TABLE}.parquet")

    # claims = read_indexer_covariates(covariate_df)

    # print(f"Claim records: {len(claims)}")
    # covariates = {"claims": claims}

    # Read community reports

    report_df = pd.read_parquet(f"{input_dir}/{COMMUNITY_REPORT_TABLE}.parquet")
    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)

    print(f"Report records: {len(report_df)}")
    report_df.head()

    # Read text units

    text_unit_df = pd.read_parquet(f"{input_dir}/{TEXT_UNIT_TABLE}.parquet")
    text_units = read_indexer_text_units(text_unit_df)

    print(f"Text unit records: {len(text_unit_df)}")
    text_unit_df.head()


    llm = ChatOpenAI(
        api_type=OpenaiApiType.AzureOpenAI,
        api_key=config.search_azure_api_key,
        deployment_name=config.search_azure_chat_deployment_name,
        model=config.search_azure_chat_model_id,
        api_base=config.search_azure_api_base,
        api_version=config.search_azure_api_version,
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")

    text_embedder = OpenAIEmbedding(
        api_type=OpenaiApiType.AzureOpenAI,
        api_key=config.azure_embedding_api_key,
        api_base=config.azure_embedding_api_base,
        api_version=config.azure_embedding_api_version,
        deployment_name=config.azure_embedding_deployment_name,
        model=config.azure_embedding_model_id,
        max_retries=20,
    )

    # Create local search context builder

    context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities,
        relationships=relationships,
        # if you did not run covariates during indexing, set this to None
        # covariates=covariates,
        entity_text_embeddings=embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,  # if the vectorstore uses entity title as ids, set this to EntityVectorStoreKey.TITLE
        text_embedder=text_embedder,
        token_encoder=token_encoder,
    )


    # text_unit_prop: proportion of context window dedicated to related text units
    # community_prop: proportion of context window dedicated to community reports.
    # The remaining proportion is dedicated to entities and relationships. Sum of text_unit_prop and community_prop should be <= 1
    # conversation_history_max_turns: maximum number of turns to include in the conversation history.
    # conversation_history_user_turns_only: if True, only include user queries in the conversation history.
    # top_k_mapped_entities: number of related entities to retrieve from the entity description embedding store.
    # top_k_relationships: control the number of out-of-network relationships to pull into the context window.
    # include_entity_rank: if True, include the entity rank in the entity table in the context window. Default entity rank = node degree.
    # include_relationship_weight: if True, include the relationship weight in the context window.
    # include_community_rank: if True, include the community rank in the context window.
    # return_candidate_context: if True, return a set of dataframes containing all candidate entity/relationship/covariate records that
    # could be relevant. Note that not all of these records will be included in the context window. The "in_context" column in these
    # dataframes indicates whether the record is included in the context window.
    # max_tokens: maximum number of tokens to use for the context window.


    local_context_params = {
        "text_unit_prop": 0.5,
        "community_prop": 0.1,
        "conversation_history_max_turns": 5,
        "conversation_history_user_turns_only": True,
        "top_k_mapped_entities": 10,
        "top_k_relationships": 10,
        "include_entity_rank": True,
        "include_relationship_weight": True,
        "include_community_rank": False,
        "return_candidate_context": False,
        "embedding_vectorstore_key": EntityVectorStoreKey.ID,  # set this to EntityVectorStoreKey.TITLE if the vectorstore uses entity title as ids
        "max_tokens": 12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
    }

    llm_params = {
        "max_tokens": 2_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 1000=1500)
        "temperature": 0.0,
    }


    # Question Generation
    # This function takes a list of user queries and generates the next candidate questions.

    question_generator = LocalQuestionGen(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        llm_params=llm_params,
        callbacks=callbacks,
        context_builder_params=local_context_params,
    )

    candidate_questions = await question_generator.agenerate(
        question_history=question_history, context_data=None, question_count=5
    )
    
    return candidate_questions


