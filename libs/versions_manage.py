import logging
import shutil
import sys
import tracemalloc
import streamlit as st
import os
from dotenv import load_dotenv
from libs.save_settings import set_settings

from libs.index_preview import index_preview
from libs.common import delete_rag_version, get_rag_versions
from theodoretools.fs import get_directory_size
from libs.prompt_tuning import prompt_tuning
from libs.upload_file import upload_file
from libs.generate_data import generate_data
from libs.build_index import build_index

tracemalloc.start()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

notebook_dir = os.path.abspath("")
parent_dir = os.path.dirname(notebook_dir)
grandparent_dir = os.path.dirname(parent_dir)

sys.path.append(grandparent_dir)


def versions_manage():
    st.session_state.rag_versions_list = get_rag_versions()
    
    st.markdown("----------------------------")
    if st.button("Refresh Projects", key="refresh", icon="🔄"):
        st.session_state.rag_versions_list = get_rag_versions()
        
    if len(st.session_state.rag_versions_list) == 0:
        return
    
    st.markdown(f"# Projects ({len(st.session_state.rag_versions_list)})")
    
    for rag_version in st.session_state.rag_versions_list:
        size_mb = get_directory_size(f"/app/projects/{rag_version}/output", ['.log'])

        if size_mb == 0:
            size_mb = ""
        else:
            size_mb = f"({size_mb} MB)"

        with st.expander(f"#### 📁 {rag_version} {size_mb}"):
                tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    "1-Upload Files",
                    "2-Generate Data",
                    "3-GraphRAG Settings",
                    "4-Build GraphRAG",
                    "5-Index Preview",
                    # "6-Store Vectors", 
                    "6-Prompt Tuning",
                    "7-Manage"
                    ])
                with tab1:
                    upload_file(rag_version)
                with tab2:
                    generate_data(rag_version)
                with tab3:
                    set_settings(rag_version)
                with tab4:
                    build_index(rag_version)
                with tab5:
                    index_preview(rag_version)
                with tab6:
                    prompt_tuning(rag_version)
                with tab7:
                    if st.button("Export to ZIP", key=f"export_zip_{rag_version}", icon="📦"):
                        export_project_to_zip(rag_version)
                        
                    if st.button("Delete", key=f"delete_{rag_version}", icon="🗑️"):
                        delete_rag_version(rag_version)
                        st.session_state.rag_versions_list = get_rag_versions()


def export_project_to_zip(rag_version):
    project_path = f"/app/projects/{rag_version}"
    with st.spinner('Exporting ...'):
        zip_file = f"/tmp/{rag_version}.zip"
        if os.path.exists(zip_file):
            os.remove(zip_file)
        shutil.make_archive(f"/tmp/{rag_version}", 'zip', project_path)
        with open(zip_file, "rb") as file:
            st.download_button(
                label=f"Download {rag_version}.zip",
                data=file,
                icon="💾",
                file_name=f"{rag_version}.zip")
