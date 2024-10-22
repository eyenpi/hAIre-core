from pydantic import BaseModel
from typing import Dict


class ProcessTextRequest(BaseModel):
    text: str


class ProcessTextResponse(BaseModel):
    pseudonymized_text: str
    pseudonymized_entity_dict: Dict[str, str]


class DepseudonymizeTextRequest(BaseModel):
    pseudonymized_text: str
    pseudonymized_entity_dict: Dict[str, str]


class DepseudonymizeTextResponse(BaseModel):
    original_text: str
