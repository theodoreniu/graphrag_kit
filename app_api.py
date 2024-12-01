import base64
import os
import re
from fastapi.responses import FileResponse
from libs.common import project_path
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import libs.config as config
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
    project_name: str
    community_level: int = 2
    dynamic_community_selection: bool = False
    query_source: bool = False
    user_cache: bool = False


def parse_file_info(input_string: str):
    match = re.match(r"(.*?\.pdf)_page_(\d+)\.png", input_string)
    if match:
        base_pdf = match.group(1)
        page_number = int(match.group(2))
        screenshot_file = f"{base_pdf}_page_{page_number}.png"
        return base_pdf, screenshot_file, page_number
    else:
        raise ValueError("输入字符串格式不正确，无法解析！")


def get_png_bas464_code_by_filepath(item: Item, screenshot_file: str):
    filepath = f"/app/projects/{item.project_name}/pdf_cache/{screenshot_file}"
    base64_pre = "data:image/png;base64,"
    with open(filepath, 'rb') as f:
        return base64_pre + base64.b64encode(f.read()).decode('utf-8')


def get_source_query(item: Item, context_data: any):
    
    sources = []
    
    if not item.query_source:
        return sources
    
    txt_files_path = f"/app/projects/{item.project_name}/pdf_cache"
    if not os.path.exists(txt_files_path):
        return sources
    
    source = context_data['sources'][0]['text']
    
    # search in every .txt
    for txt_file in os.listdir(txt_files_path):
        try:
            file_path = os.path.join(txt_files_path, txt_file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if source in content:
                    pdf_file, screenshot_file, page_number = parse_file_info(txt_file)
                    sources.append({
                        "pdf_file": pdf_file,
                        "screenshot_file": screenshot_file,
                        "page_number": page_number,
                    })
        except Exception as e:
            return {
                "txt_file": txt_file,
                "error": str(e)
            }
                
    return sources


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
@app.get("/api/pdf_cache")
def get_static_file(project_name: str, file_name: str):
    local_file_path = f"/app/projects/{project_name}/pdf_cache/{file_name}"
    if not os.path.exists(local_file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(local_file_path)


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
                "context_data": context_data,
                "sources": get_source_query(item, context_data),
                # "search_messages": st.session_state['search_messages']
            }
        
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

        return {
                "message": "ok",
                "response": response,
                "context_data": context_data,
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
        
        # set_venvs(item.project_name)

        (response, context_data) = run_drift_search(
                    root_dir=project_path(item.project_name),
                    query=item.query,
                    community_level=int(item.community_level),
                    streaming=False,
                    config_filepath=None,
                    data_dir=None,
                )

        return {
                "message": "ok",
                "response": response,
                "context_data": context_data,
            }
    except Exception as e:
        return {
                "error": str(e),
               }
