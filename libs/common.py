import io
import re
import os
import subprocess
import streamlit as st
from theodoretools.fs import list_subdirectories
import qrcode
import libs.config as config

def set_venvs(rag_version: str):
    os.environ['GRAPHRAG_ENTITY_EXTRACTION_PROMPT_FILE'] = f"/app/index/{config.tenant_name}/{rag_version}/prompts/entity_extraction.txt"
    os.environ['GRAPHRAG_COMMUNITY_REPORT_PROMPT_FILE'] = f"/app/index/{config.tenant_name}/{rag_version}/prompts/community_report.txt"
    os.environ['GRAPHRAG_SUMMARIZE_DESCRIPTIONS_PROMPT_FILE'] = f"/app/index/{config.tenant_name}/{rag_version}/prompts/summarize_descriptions.txt"

def check_rag_complete(rag_version: str):
    base_path = f"/app/index/{config.tenant_name}/{rag_version}"
    subdirectories = list_subdirectories(path=f"{base_path}/output")
    if len(subdirectories) == 0:
        raise Exception("Your need to build index first.")

def get_original_dir(rag_version: str):
    return f"/app/index/{config.tenant_name}/{rag_version}/original"

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
    new_version = re.sub('[^a-zA-Z0-9]', '', version)
    return new_version.lower()

def delete_rag_version(version: str):
    run_command(f"rm -rf /app/index/{config.tenant_name}/{version}")
    st.success(f"Deleted {version}")

def rag_version_exists(version: str):
    version_path = f'/app/index/{config.tenant_name}/{version}'
    return os.path.exists(version_path)

def get_rag_versions():
    varsion_path = f'/app/index/{config.tenant_name}'
    debug(f"scan to find versions in {varsion_path}")
    versions = list_subdirectories(varsion_path)
    # versions = [v for v in versions if v.startswith(config.tenant_name)]
    return versions

def is_login(password: str):
    if config.is_debug:
        return True
    if 'password' not in st.session_state:
        return False
    if st.session_state.password != password:
        return False
    return True

def create_session_files(rag_version: str):
    run_command(f"mkdir -p /app/index/{config.tenant_name}/{rag_version}/input")
    run_command(f"mkdir -p /app/index/{config.tenant_name}/{rag_version}/original")
    run_command(f"cp -r ./ragtest/* /app/index/{config.tenant_name}/{rag_version}/")


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


def run_command(command: str, output: bool = False):

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


