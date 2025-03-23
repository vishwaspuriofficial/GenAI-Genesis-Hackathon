# main.py

from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
from db_utils import query_database

app = FastAPI()


@app.get("/query_database")
async def query_database_endpoint(query: str = Query(..., description="Your search query")):
    results = query_database(query)
    return results


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
