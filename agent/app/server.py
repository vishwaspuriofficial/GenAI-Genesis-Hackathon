from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from utils import debug
from model.question import QuestionRequest
from pipeline.builder import graph
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

debug()


@app.post("/get_answer")
async def get_answer(request: QuestionRequest):
    try:
        response = graph.invoke(
            {"question": request.question, "context": request.question}
        )
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
