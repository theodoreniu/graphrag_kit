import logging
import shutil
import sys
import tracemalloc
import streamlit as st
import os
from dotenv import load_dotenv
from libs.save_settings import set_settings

from libs.index_preview import index_preview
from libs.common import delete_project_name, get_project_names
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


def projects_manage():
    st.session_state.project_names = get_project_names()
    
    st.markdown("----------------------------")
    if st.button("Refresh Projects", key="refresh", icon="🔄"):
        st.session_state.project_names = get_project_names()
        
    if len(st.session_state.project_names) == 0:
        return
    
    st.markdown(f"# Projects ({len(st.session_state.project_names)})")
    
    for project_name in st.session_state.project_names:
        size_mb = get_directory_size(f"/app/projects/{project_name}/output", ['.log'])

        if size_mb == 0:
            size_mb = ""
        else:
            size_mb = f"({size_mb} MB)"

        with st.expander(f"#### 📁 {project_name} {size_mb}"):
                tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                    "1 - Upload Files",
                    "2 - GraphRAG Settings",
                    "3 - Generate Data",
                    "4 - Prompt Tuning",
                    "5 - Build Index",
                    "6 - Index Preview",
                    "7 - Manage"
                    ])
                with tab1:
                    upload_file(project_name)
                with tab2:
                    set_settings(project_name)
                with tab3:
                    generate_data(project_name)
                with tab4:
                    prompt_tuning(project_name)
                with tab5:
                    build_index(project_name)
                with tab6:
                    index_preview(project_name)
                with tab7:
                    if st.button("Export to ZIP", key=f"export_zip_{project_name}", icon="📦"):
                        export_project_to_zip(project_name)
                        
                    if st.button("Delete", key=f"delete_{project_name}", icon="🗑️"):
                        delete_project_name(project_name)
                        st.session_state.project_names = get_project_names()


def export_project_to_zip(project_name: str):
    project_path = f"/app/projects/{project_name}"
    with st.spinner('Exporting ...'):
        zip_file = f"/tmp/{project_name}.zip"
        if os.path.exists(zip_file):
            os.remove(zip_file)
        shutil.make_archive(f"/tmp/{project_name}", 'zip', project_path)
        with open(zip_file, "rb") as file:
            st.download_button(
                label=f"Download {project_name}.zip",
                data=file,
                icon="💾",
                file_name=f"{project_name}.zip")
