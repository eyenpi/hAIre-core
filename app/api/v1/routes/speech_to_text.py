import io
import logging
import librosa
from fastapi import APIRouter, File, UploadFile
from app.services.stt_service import STT
import os

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()
model = STT()


@router.post("/convert")
async def speech_to_text(audio_file: UploadFile = File(...)):
    try:
        logger.info("Received audio file for transcription.")

        # Step 1: Read the audio file bytes
        audio_bytes = await audio_file.read()

        # Step 2: Write the audio bytes to a temporary file (e.g., .wav format)
        temp_audio_path = "temp_audio_file.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        logger.info("Audio file written to disk at %s", temp_audio_path)

        # Step 3: Load the audio file using librosa
        audio, sr = librosa.load(temp_audio_path, sr=16000)
        logger.info("Audio loaded successfully with sampling rate of %s.", sr)

        # Optional: You can remove the temp file after loading it if not needed anymore
        os.remove(temp_audio_path)
        logger.info("Temporary audio file deleted.")

        # Step 4: Transcribe the audio
        transcript = model.execute(audio)
        logger.info("Transcription complete: %s", transcript)

        return {"message": transcript}

    except Exception as e:
        logger.error("Error during transcription: %s", str(e))
        return {"error": str(e)}
