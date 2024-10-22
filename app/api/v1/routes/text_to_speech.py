from io import BytesIO

from fastapi import APIRouter, Response

from app.services import tts_service

router = APIRouter()


@router.post("/convert")
async def text_to_speech(text: str):
    try:
        audio_content = tts_service.get_sound_of_text(text)
        audio_buffer = BytesIO(audio_content)
        audio_buffer.seek(0)
        return Response(content=audio_buffer.read(), media_type="audio/mpeg", headers={
            "Content-Disposition": "attachment; filename=speech.mp3"
        })
    except Exception as e:
        return {'error': str(e)}