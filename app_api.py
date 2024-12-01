import os
from fastapi.responses import FileResponse
from libs.find_sources import get_query_sources
from libs.common import project_path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import libs.config as config
from graphrag.cli.query import run_local_search, run_global_search, run_drift_search
from dotenv import load_dotenv

load_dotenv()

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
    project_name: str
    community_level: int = 2
    dynamic_community_selection: bool = False
    query_source: bool = False
    user_cache: bool = False
    context_data: bool = False


local_search_cache = {}
local_search_cache_limit = 20


def get_local_search_cache(item: Item):
    if not item.user_cache:
        return None
    
    if item.query in local_search_cache:
        return local_search_cache[item.query]
    return None


def set_local_search_cache(item: Item, result: any):
    if not item.user_cache:
        return
    
    if len(local_search_cache) >= local_search_cache_limit:
        local_search_cache.pop(list(local_search_cache.keys())[0])
    local_search_cache[item.query] = result


# -----------------------------------------------------------------
@app.post("/api/local_search")
def local_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        cached_result = get_local_search_cache(item)
        if cached_result:
            return cached_result
        
        (response, context_data) = run_local_search(
                    root_dir=project_path(item.project_name),
                    query=item.query,
                    community_level=int(item.community_level),
                    response_type="Multiple Paragraphs",
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        result = {
                "message": "ok",
                "response": response,
                "query": item.query,
            }
        
        if item.query_source:
            result['sources'] = get_query_sources(item.project_name, context_data)
        
        if item.context_data:
            result['context_data'] = context_data
        
        set_local_search_cache(item, result)
        
        return result
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

        (response, context_data) = run_global_search(
                    root_dir=project_path(item.project_name),
                    query=item.query,
                    community_level=int(item.community_level),
                    response_type="Multiple Paragraphs",
                    dynamic_community_selection=bool(item.dynamic_community_selection),
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        result = {
                "message": "ok",
                "response": response,
                "query": item.query,
            }
        
        if item.context_data:
            result['context_data'] = context_data
        
        return result
    except Exception as e:
        return {
                "error": str(e),
               }


@app.post("/api/drift_search")
def global_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")

        (response, context_data) = run_drift_search(
                    root_dir=project_path(item.project_name),
                    query=item.query,
                    community_level=int(item.community_level),
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        result = {
                "message": "ok",
                "response": response,
                "query": item.query,
            }

        if item.context_data:
            result['context_data'] = context_data
        
        return result
    except Exception as e:
        return {
                "error": str(e),
               }
