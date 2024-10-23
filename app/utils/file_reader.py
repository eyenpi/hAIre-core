import os
import json


def get_hr_questions():
    """
    Get the HR questions from the JSON file.
    """
    QUESTIONS_FILE = os.getenv(
        "QUESTIONS_FILE", "hr_questions.json"
    )  # Default to hr_questions.json
    hr_questions = []

    # Check if the JSON file exists and read from it
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as file:
            hr_questions = json.load(file)  # Load the JSON data into the list

    return hr_questions
