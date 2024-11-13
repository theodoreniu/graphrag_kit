
import streamlit as st
from dotenv import load_dotenv
import io
from libs.common import get_rag_versions, project_path, restart_component
from libs.set_prompt import improve_query
from libs.store_vector import AI_SEARCH, PG
import pandas as pd
from  libs.common import is_login
import libs.config as config
from graphrag.cli.query import run_local_search, run_global_search, run_drift_search
from openai import AzureOpenAI

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


def page(title: str):
    st.title(title)
    st.markdown(f"GraphRAG Kit:`{config.app_version}` GraphRAG:`{config.graphrag_version}`")
    if config.test_tip:
        st.write(config.test_tip)
        
    restart_component()
    
    rag_versions_list = get_rag_versions()
    if len(rag_versions_list) == 0:
        st.error("No projects found.")
        return

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

    st.markdown("-----------------")
    st.markdown("## Batch Test")
    
    st.markdown("Put the question in a field called `query`, When all queries are executed, you can download the file.")
    st.markdown("If a column named `answer` is used as the standard answer, automated testing calculates answer score.")
    st.markdown("Currently, only `Local Search` is supported.")
    
    uploaded_file = st.file_uploader(
        label="upload",
        type=['xlsx'],
        accept_multiple_files=False,
        label_visibility="hidden",
        key=f"file_uploader_batch_test",
    )
    
    if uploaded_file is not None:
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
                    
                    improve_query_text = improve_query(project_name, row['query'])
                    
                    (response, context_data) = run_local_search(
                        root_dir=project_path(project_name),
                        query=improve_query_text,
                        community_level=int(community_level),
                        response_type="Multiple Paragraphs",
                        streaming=False,
                        config_filepath=None,
                        data_dir=None,
                    )
                    
                    st.info(f"Query: {row['query']}")
                    
                    score = "0"
                    
                    if 'answer' in row:
                        st.warning(f"Answer: {row['answer']}")
                        score = response_score(improve_query_text, row['answer'], response)
                    
                    modified_df.at[index, "response"] = response
                    modified_df.at[index, "score"] = score
                        
                    st.success(f"GraphRAG ({score}%): {response}")
            
            modified_sheets[sheet_name] = modified_df
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in modified_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)   
                
        st.download_button(
            label="Download Test Results",
            data=output.getvalue(),
            file_name="response_excel.xlsx",
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
