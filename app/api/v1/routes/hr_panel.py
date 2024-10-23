from fastapi import APIRouter, status
from typing import List
from fastapi.responses import JSONResponse
import os
import json
from dotenv import load_dotenv
from app.utils.file_reader import get_hr_questions

load_dotenv()

router = APIRouter()

hr_questions = []

# Define the file path
QUESTIONS_FILE = os.getenv("QUESTIONS_FILE")


@router.post("/questions", status_code=status.HTTP_201_CREATED)
async def save_questions(questions: List[str]):
    global hr_questions
    hr_questions = questions

    # Write questions to a JSON file
    with open(QUESTIONS_FILE, "w+") as file:
        json.dump(hr_questions, file)  # Save the list as JSON

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Questions saved and written to file!",
            "questions": hr_questions,
        },
    )


@router.get("/questions", status_code=status.HTTP_200_OK)
async def get_questions():

    hr_questions = get_hr_questions()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"questions": hr_questions},
    )
