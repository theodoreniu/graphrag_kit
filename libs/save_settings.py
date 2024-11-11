import pandas as pd
import streamlit as st
import os
import libs.config as config
from code_editor import code_editor
from streamlit_ace import st_ace


def get_settings(rag_version: str):
    settings_file = f"/app/projects/{rag_version}/settings.yaml"
    if not os.path.exists(settings_file):
        return ""
    
    with open(settings_file, 'r') as f:
        prompt = f.read()
        return prompt


def set_settings(rag_version: str):
    settings_file = f"/app/projects/{rag_version}/settings.yaml"

    settings = get_settings(rag_version)

    # new_settings = code_editor(settings, lang="yaml", key=f"settings_{rag_version}")
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='yaml',
                   height=400,
                          key=f"settings_{rag_version}")

    if st.button("Save", key=f"save_settings_{rag_version}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")
