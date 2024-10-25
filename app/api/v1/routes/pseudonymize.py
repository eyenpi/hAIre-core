from fastapi import APIRouter
from app.models.pseudonymize_model import (
    ProcessTextRequest,
    ProcessTextResponse,
    DepseudonymizeTextRequest,
    DepseudonymizeTextResponse,
)
from app.services.pseudonymize import AnonymizationProcessor, EntityRecognizer

# Initialize the entity recognizer and anonymization processor
entity_recognizer = EntityRecognizer()
processor = AnonymizationProcessor(entity_recognizer)
router = APIRouter()


# Route to pseudonymize text
@router.post("/pseudonymize", response_model=ProcessTextResponse)
async def pseudonymize_text(request: ProcessTextRequest):
    pseudonymized_text = processor.anonymize_text(request.text)
    return ProcessTextResponse(
        pseudonymized_text=pseudonymized_text,
        pseudonymized_entity_dict=processor.entity_map,  # Send the entity mapping
    )


# Route to depseudonymize text
@router.post("/depseudonymize", response_model=DepseudonymizeTextResponse)
async def depseudonymize_text(request: DepseudonymizeTextRequest):
    original_text = processor.reverse_anonymization(request.pseudonymized_text)
    return DepseudonymizeTextResponse(original_text=original_text)
