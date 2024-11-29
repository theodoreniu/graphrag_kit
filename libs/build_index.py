import asyncio
import time

import graphrag.api as api
import streamlit as st
from graphrag.index.emit.types import TableEmitterType

from libs.common import run_command, load_graphrag_config
from libs.progress import PrintProgressReporter


def build_index(project_name: str):

    if st.button('Start Build', key='build_index_' + project_name, icon="🚀"):
        with st.spinner("Building index..."):
            
            progress_reporter = PrintProgressReporter("")
            config = load_graphrag_config(project_name)
            
            st.json(config, expanded=False)
            
            asyncio.run(api.build_index(
                    config=config,
                    run_id="",
                    is_resume_run=False,
                    memory_profile=False,
                    progress_reporter=progress_reporter,
                    emit=[TableEmitterType.Parquet],
                ))

    st.markdown("----------------------------")
    
    if st.button("Clear index files", key="clear_index_" + project_name, icon="🗑️"):
        run_command(f"rm -rf /app/projects/{project_name}/output/*")
        st.success("All files deleted.")
        time.sleep(3)
        