

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



def build_index(rag_version: str):
    base_path = f"/app/index/{config.tenant_name}/{rag_version}"
    if st.button('Start Build', key=f"build_index_{rag_version}"):
        with st.chat_message("user", avatar="avatars/ms.svg"):
            
            # if not os.path.exists(base_path):
            #     st.error("Please upload a file first")
            #     return

            # if os.path.exists(f"{base_path}/output") and len(list_subdirectories(path=f"{base_path}/output")) > 0:
            #     st.error("You have already built the index")
            #     return
            # else:

            with st.spinner(f'Running the index pipeline for {rag_version} ...'):
                run_command(f"python -m graphrag.index --verbose --root {base_path}")

            subdirectories = list_subdirectories(path=f"{base_path}/output")
            if len(subdirectories) == 0:
                raise Exception("No output by graphrag.index, please check log.")

            create_final_entities = f"{base_path}/output/artifacts/create_final_entities.parquet"
            if not os.path.exists(create_final_entities):
                raise Exception(f"No {create_final_entities} by graphrag.index, please check log.")

            df = pd.read_parquet(create_final_entities)
            df = pd.read_parquet(f"{base_path}/output/artifacts/create_final_relationships.parquet")

            index_log_file = f"{base_path}/output/reports/indexing-engine.log"
            lines = []
            with open(index_log_file, 'r') as f:
                log_content = f.read()
                for line in log_content.split('\n'):
                    if line.strip():
                        if "output_tokens" in line:
                            line = line.replace("graphrag.llm.base.rate_limiting_llm INFO perf - ", "")
                            lines.append(line)
            st.success("Indexing completed.")
            st.write(f"LLM Logs {len(lines)} items")
            st.write(lines)

    if st.button("Clear index files", key=f"delete_all_index_files_{rag_version}"):
        run_command(f"rm -rf /app/index/{config.tenant_name}/{rag_version}/output/*")
        time.sleep(3)
        st.success("All files deleted.")
