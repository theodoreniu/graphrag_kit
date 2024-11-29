import streamlit as st
import os
from libs.set_prompt import check_prompt
from streamlit_ace import st_ace
import libs.config as config

def get_setting_file(file_path: str, default_prompt: str=""):
    if not os.path.exists(file_path):
        return default_prompt
    
    with open(file_path, 'r') as f:
        prompt = f.read()
        return prompt


def settings(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/settings.yaml"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='yaml',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"settings_{project_name}")
    
    if read_only == False and st.button("Save", key=f"save_settings_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
            st.success("Settings saved.")


def claim_extraction(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/claim_extraction.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"claim_extraction_{project_name}")
    if read_only == False and st.button("Save", key=f"save_claim_extraction_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def community_report(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/community_report.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"community_report_{project_name}")
    if read_only == False and st.button("Save", key=f"save_community_report_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def entity_extraction(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/entity_extraction.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"entity_extraction_{project_name}")
    if read_only == False and st.button("Save", key=f"save_entity_extraction_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def summarize_descriptions(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/summarize_descriptions.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"summarize_descriptions_{project_name}")
    if read_only == False and st.button("Save", key=f"save_summarize_descriptions_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")

def pdf_gpt_vision_prompt(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/pdf_gpt_vision_prompt.txt"

    settings = get_setting_file(settings_file, config.pdf_gpt_vision_prompt)
        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"generate_data_{project_name}")
    if read_only == False and st.button("Save", key=f"save_generate_data_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")

def pdf_gpt_vision_prompt_by_text(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/pdf_gpt_vision_prompt_by_text.txt"

    settings = get_setting_file(settings_file, config.pdf_gpt_vision_prompt_by_text)
        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"pdf_gpt_vision_prompt_by_text_{project_name}")
    if read_only == False and st.button("Save", key=f"save_pdf_gpt_vision_prompt_by_text_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")


def pdf_gpt_vision_prompt_by_image(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/pdf_gpt_vision_prompt_by_image.txt"

    settings = get_setting_file(settings_file, config.pdf_gpt_vision_prompt_by_image)
        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   readonly=read_only,
                   show_print_margin=True,
                   key=f"pdf_gpt_vision_prompt_by_image_{project_name}")
    if read_only == False and st.button("Save", key=f"save_pdf_gpt_vision_prompt_by_image_{project_name}", icon="💾"):
        with open(settings_file, 'w') as f:
            f.write(new_settings)
        st.success("Settings saved.")

def project_prompt_setting(project_name: str, read_only: bool=False):
    settings_file = f"/app/projects/{project_name}/prompts/prompt.txt"

    settings = get_setting_file(settings_file)        
    new_settings = st_ace(settings,
                   theme="chaos",
                   language='plain_text',
                   height=400,
                   auto_update=True,
                   wrap=True,
                   show_gutter=True,
                   show_print_margin=True,
                   key=f"project_prompt_{project_name}")
    if st.button("Save", key=f"save_project_prompt_{project_name}", icon="💾"):
        if not check_prompt(new_settings):
            st.error("Prompt must contain {query}")
            return
        with open(settings_file, 'w') as f:
            f.write(new_settings)
            st.success("Settings saved.")


def set_settings(project_name: str, read_only=False):
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "📄 settings.yaml",
        "📁 Input",
        "📄 claim_extraction.txt",
        "📄 community_report.txt",
        "📄 entity_extraction.txt",
        "📄 summarize_descriptions.txt",
        "📄 prompt.txt",
        "📄 PDF Vision",
        "📄 PDF Vision by Text",
        "📄 PDF Vision by Image",
        ])
    with tab1:
        settings(project_name, read_only=read_only)
    with tab2:
        input_files(project_name)
    with tab3:
        claim_extraction(project_name, read_only=read_only)
    with tab4:
        community_report(project_name, read_only=read_only)
    with tab5:
        entity_extraction(project_name, read_only=read_only)
    with tab6:
        summarize_descriptions(project_name, read_only=read_only)
    with tab7:
        project_prompt_setting(project_name, read_only=read_only)
    with tab8:
        pdf_gpt_vision_prompt(project_name, read_only=read_only)
    with tab9:
        pdf_gpt_vision_prompt_by_text(project_name, read_only=read_only)
    with tab10:
        pdf_gpt_vision_prompt_by_image(project_name, read_only=read_only)

def input_files(project_name: str):
    files_path = f"/app/projects/{project_name}/input"
    if not os.path.exists(files_path):
        os.makedirs(files_path)
    files = os.listdir(files_path)
    st.markdown(f"Items: `{len(files)}`")
    st.write(files)
