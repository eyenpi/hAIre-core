import io

import librosa
from fastapi import APIRouter, File, UploadFile

from app.services.stt_service import get_text_of_sound

router = APIRouter()


@router.post("/convert")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        audio_bytes = await audio_file.read()

        # Load the audio using librosa from bytes
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # Transcribe the audio
        transcript = get_text_of_sound(audio)
        return {'message': transcript}
    
    except Exception as e:
        return {'error': str(e)}

