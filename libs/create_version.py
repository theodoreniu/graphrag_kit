import io
import time
from pathlib import Path
import streamlit as st
import os
from dotenv import load_dotenv
from libs.common import format_rag_version, get_rag_versions, run_command
import libs.config as config
from contextlib import redirect_stdout
import asyncio
from graphrag.cli.initialize import initialize_project_at

load_dotenv()


def initialize_project(path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    output = io.StringIO()

    try:
        with redirect_stdout(output):
            initialize_project_at(path)
        output_value = output.getvalue()
        st.success(output_value)
    finally:
        loop.close()


def overwrite_settings_yaml(root, new_rag_version):
    settings_yaml = f"{root}/settings.yaml"
    template_settings_yaml = f"/app/template/setting.yaml"
    container_name = f"{config.app_name}_{new_rag_version}"
    with open(template_settings_yaml, "r") as t:
        with open(settings_yaml, "w") as f:
            new_settings_yaml = t.read().replace("container_name: default", f"container_name: {container_name}")
            f.write(new_settings_yaml)


def create_version():
    rag_versions_list = get_rag_versions()
    st.markdown("# New Project")
    today_hour = time.strftime("%Y%m%d%H", time.localtime())
    new_project_value = "Just New Project"
    c1, c2 = st.columns(2)
    with c1:
        new_rag_version = st.text_input("Please input name",
                                        value=today_hour,
                                        max_chars=30,
                                    )
    with c2:
        rag_versions_list.insert(0, new_project_value)
        copy_from_project_name = st.selectbox("Copy from", rag_versions_list, key="create_from_project_name")
        
    btn = st.button("Confirm", key="confirm")
    if btn:
        formatted_rag_version = format_rag_version(new_rag_version)
        
        if check_project_exists(formatted_rag_version):
            st.error(f"Project {formatted_rag_version} already exists.")
            return
        
        root = os.path.join("/app", "projects", formatted_rag_version)
        
        try:
            if copy_from_project_name == new_project_value:
                initialize_project(path=root)
                overwrite_settings_yaml(root, formatted_rag_version)
            else:
                copy_project(copy_from_project_name, formatted_rag_version)
        except Exception as e:
            st.error(str(e))


def check_project_exists(formatted_rag_version: str):
    return os.path.exists(f"/app/projects/{formatted_rag_version}")


def copy_project(copy_from_project_name: str, formatted_rag_version: str):
    run_command(f"cp -r '/app/projects/{copy_from_project_name}' '/app/projects/{formatted_rag_version}'")
    st.success(f"Project {copy_from_project_name} copied to {formatted_rag_version}")
    time.sleep(3)
