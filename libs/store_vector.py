
import asyncio
import logging
import sys
import time
import tracemalloc
import requests
import uuid
import tiktoken
import pandas as pd
import streamlit as st
import zipfile
import os
import re
import base64
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_javascript import st_javascript

from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.indexer_adapters import (
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from libs.pgvector import PgVectorStore
from libs.common import delete_rag_version, rag_version_exists, run_command, javascript_code, get_rag_versions, format_rag_version
from io import StringIO
from pathlib import Path
from openai import OpenAI
from theodoretools.url import url_to_name
from theodoretools.fs import list_subdirectories
import pdfplumber
import csv
import fitz
import streamlit_authenticator as stauth
from  libs.common import is_login
import libs.config as config
from typing import Literal
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from libs.azure_ai_search import AzureAISearch

PG = 'PostgreSQL Vector'
MILVUS = 'milvus'
LANCE = 'lance'
AI_SEARCH = 'Azure AI Search'

def store_vector(rag_version: str):

    if not config.disable_aisearch and st.button(f'Store data on {AI_SEARCH}', key=f"store_vector_aisearch_{rag_version}"):
            store_vector_pgvector(rag_version=rag_version, db=AI_SEARCH) 

    if not config.disable_pgvector and st.button(f'Store data on {PG}', key=f"store_vector_pg_{rag_version}"):
            store_vector_pgvector(rag_version=rag_version, db=PG) 
            
    # if st.button('Store LanceDB', key=f"store_vector_lance_{rag_version}"):
    #         store_vector_pgvector(rag_version=rag_version, db=LANCE) 
    # if st.button('Store Milvus', key=f"store_vector_milvus_{rag_version}"):
    #         store_vector_pgvector(rag_version=rag_version, db=MILVUS) 

def store_vector_pgvector(rag_version: str, db: str = PG):
    base_path = f"/app/index/{config.tenant_name}/{rag_version}"
    
    subdirectories = list_subdirectories(path=f"{base_path}/output")
    if len(subdirectories) == 0:
        st.error("Your need to build index first.")
        return
    
    with st.spinner(f'Reading ...'):
        create_final_entities = f"{base_path}/output/artifacts/create_final_entities.parquet"
        if not os.path.exists(create_final_entities):
            st.error(f"No {create_final_entities} by graphrag.index, please check log.")
            return
    
    with st.spinner(f'Processing ...'):
        community_level = 2
        input_dir = f"{base_path}/output/artifacts"
        entity_df = pd.read_parquet(f"{input_dir}/create_final_nodes.parquet")
        entity_embedding_df = pd.read_parquet(f"{input_dir}/create_final_entities.parquet")
        entities = read_indexer_entities(entity_df, entity_embedding_df, community_level)

        embedding_store = get_embedding_store(db=db, rag_version=rag_version)

        if db == PG:
            embedding_store.truncate_table()
            st.write(f"Your table is truncated")

        st.write(f"Starting to store embeddings ...")
        store_entity_semantic_embeddings(
            entities=entities,
            vectorstore=embedding_store
        )
        st.success(f"Semantic embeddings stored") 


def get_embedding_store(db:str,rag_version:str):
    if db == PG:
        return get_pg_vector_store(rag_version)
    if db == MILVUS:
        return get_mivlus_store(rag_version)
    if db == LANCE:
        return get_lancedb_store(rag_version)
    if db == AI_SEARCH:
        return get_ai_search_store(rag_version)
    
    raise Exception(f"Unknown db {db}")


def get_pg_vector_store(rag_version: str):
        collection_name=f"entity_embeddings_{config.tenant_name}_{rag_version}"
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

def get_lancedb_store(rag_version: str):
        db_uri='/data/lancedb'
        collection_name=f"entity_embeddings_{config.tenant_name}_{rag_version}"
        embedding_store = LanceDBVectorStore(
            db_uri=db_uri,
            collection_name=collection_name,
            overwrite=True,
        )
        embedding_store.connect(
            db_uri=db_uri
        )
        return embedding_store

def get_ai_search_store(rag_version: str):
        collection_name=f"entity_embeddings_{config.tenant_name}_{rag_version}"
        embedding_store = AzureAISearch(
             collection_name=collection_name
        )
        embedding_store.connect(
            url=config.ai_search_url,
            api_key=config.ai_search_key,
        )
        return embedding_store

def get_mivlus_store(rag_version: str):
    raise Exception("Not implemented yet")
