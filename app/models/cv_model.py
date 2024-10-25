from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    result: bool
    score: int
