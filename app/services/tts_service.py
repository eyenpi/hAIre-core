import os
from dotenv import load_dotenv
from openai import OpenAI


class TextToSpeechService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        # Initialize OpenAI client with API key from environment variables
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_sound_of_text(self, text: str) -> bytes:
        """
        Converts text to speech using the OpenAI API.
        :param text: The text to convert to speech.
        :return: The audio content in bytes.
        """
        response = self.client.audio.speech.create(
            model="tts-1", voice="alloy", input=text
        )
        audio_content = response.read()
        return audio_content
