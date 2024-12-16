import asyncio
import time

from datashaper import WorkflowCallbacks
import graphrag.api as api
import streamlit as st

from libs.common import run_command, load_graphrag_config
from libs.progress import PrintProgressReporter


def build_index(project_name: str):

    if st.button('Start Build', key='build_index_' + project_name, icon="🚀"):
        with st.spinner("Building index..."):
            
            progress_reporter = PrintProgressReporter("")
            config = load_graphrag_config(project_name)
            
            st.json(config, expanded=False)
            
            # TODO: will support this in the future
            # workflow_callbacks = [
            #     WorkflowCallbacks(
            #         on_progress=lambda progress: st.write(progress)
            #     )
            # ]
            
            asyncio.run(api.build_index(
                    config=config,
                    run_id="",
                    is_resume_run=False,
                    memory_profile=False,
                    progress_reporter=progress_reporter,
                    # callbacks=workflow_callbacks,
                ))

    st.markdown("----------------------------")
    
    if st.button("Clear index files", key="clear_index_" + project_name, icon="🗑️"):
        run_command(f"rm -rf /app/projects/{project_name}/output/*")
        st.success("All files deleted.")
        time.sleep(3)
        
