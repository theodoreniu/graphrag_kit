from graphrag_kit.libs.common import set_venvs
from libs.global_search import run_global_search
from libs.local_search import run_local_search
from libs.set_prompt import improve_query
from libs.store_vector import PG
from openai import AzureOpenAI
from fastapi import FastAPI, Request,Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import libs.config as config
import os

app = FastAPI()

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
@app.post("/api/local_search")
async def local_search(item: Item, api_key: str = Header(...)):
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
async def global_search(item: Item, api_key: str = Header(...)):
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