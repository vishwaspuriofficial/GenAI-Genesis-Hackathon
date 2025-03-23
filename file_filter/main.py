# main.py

from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
from db_utils import query_database

app = FastAPI()

# Pydantic model to describe the metadata (including page_content)
class DocumentMetadata(BaseModel):
    source: str
    category: str
    date: str
    page_content: str

@app.get("/query_database", response_model=List[DocumentMetadata])
async def query_database_endpoint(query: str = Query(..., description="Your search query")):
    results = query_database(query)
    return results
