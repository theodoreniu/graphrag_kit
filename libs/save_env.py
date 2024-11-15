import streamlit as st
import os
from streamlit_ace import st_ace


def get_envs():
    env_file = f"/app/.env"
    if not os.path.exists(env_file):
        return ""
    
    with open(env_file, 'r') as f:
        prompt = f.read()
        return prompt


def set_envs():
    with st.expander("ENV"):

        env_file = f"/app/.env"

        envs = get_envs()

        new_envs = st_ace(envs,
                          key=f"env_file",
                          theme="tomorrow_night",
                          language='sh',
                          height=300,
                          auto_update=True,
                          )

        if st.button("Save", key=f"save_env", icon="💾"):
            with open(env_file, 'w') as f:
                f.write(new_envs)
            st.success("ENV saved. You need to restart app for it to take effect.")
