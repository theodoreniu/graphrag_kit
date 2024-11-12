from fastapi.responses import FileResponse
from libs.common import project_path
from libs.set_prompt import improve_query
from fastapi import FastAPI, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import libs.config as config
import os
from graphrag.cli.query import run_local_search, run_global_search, run_drift_search

app = FastAPI(
    title="GraphRAG Kit API",
    version=config.app_version,
    terms_of_service="https://github.com/TheodoreNiu/graphrag_kit",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    query: str
    rag_version: str
    community_level: int = 2


# -----------------------------------------------------------------
@app.post("/api/local_search")
def local_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        # set_venvs(item.rag_version)
        
        (response, context_data) = run_local_search(
                    root_dir=project_path(item.rag_version),
                    query=improve_query(item.rag_version, item.query),
                    community_level=int(item.community_level),
                    response_type="Multiple Paragraphs",
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        return {
                "message": "ok",
                "response": response,
                "context_data": context_data
            }
    except Exception as e:
        return {
                "error": str(e),
               }


# -----------------------------------------------------------------
@app.post("/api/global_search")
def global_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        # set_venvs(item.rag_version)

        (response, context_data) = run_global_search(
                    root_dir=project_path(item.rag_version),
                    query=improve_query(item.rag_version, item.query),
                    community_level=int(item.community_level),
                    response_type="Multiple Paragraphs",
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        return {
                "message": "ok",
                "response": response,
                "context_data": context_data
            }
    except Exception as e:
        return {
                "error": str(e),
               }


@app.post("/api/drift_search")
def global_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        # set_venvs(item.rag_version)

        (response, context_data) = run_drift_search(
                    root_dir=project_path(item.rag_version),
                    query=improve_query(item.rag_version, item.query),
                    community_level=int(item.community_level),
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        return {
                "message": "ok",
                "response": response,
                "context_data": context_data
            }
    except Exception as e:
        return {
                "error": str(e),
               }
