

import asyncio
import time
import streamlit as st
from graphrag.index.emit.types import TableEmitterType
from libs.common import run_command, load_graphrag_config
import libs.config as config
import graphrag.api as api
import asyncio
import time
import streamlit as st
import libs.config as config
import asyncio

from libs.progress import PrintProgressReporter


def build_index(project_name: str):
    try:
        if st.button('Start Build', key='build_index_' + project_name):
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
    except Exception as e:
        st.error(str(e))

    if st.button("Clear index files", key="clear_index_" + project_name):
        run_command(f"rm -rf /app/projects/{project_name}/output/*")
        time.sleep(3)
        st.success("All files deleted.")
