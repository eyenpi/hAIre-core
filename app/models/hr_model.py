from pydantic import BaseModel


class HRInputModel(BaseModel):
    questions: list[str]
    metrics: list[str]
    email_address: str
    ask_from_cv: bool
