from pydantic import BaseModel
from typing import Optional


class UserMessage(BaseModel):
    message: str


class QuestionRequest(BaseModel):
    answer: Optional[str] = None
