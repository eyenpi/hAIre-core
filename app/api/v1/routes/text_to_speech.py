from fastapi import APIRouter, Response
from io import BytesIO
from app.models.tts_stt_model import TextInput
from app.services.tts_service import TextToSpeechService

router = APIRouter()
model = TextToSpeechService()


@router.post("/convert")
async def text_to_speech(text_input: TextInput):
    try:
        text = text_input.text

        audio_content = model.get_sound_of_text(text)
        audio_buffer = BytesIO(audio_content)
        audio_buffer.seek(0)

        return Response(
            content=audio_buffer.read(),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )
    except Exception as e:
        return {"error": str(e)}
