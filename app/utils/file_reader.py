import os
import json


def get_hr_config():
    """
    Get the HR questions from the JSON file.
    """
    QUESTIONS_FILE = os.getenv("QUESTIONS_FILE", "assets/hr_questions.json")

    # Check if the JSON file exists and read from it
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as file:
            hr_config = json.load(file)  # Load the JSON data into the list

    hr_config = json.loads(hr_config)
    return hr_config
