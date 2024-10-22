from fastapi import APIRouter
from app.models.pseudonymize_model import (
    ProcessTextRequest,
    ProcessTextResponse,
    DepseudonymizeTextRequest,
    DepseudonymizeTextResponse,
)
from app.services.pseudonymize import DataProcessor

processor = DataProcessor()
router = APIRouter()


# Route to pseudonymize text
@router.post("/pseudonymize", response_model=ProcessTextResponse)
async def pseudonymize_text(request: ProcessTextRequest):
    pseudonymized_text, pseudonymized_entity_dict = processor.process_text(request.text)
    return ProcessTextResponse(
        pseudonymized_text=pseudonymized_text,
        pseudonymized_entity_dict=pseudonymized_entity_dict,
    )


# Route to depseudonymize text
@router.post("/depseudonymize", response_model=DepseudonymizeTextResponse)
async def depseudonymize_text(request: DepseudonymizeTextRequest):
    original_text = processor.depseudonymize_text(
        request.pseudonymized_text, request.pseudonymized_entity_dict
    )
    return DepseudonymizeTextResponse(original_text=original_text)
