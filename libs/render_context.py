import re
import streamlit as st
import pandas as pd


def get_real_response(response:str):
    return re.match(r"^[^[]*", response).group(0).strip()


def render_context_data_local(context_data:dict):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Entities", "Reports", "Relationships", "Claims", "Sources"])
    
    df = pd.DataFrame(context_data['entities'])
    tab1.markdown(f"Items: `{len(df)}`")
    df["number of relationships"] = pd.to_numeric(df["number of relationships"], errors='coerce')
    df = df.sort_values(by="number of relationships", ascending=False)
    tab1.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['reports'])
    tab2.markdown(f"Items: `{len(df)}`")
    tab2.dataframe(df, use_container_width=True)

    df = pd.DataFrame(context_data['relationships'])
    tab3.markdown(f"Items: `{len(df)}`")
    df["weight"] = pd.to_numeric(df["weight"], errors='coerce')
    if 'links' in df:
        df["links"] = pd.to_numeric(df["links"], errors='coerce')
    df = df.sort_values(by="weight", ascending=False) 
    tab3.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['claims'])
    tab4.markdown(f"Items: `{len(df)}`")
    tab4.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['sources'])
    tab5.markdown(f"Items: `{len(df)}`")
    tab5.dataframe(df, use_container_width=True)


def render_context_data_global(context_data:dict):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Reports", "Entities", "Relationships", "Claims", "Sources"])
        
    df = pd.DataFrame(context_data['reports'])
    tab1.markdown(f"Items: `{len(df)}`")
    
    if "occurrence weight" in df.columns:
        df["occurrence weight"] = pd.to_numeric(df["occurrence weight"], errors='coerce')
        df = df.sort_values(by="occurrence weight", ascending=False)
        
    if "rank" in df.columns:
        df["rank"] = pd.to_numeric(df["rank"], errors='coerce')
    tab1.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['entities'])
    tab2.markdown(f"Items: `{len(df)}`")
    # df = df.sort_values(by="number of relationships", ascending=False) 
    tab2.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['relationships'])
    tab3.markdown(f"Items: `{len(df)}`")
    tab3.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['claims'])
    tab4.markdown(f"Items: `{len(df)}`")
    tab4.dataframe(df, use_container_width=True)
    
    df = pd.DataFrame(context_data['sources'])
    tab5.markdown(f"Items: `{len(df)}`")
    tab5.dataframe(df, use_container_width=True)


def render_context_data_drift(context_data:dict):
    with st.expander("context_data"):
        st.write(context_data)


def render_response(response:str):
    response = response.strip()
    result = get_real_response(response)
    st.success(f"GraphRAG (chars {len(result)}): {response}")
