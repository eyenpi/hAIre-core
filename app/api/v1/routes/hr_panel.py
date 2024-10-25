from fastapi import APIRouter, status, HTTPException
from typing import List
from fastapi.responses import JSONResponse, FileResponse
import os
import json
from dotenv import load_dotenv
from app.utils.file_reader import get_hr_config
from app.services.hr_report import HRReportGenerator
from app.models.hr_model import HRInputModel
from app.utils.singleton import AgentSingleton
from app.utils.mail import EmailSender
from app.models.cv_model import EvaluationResponse
from app.services.cv_fit import CVJobFitEvaluator

load_dotenv()

router = APIRouter()

hr_config = {}

# Define the file path
QUESTIONS_FILE = os.getenv("QUESTIONS_FILE")

# Initialize the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Instantiate the HRReportGenerator class
hr_report_generator = HRReportGenerator(api_key=api_key)

evaluator = CVJobFitEvaluator(api_key=api_key)


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


@router.get("/questions", status_code=status.HTTP_200_OK)
async def get_config():

    agent = AgentSingleton.get_instance()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"questions": agent.questions},
    )


@router.get("/generate-report", status_code=status.HTTP_200_OK)
async def generate_report():
    """
    Generate a human-readable HR report based on the provided interview conversation.
    :param conversation: The interview conversation (questions and answers)
    :return: A formatted HR report for the manager.
    """
    conversation_file = "logs/conversation.log"
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
    # read conversation from file
    with open(conversation_file, "r") as file:
        conversation = file.read()

    report_content = hr_report_generator.generate_report(
        conversation, file_path, criteria=metrics
    )

    email_sender = EmailSender()
    email_sender.send_email(
        to_email=hr_config["email_address"],
        subject="HR Interview Report",
        body="Please find the attached HR interview report for your review.",
        file_path=file_path,
    )

    return FileResponse(
        file_path, media_type="application/pdf", filename="hr_report.pdf"
    )


@router.get("/download-report", status_code=status.HTTP_200_OK)
async def download_report():
    file_path = "assets/hr_report.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File not found")
    return FileResponse(
        file_path, media_type="application/pdf", filename="hr_report.pdf"
    )


@router.get(
    "/evaluate-fit", response_model=EvaluationResponse, status_code=status.HTTP_200_OK
)
async def evaluate_fit():
    """
    Evaluate the fit between the user's CV and the job description, returning a score and detailed assessment.

    :param request: EvaluationRequest object with user_cv and job_description
    :return: JSON response containing the score, evaluation, and overall assessment
    """
    try:
        # read user cv and job description from file
        with open("assets/segmented_cv.json", "r") as file:
            user_cv = json.load(file)
        hr_config = get_hr_config()
        job_description = hr_config["job_info"]
        result = evaluator.evaluate_fit(user_cv, job_description)

        return EvaluationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
