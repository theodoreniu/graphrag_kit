import pandas as pd
import streamlit as st
import os
import libs.config as config
from code_editor import code_editor
from streamlit_ace import st_ace


def get_setting_file(file_path: str):
    if not os.path.exists(file_path):
        return ""
    
    with open(file_path, 'r') as f:
        prompt = f.read()
        return prompt


def settings(project_name: str):
    settings_file = f"/app/projects/{project_name}/settings.yaml"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='yaml',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"settings_{project_name}")
    if st.button("Save", key=f"save_settings_{project_name}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def claim_extraction(project_name: str):
    settings_file = f"/app/projects/{project_name}/prompts/claim_extraction.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"claim_extraction_{project_name}")
    if st.button("Save", key=f"save_claim_extraction_{project_name}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def community_report(project_name: str):
    settings_file = f"/app/projects/{project_name}/prompts/community_report.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"community_report_{project_name}")
    if st.button("Save", key=f"save_community_report_{project_name}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def entity_extraction(project_name: str):
    settings_file = f"/app/projects/{project_name}/prompts/entity_extraction.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"entity_extraction_{project_name}")
    if st.button("Save", key=f"save_entity_extraction_{project_name}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def summarize_descriptions(project_name: str):
    settings_file = f"/app/projects/{project_name}/prompts/summarize_descriptions.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="tomorrow_night",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"summarize_descriptions_{project_name}")
    if st.button("Save", key=f"save_summarize_descriptions_{project_name}"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def set_settings(project_name: str):

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "settings.yaml",
        "claim_extraction.txt",
        "community_report.txt",
        "entity_extraction.txt",
        "summarize_descriptions.txt",
        ])
    with tab1:
        settings(project_name)
    with tab2:
        claim_extraction(project_name)
    with tab3:
        community_report(project_name)
    with tab4:
        entity_extraction(project_name)
    with tab5:
        summarize_descriptions(project_name)
