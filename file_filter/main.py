# main.py

import requests
import json
import os
import dotenv
from file_filter_utils import update_database_from_raw_files
from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
from db_utils import query_database
from test_download_and_extract import download_to_current_directory

app = FastAPI()


def get_all_files(meeting_id: str) -> List[str]:
    """
    Get all files for a given meeting ID
    :param meeting_id: Meeting ID
    :return: List of files
    """
    endpoint = f"/api/meetings/{meeting_id}/files"
    url = "http://localhost:8000" + endpoint
    response = requests.get(url)
    parsed = response.json()
    return parsed.get("files", [])


@app.get("/update_database")
async def update_database(meeting_id: str = Query(..., description="The meeting ID to fetch files for")):
    """
    Update the database with the latest documents.
    The URL is like: http://localhost:8025/update_database?meeting_id=4dtYGMkGnbnlooUQ8Aod
    """
    files = get_all_files(meeting_id)
    # Download all the files
    download_to_current_directory(files)
    # update the database
    update_database_from_raw_files()
    return {"message": "Database updated successfully", "meeting_id": meeting_id, "files_processed": len(files)}


if __name__ == '__main__':
    import uvicorn
    # no: 8000, 8080, 8501
    uvicorn.run(app, host="127.0.0.1", port=8025)
