from fastapi.responses import FileResponse, RedirectResponse
from libs.common import set_venvs
from libs.set_prompt import improve_query
from libs.store_vector import PG
from openai import AzureOpenAI
from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
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
    db: str


# -----------------------------------------------------------------
@app.get("/favicon.ico")
async def favicon():
   return FileResponse(os.path.join("avatars", "favicon.ico"))


# -----------------------------------------------------------------
@app.post("/api/local_search")
async def local_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        set_venvs(item.rag_version)
        
        result = await run_local_search(
            rag_version=item.rag_version,
            db=item.db,
            query=improve_query(item.rag_version, item.query),
        )

        return {
                "message": "ok",
                "tenant_name": config.tenant_name,
                "result": result.response
            }
    except Exception as e:
        return {
                "tenant_name": config.tenant_name,
                "error": str(e),
               }


# -----------------------------------------------------------------
@app.post("/api/global_search")
async def global_search(item: Item, api_key: str=Header(...)):
    try:
        if config.api_key != api_key:
            raise Exception("Invalid api-key")
        
        set_venvs(item.rag_version)

        result = await run_global_search(
            rag_version=item.rag_version,
            db=item.db,
            query=improve_query(item.rag_version, item.query),
        )

        return {
                "message": "ok",
                "tenant_name": config.tenant_name,
                "result": result.response
            }
    except Exception as e:
        return {
                "tenant_name": config.tenant_name,
                "error": str(e),
               }
