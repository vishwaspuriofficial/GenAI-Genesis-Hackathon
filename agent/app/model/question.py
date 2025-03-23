
from openai import BaseModel


class QuestionRequest(BaseModel):
    question: str