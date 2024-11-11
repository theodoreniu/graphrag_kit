
import streamlit as st
from dotenv import load_dotenv

from libs.common import get_rag_versions, project_path
from libs.set_prompt import improve_query
from libs.store_vector import AI_SEARCH, PG

from  libs.common import is_login
import libs.config as config
from graphrag.cli.query import run_local_search, run_global_search, run_drift_search

load_dotenv()


def page(title: str):
    st.title(title)
    st.markdown(f"GraphRAG Kit:`{config.app_version}` GraphRAG:`{config.graphrag_version}`")
    if config.test_tip:
        st.write(config.test_tip)
    rag_versions_list = get_rag_versions()
    if len(rag_versions_list) == 0:
        st.error("No projects found.")
        return
    
    st.markdown("------------------------")
    st.markdown("### Generate Test")

    options = []
    if not config.disable_pgvector:
        options.append(PG)
    if not config.disable_aisearch:
        options.append(AI_SEARCH)

    c1, c2 = st.columns([1, 1])
    with c1:
        project_name = st.selectbox("Projects", rag_versions_list)
    with c2:
        community_level = st.text_input("community_level", value=2)

    query = st.text_area(label="search",
                         label_visibility='hidden',
                         max_chars=1000,
                         placeholder="Input your query here",
                         value="")
    
    st.markdown("Local Search: https://microsoft.github.io/graphrag/query/local_search/")
    st.markdown("Global Search: https://microsoft.github.io/graphrag/query/global_search/")
    st.markdown("DRIFT Search: https://microsoft.github.io/graphrag/query/drift_search/")
    st.markdown("------------------------")
            
    if st.button('Local Search', key="local_search"):
        if not query:
            st.error("Please enter a query")
        else:
            with st.spinner('Generating ...'):
                (response, context_data) = run_local_search(
                    root_dir=project_path(project_name),
                    query=improve_query(project_name, query),
                    community_level=int(community_level),
                    response_type="Multiple Paragraphs",
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )
                st.write(response)
                with st.expander("Context"):
                    st.write(context_data)

    if st.button('Global Search', key="global_search"):
        if not query:
            st.error("Please enter a query")
        else:
            with st.spinner('Generating ...'):
                (response, context_data) = run_global_search(
                    root_dir=project_path(project_name),
                    query=improve_query(project_name, query),
                    community_level=int(community_level),
                    response_type="Multiple Paragraphs",
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )
                st.write(response)
                with st.expander("Context"):
                    st.write(context_data)

    if st.button('Drift Search', key="run_drift_search"):
        if not query:
            st.error("Please enter a query")
            return
        else:
            with st.spinner('Generating ...'):
                (response, context_data) = run_drift_search(
                    root_dir=project_path(project_name),
                    query=improve_query(project_name, query),
                    community_level=int(community_level),
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )
                st.write(response)
                with st.expander("Context"):
                    st.write(context_data)

    # if st.button('Candidate Questions', key="run_candidate_questions"):
    #     if not query:
    #         st.error("Please enter a query")
    #     else:
    #         with st.spinner('Generating ...'):
    #             (response, context_data) = run_candidate_questions(
    #                 rag_version=project_name,
    #                 db=db,
    #                 question_history=[query],
    #                 callbacks=[LLMCallback()],
    #             )
    #             st.success(result.response)


if __name__ == "__main__":

        page_title = "GraphRAG Test"
        st.set_page_config(
            page_title=page_title,
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
