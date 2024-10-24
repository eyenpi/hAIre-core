import logging
from fastapi import File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from app.services.stt_service import STT
from app.services.pseudonymize import AnonymizationProcessor, EntityRecognizer
from app.utils.singleton import AgentSingleton
from app.services.tts_service import TextToSpeechService
import base64
import librosa

# Initialize logger and log to a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler to log to a file
file_handler = logging.FileHandler("app_log.log")
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the file handler
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Optionally, also log to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

router = APIRouter()

# Initialize services
stt_service = STT()
entity_recognizer = EntityRecognizer()  # Updated to use EntityRecognizer
anonymizer_service = AnonymizationProcessor(
    entity_recognizer
)  # Updated to use AnonymizationProcessor
tts_service = TextToSpeechService()


# Helper function to save question and answer to file
def save_question_and_answer(question: str, answer: str = None):
    with open("conversation_log.txt", "a+") as file:
        if not answer:
            file.write(f"**Start of Conversation**\n\nQuestion: {question}\n")
        elif not question:
            file.write(f"**End of conversation**")
        else:
            file.write(f"Answer: {answer}\n\nQuestion: {question}\n")


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

        # No user answer yet, but we save the question
        save_question_and_answer(first_question_response["question"])

        # Step 2: Convert the question text to speech using TTS
        question_text = first_question_response["question"]
        audio_content = tts_service.get_sound_of_text(question_text)
        logger.info("TTS conversion for the first question completed.")

        # Step 3: Encode audio content in base64 to send as part of the JSON response
        audio_base64 = base64.b64encode(audio_content).decode("utf-8")

        # Step 4: Return JSON response with question text and audio content
        response = {
            "status": first_question_response["status"],
            "question_text": question_text,
            "question_audio": audio_base64,
        }
        logger.info("Returning JSON response with question text and audio.")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error retrieving first question: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error retrieving first question: {str(e)}"
        )


@router.post("/next_step/")
async def process_audio(audio_file: UploadFile = File(...)):
    try:
        logger.info("Received audio file from frontend")
        chatbot_service = AgentSingleton.get_instance()

        # Step 1: Receive audio file from frontend and transcribe it
        audio_bytes = await audio_file.read()

        temp_audio_path = "temp_audio_file.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_bytes)

        logger.info("Audio file written to disk at %s", temp_audio_path)

        # Step 2: Load the audio file using librosa
        audio, sr = librosa.load(temp_audio_path, sr=16000)
        logger.info("Audio loaded successfully with sampling rate of %s.", sr)

        transcribed_text = stt_service.execute(audio)
        logger.info(f"Transcription complete: {transcribed_text}")

        # Step 3: Pass the transcription through the anonymizer
        pseudonymized_text = anonymizer_service.anonymize_text(transcribed_text)
        logger.info(f"Text after anonymization: {pseudonymized_text}")
        logger.info(f"Entity mapping: {anonymizer_service.entity_map}")

        # Step 4: Send the pseudonymized text to the chatbot
        chatbot_response = chatbot_service.handle_question_and_answer(
            pseudonymized_text
        )
        logger.info(f"Chatbot response: {chatbot_response}")

        # Save the question and the user's transcribed and pseudonymized answer
        save_question_and_answer(
            chatbot_response["question"],
            anonymizer_service.reverse_anonymization(pseudonymized_text),
        )

        if chatbot_response["status"] == "completed":
            logger.info("Chatbot conversation completed.")
            return JSONResponse(
                content={
                    "status": "completed",
                    "question_text": None,
                    "question_audio": None,
                }
            )

        # Step 5: Convert chatbot's response to speech using TTS
        chatbot_answer = chatbot_response["question"]
        audio_content = tts_service.get_sound_of_text(chatbot_answer)
        logger.info("TTS conversion completed.")

        # Step 6: Encode audio content in base64 to send as part of the JSON response
        audio_base64 = base64.b64encode(audio_content).decode("utf-8")

        # Step 7: Return JSON response with status, question text, and audio content
        response = {
            "status": chatbot_response["status"],
            "question_text": chatbot_answer,
            "question_audio": audio_base64,  # This is the audio in base64 format
        }
        logger.info("Returning JSON response with question text and audio.")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
