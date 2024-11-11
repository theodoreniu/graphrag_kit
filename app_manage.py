import logging
import sys
import tracemalloc
import streamlit as st
import os
from dotenv import load_dotenv
from libs.save_env import set_envs
from  libs.common import is_login
import libs.config as config
from libs.create_version import create_version
from libs.versions_manage import versions_manage

tracemalloc.start()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

notebook_dir = os.path.abspath("")
parent_dir = os.path.dirname(notebook_dir)
grandparent_dir = os.path.dirname(parent_dir)

sys.path.append(grandparent_dir)


def page(title: str):
    st.title(title)
    st.markdown(f"GraphRAG Kit:`{config.app_version}` GraphRAG:`{config.graphrag_version}`")
    if config.manage_tip:
        st.write(config.manage_tip)
    # st.info(f"RAG tanant name: {config.tenant_name}")

    set_envs()

    create_version()

    versions_manage()


if __name__ == "__main__":
    try:
        page_title = "GraphRAG Manage"
        st.set_page_config(page_title=page_title,
                            page_icon="avatars/favicon.ico",
                            layout="wide",
                            initial_sidebar_state='expanded')
        st.image("avatars/logo.svg", width=100)

        if is_login():
            page(page_title)
        else:
            pass_input = st.text_input("Please input password", type="password")
            pass_btn = st.button("Summit")
            if pass_btn:
                if pass_input != config.app_password:
                    st.error("Password error")
                else:
                    st.session_state.password = config.app_password
                    st.success("Login success")
                    page(page_title)

    except Exception as e:
        logger.exception(e)
        raise e
