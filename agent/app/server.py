from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.model.question import QuestionRequest
from app.pipeline.builder import graph

app = FastAPI()


@app.post("/get_answer")
async def get_answer(request: QuestionRequest):
    try:
        response = graph.invoke({"question": request.question})
        return {"answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
