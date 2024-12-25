
import json
import os
import streamlit as st
from dotenv import load_dotenv
import io
from libs.find_sources import get_query_sources
from libs.render_context import get_real_response, render_context_data_drift, render_context_data_global, render_context_data_local, render_response
from libs.save_settings import set_settings
from libs.common import get_project_names, project_path, restart_component
import pandas as pd
import libs.config as config
from graphrag.cli.query import run_local_search, run_global_search, run_drift_search
from openai import AzureOpenAI
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from libs.render_excel import render_excel_file

load_dotenv()

client = AzureOpenAI(
    api_version=config.search_azure_api_version,
    azure_endpoint=config.search_azure_api_base,
    azure_deployment=config.search_azure_chat_deployment_name,
    api_key=config.search_azure_api_key,
)


def response_score(query:str, standard_answer:str, generated_answer:str):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "你是一个答案评分助手，我给你问题、标准答案和AI生成的答案，请给你AI生成的答案评分，满分 100 分，最小分0分，分数需要是整数，你只需要给出分数即可。如果AI生成的答案与标准答案含义相同或者能包含标准答案的含义，则满分，否则分数递减。",
            },
            {
                "role": "user",
                "content": f"问题：{query} \n\n标准答案：{standard_answer} \n\nAI生成的答案：{generated_answer} \n\n",
            }
        ],
        model=config.search_azure_chat_model_id,
    )
    ai_txt = completion.choices[0].message.content
    return ai_txt


