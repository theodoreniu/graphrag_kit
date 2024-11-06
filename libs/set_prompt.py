import pandas as pd
import streamlit as st
import os
import libs.config as config


def improve_query(rag_version: str, query: str):
    prompt = get_prompt(rag_version)
    if not prompt:
        return query

    prompt = prompt.replace("{query}", query)

    # if config.is_debug:
    #     st.text(prompt)

    return prompt


def get_prompt(rag_version: str):
    prompt_txt = f"/app/index/{config.tenant_name}/{rag_version}/prompts/prompt.txt"
    if not os.path.exists(prompt_txt):
        return """-Your Role-
You are an intelligent assistant.

-User Query-
{query}
"""
    
    with open(prompt_txt, 'r') as f:
        prompt = f.read()
        return prompt

def check_prompt(content:str):
    if content.find("{query}") == -1:
        return False
    return True

def set_prompt(rag_version: str):
    prompt_txt = f"/app/index/{config.tenant_name}/{rag_version}/prompts/prompt.txt"

    prompt = get_prompt(rag_version)

    new_prompt = st.text_area("Prompt", 
                              value=prompt, 
                              height=400,
                              key=f"prompt_{rag_version}")

    if st.button("Save", key=f"save_{rag_version}"):
        if not check_prompt(new_prompt):
            st.error("Prompt must contain {query}")
            return
        with open(prompt_txt, 'w') as f:
            f.write(new_prompt)
        st.success("Prompt saved.")
