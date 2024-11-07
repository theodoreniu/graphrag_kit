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
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.query.structured_search.global_search.search import GlobalSearch

from libs.candidate_questions import run_candidate_questions
from libs.global_search import run_global_search
from libs.local_search import run_local_search
from libs.pgvector import PgVectorStore
from libs.common import check_rag_complete, run_command,  javascript_code, get_rag_versions, set_venvs


from libs.search import LLMCallback, GlobalSearchLLMCallback
from libs.set_prompt import improve_query
from libs.store_vector import AI_SEARCH, LANCE, PG, get_embedding_store

from io import StringIO
from pathlib import Path
from openai import OpenAI
from theodoretools.fs import list_subdirectories
import pdfplumber
import csv
import fitz
import streamlit_authenticator as stauth
from  libs.common import is_login
import libs.config as config
from graphrag.query.structured_search.base import BaseSearch, SearchResult


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

notebook_dir = os.path.abspath("")
parent_dir = os.path.dirname(notebook_dir)
grandparent_dir = os.path.dirname(parent_dir)

sys.path.append(grandparent_dir)


async def search(rag_version: str, db:str):
    query = st.text_area(label="search",
                         label_visibility='hidden',
                         max_chars=1000,
                         placeholder="Input your query here",
                         value="")
    
    
    st.markdown("Local Search: https://microsoft.github.io/graphrag/query/local_search/")
    st.markdown("Global Search: https://microsoft.github.io/graphrag/query/global_search/")
    st.markdown("Question Generation: https://microsoft.github.io/graphrag/query/question_generation/")
    st.markdown("------------------------")

    set_venvs(rag_version)

    if st.button('Local Search', key="local_search"):
        if not query:
            st.error("Please enter a query")
            return

        check_rag_complete(rag_version)
        with st.spinner(f'Generating ...'):
            result = await run_local_search(
                rag_version=rag_version, 
                db=db, 
                query=improve_query(rag_version, query),
                callbacks=[LLMCallback()],
            )

            if "claims" in result.context_data:
                st.write(result.context_data["claims"].head())

            st.write(f"LLM calls: {result.llm_calls}. LLM tokens: {result.prompt_tokens}")
            if config.is_debug:
                if result.context_data:
                    with st.expander("Debug context_data"):
                        st.write(result.context_data)
                if result.context_text:
                    with st.expander("Debug context_text"):
                        st.text(result.context_text)

    if st.button('Global Search', key="global_search"):
        if not query:
            st.error("Please enter a query")
            return

        check_rag_complete(rag_version)
        with st.spinner(f'Generating ...'):
            result = await run_global_search(
                rag_version=rag_version, 
                db=db, 
                query=improve_query(rag_version, query),
                callbacks=[GlobalSearchLLMCallback()],
            )
            st.success(result.response)
            st.write(f"LLM calls: {result.llm_calls}. LLM tokens: {result.prompt_tokens}")

            if config.is_debug:
                if result.context_data:
                    with st.expander("Debug context_data"):
                        st.write(result.context_data)
                if result.context_text:
                    with st.expander("Debug context_text"):
                        st.text(result.context_text)

    if st.button('Candidate Questions', key="run_candidate_questions"):
        if not query:
            st.error("Please enter a query")
            return

        check_rag_complete(rag_version)

        with st.spinner(f'Generating ...'):
            result = await run_candidate_questions(
                rag_version=rag_version, 
                db=db, 
                question_history=[query],
                callbacks=[LLMCallback()],
            )
            # st.success(result.response)
            # st.write(f"LLM calls: {result.llm_calls}. LLM tokens: {result.prompt_tokens}")

def page(title: str):
    st.title(title)
    st.markdown(f"GraphRAG Kit:`{config.app_version}` GraphRAG:`{config.graphrag_version}`")
    if config.test_tip:
        st.write(config.test_tip)
    rag_versions_list = get_rag_versions()
    if len(rag_versions_list) == 0:
        st.error("No RAG versions found.")
        return
    
    st.markdown("------------------------")
    st.markdown("### Generate Test")

    options = []
    if not config.disable_pgvector:
        options.append(PG)
    if not config.disable_aisearch:
        options.append(AI_SEARCH)

    c1, c2 = st.columns([1, 1])
    with c1:
        rag_version = st.selectbox("RAG Versions", rag_versions_list)
    with c2:
        db = st.selectbox("Vector DB", options)

    asyncio.run(search(rag_version, db))



if __name__ == "__main__":
    try:
        page_title = F"GraphRAG Test for {config.app_title}"
        st.set_page_config(page_title=page_title,
                            page_icon="avatars/favicon.ico",
                            layout="wide",
                            initial_sidebar_state='expanded')
        st.image("avatars/logo.svg", width=100)

        if is_login(config.app_password):
            page(page_title)
        else:
            pass_input = st.text_input("Please input password", type="password")
            pass_btn = st.button("Summit")
            if pass_btn:
                if pass_input != config.app_password:
                    st.error("Password error")
                else:
                    st.session_state.password = config.app_password
                    st.success("Login success")
                    page(page_title)

    except Exception as e:
        logger.exception(e)
        raise e