def page():
    restart_component()

    project_names = get_project_names()
    if len(project_names) == 0:
        st.error("No projects found, please go to manage page to create a project.")
        return

    st.markdown("### Select Project to Test")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        project_name = st.selectbox("Project", project_names)
    with c2:
        community_level = st.text_input("community_level", value=2)
    with c3:
        response_type = st.selectbox("Response Type", ["Single Paragraph", "Multiple Paragraphs"])
    
    st.session_state['project_name'] = project_name
    st.session_state['community_level'] = community_level
    st.session_state['response_type'] = response_type
    
    # project settings review
    st.write(f"You selected: `{project_name}`")
    with st.expander("🔧 Project Settings Review"):
        set_settings(project_name, read_only=True)
    
    st.text("\n")
    st.text("\n")
    st.text("\n")
    st.markdown("### Single Test")
    
    # query input
    query = st.text_area(label="search",
                         label_visibility='hidden',
                         max_chars=1000,
                         placeholder="Input your query here",
                         value="")
    
    tab1, tab2, tab3 = st.tabs(["🛢️ Local Search", "🌍 Global Search", "🌀 Drift Search"])
    
    with tab1:
        st.markdown("About Local Search: https://microsoft.github.io/graphrag/query/local_search/")
        if st.button('🔎 Local Search', key="local_search"):
            if not query:
                st.error("Please enter a query")
            else:
                with st.spinner('Generating ...'):
                    (response, context_data) = run_local_search(
                        root_dir=project_path(project_name),
                        query=query,
                        community_level=int(community_level),
                        response_type=response_type,
                        streaming=False,
                        config_filepath=None,
                        data_dir=None,
                    )
                    render_response(response)
                    with st.expander("📄 Sources"):
                        sources = get_query_sources(project_name, context_data)
                        for source in sources:
                            screenshot_sas_url = source['screenshot_sas_url']
                            if screenshot_sas_url:
                                st.image(screenshot_sas_url, width=500)
                            st.write(source)
                    render_context_data_local(context_data)
    
    with tab2:
        st.markdown("About Global Search: https://microsoft.github.io/graphrag/query/global_search/")
        dynamic_community_selection = st.checkbox("Dynamic Community Selection", value=False)
        if st.button('🔎 Global Search', key="global_search"):
            if not query:
                st.error("Please enter a query")
            else:
                with st.spinner('Generating ...'):
                    (response, context_data) = run_global_search(
                        root_dir=project_path(project_name),
                        query=query,
                        community_level=int(community_level),
                        response_type=response_type,
                        streaming=False,
                        config_filepath=None,
                        data_dir=None,
                        dynamic_community_selection=dynamic_community_selection
                    )
                    render_response(response)
                    render_context_data_global(context_data)
    
    with tab3:
        st.markdown("About DRIFT Search: https://microsoft.github.io/graphrag/query/drift_search/")
        if st.button('🔎 Drift Search', key="run_drift_search"):
            if not query:
                st.error("Please enter a query")
                return
            else:
                with st.spinner('Generating ...'):
                    (response, context_data) = run_drift_search(
                        root_dir=project_path(project_name),
                        query=query,
                        community_level=int(community_level),
                        streaming=False,
                        config_filepath=None,
                        data_dir=None,
                    )
                    render_response(response)
                    render_context_data_drift(context_data)
        
    st.markdown("-----------------")
    st.markdown("## Batch Test")
    
    st.markdown("Put the question in a field called `query`, When all queries are executed, you can download the file.")
    st.markdown("If a column named `answer` is used as the standard answer, automated testing calculates answer score.")
    st.markdown("Currently, only `Local Search` is supported.")
    st.markdown("Query `cache` enabled, the same query will not be executed multiple times.")
    
    # download test set excel file
    st.markdown("-----------------")
    st.download_button(
        label="Download Test File",
        data=open('./template/test_set.xlsx', 'rb').read(),
        file_name='test_set.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        icon="💾",
    )
    st.markdown("-----------------")
    
    enable_print_context = st.checkbox("Print every item context", value=False)
    
    uploaded_file = st.file_uploader(
        label="upload",
        type=['xlsx'],
        accept_multiple_files=False,
        label_visibility="hidden",
        key=f"file_uploader_batch_test",
    )
    
    if uploaded_file is not None:
        output = test_file(uploaded_file, project_name, community_level, response_type, enable_print_context)
        st.markdown("-------------------------------------------")
        st.download_button(
            label="Download Test Results",
            data=output.getvalue(),
            file_name=uploaded_file.name.replace(".xlsx", "_result.xlsx"),
            icon="💾",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
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


@st.cache_data
def test_file(uploaded_file, project_name, community_level, response_type, enable_print_context):
    excel_data = pd.ExcelFile(uploaded_file)
    modified_sheets = {}

    for sheet_name in excel_data.sheet_names:
        st.write(f"### Sheet: {sheet_name}")
        
        sheet_df = excel_data.parse(sheet_name)
        row_count = len(sheet_df)
        
        modified_df = sheet_df.copy()
        
        for index, row in sheet_df.iterrows():
            if 'query' not in row:
                raise Exception("query must be in every row")

            index_name = f"{index+1}/{row_count}"
            st.markdown(f"## {index_name}")
            with st.spinner(f'Generating ...'):
                
                query = row['query']

                (response, context_data) = run_local_search(
                    root_dir=project_path(project_name),
                    query=query,
                    community_level=int(community_level),
                    response_type=response_type,
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )
                
                st.info(f"Query: {row['query']}")
                
                if 'answer' in row:
                    st.warning(f"Answer: {row['answer']}")

                modified_df.at[index, "GraphRAG"] = response
                result = get_real_response(response)
                st.success(f"GraphRAG (chars {len(result)}): {response}")
                # modified_df.at[index, f"{project_name}_response_count"] = len(result)
                # modified_df.at[index, f"{project_name}_context_data"] = json.dumps(context_data, ensure_ascii=False, indent=4)
                # modified_df.at[index, f"{project_name}_response_type"] = response_type
                if enable_print_context:
                    render_context_data_local(context_data)
        
        modified_sheets[sheet_name] = modified_df
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in modified_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)   
    
    output = render_excel_file(output)
    return output


if __name__ == "__main__":
    page_title = "GraphRAG Test"
    st.set_page_config(
        page_title=page_title,
                        page_icon="avatars/favicon.ico",
                        layout="wide",
                        initial_sidebar_state='expanded')
    st.image("avatars/logo.svg", width=100)
    st.title(page_title)
    
    if not os.path.exists('./config.yaml'):
        page()
    else:
        with open('./config.yaml') as file:
            yaml_config = yaml.load(file, Loader=SafeLoader)
            authenticator = stauth.Authenticate(
                yaml_config['credentials'],
                yaml_config['cookie']['name'],
                yaml_config['cookie']['key'],
                yaml_config['cookie']['expiry_days'],
            )
            
            authenticator.login()

            if st.session_state['authentication_status']:
                st.write(f'Welcome `{st.session_state["name"]}`')
                authenticator.logout()
                st.markdown("-----------------")
                page()
            elif st.session_state['authentication_status'] is False:
                st.error('Username/password is incorrect')
            elif st.session_state['authentication_status'] is None:
                st.warning('Please enter your username and password')

