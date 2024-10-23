import logging
from fastapi import File, UploadFile, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.services.stt_service import STT
from app.services.pseudonymize import DataProcessor
from app.utils.singleton import AgentSingleton
from app.services.tts_service import TextToSpeechService
import base64

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Initialize services
stt_service = STT()
anonymizer_service = DataProcessor()
tts_service = TextToSpeechService()


@router.post("/start/")
async def get_first_question():
    """
    Get the first question from the chatbot.
    This is called the first time to start the conversation.
    """
    try:
        logger.info("Getting the first question from the chatbot.")
        chatbot_service = AgentSingleton.get_instance()

        # Step 1: Get the first question from the chatbot
        first_question_response = chatbot_service.handle_question_and_answer()

        # Log the first question and the status
        logger.info(f"First question received: {first_question_response['question']}")
        logger.info(f"Status: {first_question_response['status']}")

        # Step 2: Convert the question text to speech using TTS
        question_text = first_question_response["question"]
        audio_content = tts_service.get_sound_of_text(question_text)
        logger.info("TTS conversion for the first question completed.")

        # Step 3: Return both the text question and the audio file
        audio_bytes_io = BytesIO(audio_content)
        audio_bytes_io.seek(0)  # Move to the start of the BytesIO object for streaming

        logger.info("Returning the audio file to the frontend.")

        # Use StreamingResponse for BytesIO
        return StreamingResponse(audio_bytes_io, media_type="audio/mpeg")

    except Exception as e:
        logger.error(f"Error retrieving first question: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving first question: {str(e)}"
        )


@router.post("/next_step/")
async def process_audio(file: UploadFile = File(...)):
    try:
        logger.info("Received audio file from frontend")
        chatbot_service = AgentSingleton.get_instance()

        # Step 1: Receive audio file from frontend and transcribe it
        audio_data = await file.read()
        transcribed_text = stt_service.execute(audio_data)
        logger.info(f"Transcription complete: {transcribed_text}")

        # Step 2: Pass the transcription through the anonymizer
        pseudonymized_text, pseudonymized_entity_dict = anonymizer_service.process_text(
            transcribed_text
        )
        logger.info(f"Text after anonymization: {pseudonymized_text}")

        # Step 3: Send the pseudonymized text to the chatbot
        chatbot_response = chatbot_service.handle_question_and_answer(
            pseudonymized_text
        )
        logger.info(f"Chatbot response: {chatbot_response}")

        # Step 4: Convert chatbot's response to speech using TTS
        chatbot_answer = chatbot_response["question"]
        audio_content = tts_service.get_sound_of_text(chatbot_answer)
        logger.info("TTS conversion completed.")

        # Step 5: Encode audio content in base64 to send as part of the JSON response
        audio_base64 = base64.b64encode(audio_content).decode("utf-8")

        # Step 6: Return JSON response with status, question text, and audio content
        response = {
            "status": chatbot_response["status"],
            "question_text": chatbot_answer,
            "question_audio": audio_base64,  # This is the audio in base64 format
        }
        logger.info("Returning JSON response with question text and audio.")
        return response

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
