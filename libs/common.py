import re
import os
import subprocess
import streamlit as st
from theodoretools.fs import list_subdirectories
import libs.config as config
from graphrag.config import (
    load_config,
)
from pathlib import Path


def project_path(project_name: str):
    return Path("/app/projects") / project_name


def load_graphrag_config(project_name: str):
    return load_config(root_dir=project_path(project_name))


def set_venvs(rag_version: str):
    os.environ['GRAPHRAG_ENTITY_EXTRACTION_PROMPT_FILE'] = str(Path("/app/projects") / rag_version / "prompts" / "entity_extraction.txt")
    os.environ['GRAPHRAG_COMMUNITY_REPORT_PROMPT_FILE'] = f"/app/projects/{rag_version}/prompts/community_report.txt"
    os.environ['GRAPHRAG_SUMMARIZE_DESCRIPTIONS_PROMPT_FILE'] = f"/app/projects/{rag_version}/prompts/summarize_descriptions.txt"


def check_rag_complete(rag_version: str):
    base_path = f"/app/projects/{rag_version}"
    subdirectories = list_subdirectories(path=f"{base_path}/output")
    if len(subdirectories) == 0:
        raise Exception("Your need to build index first.")


def get_original_dir(rag_version: str):
    return f"/app/projects/{rag_version}/original"


def list_files_and_sizes(directory: str):
    file_list = []
    for root, dirs, files in os.walk(f"{directory}/"):
        for file in files:
            file_path = os.path.join(root, file)
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            file_list.append(f"{file} ({file_size_mb:.4f}MB)")
    return file_list


def debug(data:any, title:str=""):
    return
    if config.is_debug:
        if title:
            st.warning(title)
        st.warning(data)


def format_rag_version(version: str):
    if not re.match("^[A-Za-z0-9]*$", version):
        raise ValueError("输入版本只能包含英文字母和数字，不允许其他符号。")
    return f'{config.app_name}_{version.lower()}'


def delete_rag_version(version: str):
    run_command(f"rm -rf /app/projects/{version}")
    st.success(f"Deleted {version}")


def rag_version_exists(version: str):
    version_path = f'/app/projects/{version}'
    return os.path.exists(version_path)


def get_rag_versions():
    version_path = '/app/projects'
    debug(f"scan to find versions in {version_path}")
    versions = list_subdirectories(version_path)
    return [v for v in versions if v.startswith(config.app_name)]


def is_login():
    if not config.app_password:
        return True
    if 'password' not in st.session_state:
        return False
    if st.session_state.password != config.app_password:
        return False
    return True


def javascript_code():
    baidu_js = """
<script>
var _hmt = _hmt || [];
(function() {
var hm = document.createElement("script");
hm.src = "https://hm.baidu.com/hm.js?3ecc8ff27ffb0aac0dc2e6a27d726ff9";
var s = document.getElementsByTagName("script")[0];
s.parentNode.insertBefore(hm, s);
})();
</script>
"""
    st.components.v1.html(baidu_js, height=0, width=0)


def run_command(command: str, output: bool=False):

    debug(f"run command: {command}")

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    while True:
        stdout = process.stdout.readline()
        stderr = process.stderr.readline()

        if output and stderr:
            st.error(stderr)

        if stdout == '' and process.poll() is not None:
            break
        if stdout:
            s = stdout.strip()
            if output:
                st.write(s)
            elif s.startswith('🚀'):
                st.write(s)

    rc = process.poll()
    return rc

