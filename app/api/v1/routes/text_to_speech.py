from fastapi import APIRouter

router = APIRouter()


@router.post("/convert")
async def text_to_speech(text: str):
    # Mock implementation for now
    return {"message": "Text converted to speech successfully!"}
