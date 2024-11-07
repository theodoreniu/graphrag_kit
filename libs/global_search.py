import os

import pandas as pd
import tiktoken

from graphrag.query.indexer_adapters import read_indexer_entities, read_indexer_reports
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch

import libs.config as config
from libs.store_vector import PG, get_embedding_store
import asyncio
from graphrag.query.llm.base import BaseLLM, BaseLLMCallback

async def run_global_search(
        rag_version: str, 
        db:str, 
        query: str,
        callbacks: list[BaseLLMCallback] | None = None,
        ):
    
    input_dir = f"/app/index/{config.tenant_name}/{rag_version}/output/artifacts"

    # LLM setup
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

    # Load community reports as context for global search
    COMMUNITY_REPORT_TABLE = "create_final_community_reports"
    ENTITY_TABLE = "create_final_nodes"
    ENTITY_EMBEDDING_TABLE = "create_final_entities"

    # community level in the Leiden community hierarchy from which we will load the community reports
    # higher value means we use reports from more fine-grained communities (at the cost of higher computation cost)
    COMMUNITY_LEVEL = 2

    entity_df = pd.read_parquet(f"{input_dir}/{ENTITY_TABLE}.parquet")
    report_df = pd.read_parquet(f"{input_dir}/{COMMUNITY_REPORT_TABLE}.parquet")
    entity_embedding_df = pd.read_parquet(f"{input_dir}/{ENTITY_EMBEDDING_TABLE}.parquet")

    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)
    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)
    print(f"Total report count: {len(report_df)}")
    print(
        f"Report count after filtering by community level {COMMUNITY_LEVEL}: {len(reports)}"
    )
    report_df.head()

    # Build global context based on community reports

    context_builder = GlobalCommunityContext(
        community_reports=reports,
        entities=entities,  # default to None if you don't want to use community weights for ranking
        token_encoder=token_encoder,
    )   

    # Perform global search
    context_builder_params = {
        "use_community_summary": False,  # False means using full community reports. True means using community short summaries.
        "shuffle_data": True,
        "include_community_rank": True,
        "min_community_rank": 0,
        "community_rank_name": "rank",
        "include_community_weight": True,
        "community_weight_name": "occurrence weight",
        "normalize_community_weight": True,
        "max_tokens": 12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
        "context_name": "Reports",
    }

    map_llm_params = {
        "max_tokens": 1000,
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
    }

    reduce_llm_params = {
        "max_tokens": 2000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 1000-1500)
        "temperature": 0.0,
    }

    search_engine = GlobalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        max_data_tokens=12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
        map_llm_params=map_llm_params,
        reduce_llm_params=reduce_llm_params,
        allow_general_knowledge=False,  # set this to True will add instruction to encourage the LLM to incorporate general knowledge in the response, which may increase hallucinations, but could be useful in some use cases.
        json_mode=True,  # set this to False if your LLM model does not support JSON mode.
        context_builder_params=context_builder_params,
        concurrent_coroutines=32,
        callbacks=callbacks,
        response_type="multiple paragraphs",  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
    )

    result = await search_engine.asearch(
        query=query,
    )

    print(result.response)

    # inspect the data used to build the context for the LLM responses
    # result.context_data["reports"]

    # inspect number of LLM calls and tokens
    print(f"LLM calls: {result.llm_calls}. LLM tokens: {result.prompt_tokens}")

    return result