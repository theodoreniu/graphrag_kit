

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
from graphrag.config.models.graph_rag_config import GraphRagConfig
from libs.generate_indexing_prompts import generate_indexing_prompts
from libs.pgvector import PgVectorStore
from libs.common import delete_rag_version, rag_version_exists, run_command, javascript_code

from theodoretools.url import url_to_name
from theodoretools.fs import list_subdirectories
import pdfplumber
import csv
import fitz
import streamlit_authenticator as stauth
from  libs.common import is_login
import libs.config as config
import graphrag
import subprocess
from graphrag.config import load_config

async def start(base_path:str):
    graph_config = load_config(base_path, f"{base_path}/settings.yaml")
    (
        entity_extraction_prompt,
        entity_summarization_prompt,
        community_summarization_prompt,
    ) = await generate_indexing_prompts(
            config=graph_config,
            root=base_path,
        )

    st.markdown("## entity_extraction_prompt")
    st.text(entity_extraction_prompt)

    st.markdown("## entity_summarization_prompt")
    st.text(entity_summarization_prompt)

    st.markdown("## community_summarization_prompt")
    st.text(community_summarization_prompt)

    entity_extraction_prompt_path = f"{base_path}/prompts/entity_extraction.txt"
    entity_summarization_prompt_path = f"{base_path}/prompts/summarize_descriptions.txt"
    community_summarization_prompt_path = f"{base_path}/prompts/community_report.txt"

    with open(entity_extraction_prompt_path, "wb") as file:
        file.write(entity_extraction_prompt.encode(encoding="utf-8", errors="strict"))
    with open(entity_summarization_prompt_path, "wb") as file:
        file.write(entity_summarization_prompt.encode(encoding="utf-8", errors="strict"))
    with open(community_summarization_prompt_path, "wb") as file:
        file.write(community_summarization_prompt.encode(encoding="utf-8", errors="strict"))

def prompt_tuning(rag_version: str):
    base_path = f"/app/index/{config.tenant_name}/{rag_version}"

    if st.button('Start Tuning ', key=f"prompt_tuning_{rag_version}"):
    
        asyncio.run(start(base_path))
