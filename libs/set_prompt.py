import pandas as pd
import streamlit as st
import os
import libs.config as config


def improve_query(project_name: str, query: str):
    prompt = get_prompt(project_name)
    if not prompt:
        return query

    prompt = prompt.replace("{query}", query)

    # if config.is_debug:
    #     st.text(prompt)

    return prompt


def get_prompt(project_name: str):
    prompt_txt = f"/app/projects/{project_name}/prompts/prompt.txt"
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

def set_prompt(project_name: str):
    prompt_txt = f"/app/projects/{project_name}/prompts/prompt.txt"

    prompt = get_prompt(project_name)

    new_prompt = st.text_area("Prompt", 
                              value=prompt, 
                              height=400,
                              key=f"prompt_{project_name}")

    if st.button("Save", key=f"save_{project_name}"):
        if not check_prompt(new_prompt):
            st.error("Prompt must contain {query}")
            return
        with open(prompt_txt, 'w') as f:
            f.write(new_prompt)
        st.success("Prompt saved.")
