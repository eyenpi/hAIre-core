from fastapi import APIRouter

router = APIRouter()


@router.post("/convert")
async def speech_to_text(audio_file: bytes):
    # Mock implementation for now
    return {"message": "Speech converted to text successfully!"}
