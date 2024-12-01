import json
import re
import os
import subprocess
import streamlit as st
from theodoretools.fs import list_subdirectories
import libs.config as config
from graphrag.config.load_config import load_config
from pathlib import Path
import sys
import signal

import hashlib


def project_path(project_name: str):
    return Path("/app/projects") / project_name


def load_graphrag_config(project_name: str):
    return load_config(root_dir=project_path(project_name))


def set_venvs(project_name: str):
    os.environ['GRAPHRAG_ENTITY_EXTRACTION_PROMPT_FILE'] = str(Path("/app/projects") / project_name / "prompts" / "entity_extraction.txt")
    os.environ['GRAPHRAG_COMMUNITY_REPORT_PROMPT_FILE'] = f"/app/projects/{project_name}/prompts/community_report.txt"
    os.environ['GRAPHRAG_SUMMARIZE_DESCRIPTIONS_PROMPT_FILE'] = f"/app/projects/{project_name}/prompts/summarize_descriptions.txt"


def check_rag_complete(project_name: str):
    base_path = f"/app/projects/{project_name}"
    subdirectories = list_subdirectories(path=f"{base_path}/output")
    if len(subdirectories) == 0:
        raise Exception("Your need to build index first.")


def get_original_dir(project_name: str):
    return f"/app/projects/{project_name}/original"


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


def is_admin():
    if not os.path.exists('./config.yaml'):
        return True

    if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
        return st.session_state['username'].lower() == 'admin'
    
    return True


def get_username():
    if st.session_state['authentication_status']:
        return st.session_state['username']
    return config.app_name


def format_project_name(version: str):
    if not re.match("^[A-Za-z0-9_-]*$", version):
        raise ValueError("Name can only contain letters and numbers.")
    
    if is_admin():
        return version.lower()
    
    return f'{get_username()}_{version.lower()}'


def delete_project_name(project_name: str):
    run_command(f"rm -rf /app/projects/{project_name}")
    st.success(f"Deleted {project_name}")


def project_name_exists(project_name: str):
    project_path = f'/app/projects/{project_name}'
    return os.path.exists(project_path)


def get_project_names():
    project_name_path = '/app/projects'
    debug(f"scan to find versions in {project_name_path}")
    projects = list_subdirectories(project_name_path)
    if is_admin():
        return projects
    
    return [v for v in projects if v.startswith(get_username())]


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


def restart_component():
    st.markdown(f"[GraphRAG Kit](https://github.com/TheodoreNiu/graphrag_kit):`{config.app_version}` [GraphRAG](https://github.com/microsoft/graphrag):`{config.graphrag_version}` App started at: `{config.app_started_at}`")
    
    if config.app_tip:
        st.write(config.app_tip)
        
    with st.expander("App Server"):
        if st.button("Restart"):
            st.success("You need to refresh page later.")
            os._exit(1)
            sys.exit(1)
            os.kill(os.getpid(), signal.SIGTERM)
            st.stop()
            sys.exit()

    st.markdown("-----------------")


def generate_text_fingerprint(text, algorithm="sha256"):
    hash_object = hashlib.new(algorithm)
    hash_object.update(text.encode('utf-8'))
    return hash_object.hexdigest()


def get_cache_json_from_file(cache_key: str):
    cache_file = f"/app/cache/query_cache/{cache_key}.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            return json.load(file)
    return None


def set_cache_json_to_file(cache_key: str, data: dict):
    cache_file = f"/app/cache/query_cache/{cache_key}.json"
    cache_file_dir = os.path.dirname(cache_file)
    if not os.path.exists(cache_file_dir):
        os.makedirs(cache_file_dir, exist_ok=True)
        
    with open(cache_file, "w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
