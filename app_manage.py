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
from libs.index_preview import index_preview
from libs.pgvector import PgVectorStore
from libs.common import debug, delete_rag_version, rag_version_exists, run_command, javascript_code, create_session_files, get_rag_versions, format_rag_version
from io import StringIO
from pathlib import Path
from openai import OpenAI
from theodoretools.url import url_to_name
from theodoretools.fs import list_subdirectories,get_directory_size
import pdfplumber
import csv
import fitz
import streamlit_authenticator as stauth
from  libs.common import is_login
import libs.config as config
from libs.prompt_tuning import prompt_tuning
from libs.set_prompt import set_prompt
from libs.upload_file import upload_file
from libs.genearate_data import genearate_data
from libs.build_index import build_index
from libs.store_vector import store_vector

tracemalloc.start()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

notebook_dir = os.path.abspath("")
parent_dir = os.path.dirname(notebook_dir)
grandparent_dir = os.path.dirname(parent_dir)

sys.path.append(grandparent_dir)


def versions_manage():
    rag_versions_list = get_rag_versions()
    if len(rag_versions_list) == 0:
        return

    st.markdown("----------------------------")
    st.markdown(f"# RAG Versions ({len(rag_versions_list)})")
    for rag_version in rag_versions_list:
        size_mb = get_directory_size(f"/app/index/{config.tenant_name}/{rag_version}/output", ['.log'])
        if size_mb == 0:
            size_mb = ""
        else:
            size_mb = f"({size_mb} MB)"
        show_expander = st.session_state.get(f"show_expander_{rag_version}", True)
        if show_expander:
            with st.expander(f"#### {rag_version} {size_mb}"):
                tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                    "1-Upload Files", 
                    "2-Generate Data", 
                    "3-Build GraphRAG", 
                    "4-Index Preview", 
                    "5-Store Vectors", 
                    "6-Prompt Tuning", 
                    "7-Set Prompt", 
                    "8-Delete"
                    ])
                with tab1:
                    upload_file(rag_version)
                with tab2:
                    genearate_data(rag_version)
                with tab3:
                    build_index(rag_version)
                with tab4:
                    index_preview(rag_version)
                with tab5:
                    store_vector(rag_version)
                with tab6:
                    prompt_tuning(rag_version)
                with tab7:
                    set_prompt(rag_version)
                with tab8:
                    if st.button("Delete", key=f"delete_{rag_version}"):
                        delete_rag_version(rag_version)
                        show_expander = False
                        st.session_state[f"show_expander_{rag_version}"] = False
                    

def page(title: str):
    st.title(title)
    st.write(f"GraphRAG Kit ({config.app_version})")
    st.write(os.getenv('TEST_TIP'))
    st.info(f"RAG tanant name: {config.tenant_name}")

    st.markdown("----------------------------")
    st.markdown("# Build New Version")
    today_hour=time.strftime("%Y%m%d%H", time.localtime())

    new_rag_version=st.text_input("Please input new rag version", 
                                    value=today_hour,
                                    max_chars=14,
                                    )
    btn = st.button("Confirm", key="confirm")
    if btn:
        formated_rag_version = format_rag_version(new_rag_version)
        st.info(f"New rag version formated is: {formated_rag_version}")
        if rag_version_exists(formated_rag_version):
            st.error(f"RAG version {formated_rag_version} already exists.")
        else:
            create_session_files(new_rag_version)
            st.success(f"Created Version {formated_rag_version}")

    versions_manage()


if __name__ == "__main__":
    try:
        page_title = F"GraphRAG Manage for {config.app_title}"
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
