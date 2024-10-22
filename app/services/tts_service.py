import os
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

def get_sound_of_text(text):
    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    audio_content = response.read()

    return audio_content

get_sound_of_text('test')