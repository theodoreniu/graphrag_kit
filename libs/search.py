from graphrag.query.llm.base import BaseLLMCallback
import streamlit as st
from graphrag.query.structured_search.base import SearchResult

class LLMCallback(BaseLLMCallback):
    """Base class for LLM callbacks."""

    def __init__(self):
        super().__init__()
        self.st = st.empty()
        self.buffer = ""

    def on_llm_new_token(self, token: str):
        super().on_llm_new_token(token)
        self.buffer += token
        self.st.success(self.buffer)

class GlobalSearchLLMCallback(BaseLLMCallback):
    """GlobalSearch LLM Callbacks."""

    def __init__(self):
        super().__init__()
        self.map_response_contexts = []
        self.map_response_outputs = []
        self.st = st.empty()

    def on_map_response_start(self, map_response_contexts: list[str]):
        """Handle the start of map response."""
        self.map_response_contexts = map_response_contexts
        # self.st.write(map_response_contexts)
        # st.write(map_response_contexts)
        

    def on_map_response_end(self, map_response_outputs: list[SearchResult]):
        """Handle the end of map response."""
        self.map_response_outputs = map_response_outputs
        # self.st.write(self.map_response_outputs)
        