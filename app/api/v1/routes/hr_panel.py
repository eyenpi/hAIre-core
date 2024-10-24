from fastapi import APIRouter, status, Body
from typing import List
from fastapi.responses import JSONResponse, FileResponse
import os
import json
from dotenv import load_dotenv
from app.utils.file_reader import get_hr_config
from app.services.hr_report import HRReportGenerator
from app.models.hr_model import HRInputModel

load_dotenv()

router = APIRouter()

hr_config = {}

# Define the file path
QUESTIONS_FILE = os.getenv("QUESTIONS_FILE")

# Initialize the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Instantiate the HRReportGenerator class
hr_report_generator = HRReportGenerator(api_key=api_key)


@router.post("/config", status_code=status.HTTP_201_CREATED)
async def save_config(data: HRInputModel):
    # Write questions to a JSON file
    with open(QUESTIONS_FILE, "w+") as file:
        json.dump(data.model_dump_json(), file)  # Save the list as JSON

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Data saved and written to file!",
            "data": data.model_dump_json(),
        },
    )


@router.get("/config", status_code=status.HTTP_200_OK)
async def get_config():

    hr_config = get_hr_config()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"config": hr_config},
    )


@router.post("/generate-report", status_code=status.HTTP_200_OK)
async def generate_report(conversation: str = Body(...)):
    """
    Generate a human-readable HR report based on the provided interview conversation.
    :param conversation: The interview conversation (questions and answers)
    :return: A formatted HR report for the manager.
    """
    file_path = "assets/hr_report.pdf"
    hr_config = get_hr_config()
    metrics = hr_config["metrics"]

    if not hr_config["metrics"]:
        metrics = [
            "Relevance",
            "Completeness",
            "Clarity",
            "Consistency",
            "Strengths and Weaknesses",
        ]
    report_content = hr_report_generator.generate_report(
        conversation, file_path, criteria=metrics
    )
    return FileResponse(
        file_path, media_type="application/pdf", filename="hr_report.pdf"
    )
