

import asyncio
from pathlib import Path
import streamlit as st

import graphrag.api as api

import libs.config as config
from graphrag.config import load_config

async def start(base_path:str):

    (
        entity_extraction_prompt,
        entity_summarization_prompt,
        community_summarization_prompt,
    ) = await api.generate_indexing_prompts(
            config=load_config(root_dir=Path(base_path)),
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
    base_path = f"/app/projects/{rag_version}"

    if st.button('Start Tuning ', key=f"prompt_tuning_{rag_version}"):
    
        asyncio.run(start(base_path))
