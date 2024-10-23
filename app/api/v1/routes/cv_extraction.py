from fastapi import APIRouter, UploadFile, File
from app.utils.singleton import AgentSingleton
from app.utils.file_reader import get_hr_questions
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/extract")
async def cv_extraction(cv_file: UploadFile = File(...)):
    file_content = await cv_file.read()

    # Update the agent's questions
    updated_questions = get_hr_questions()
    AgentSingleton.update_instance(updated_questions)

    return JSONResponse(
        status_code=200,
        content={
            "name": "Hosein",
            "email": "hoseinmirhoseini64@gmail.com",
            "work_experiences": [
                {
                    "position": "Software Engineer",
                    "company": "Scalapay",
                    "from_to": "2021-01-01 to Present",
                    "description": "Software Engineer at Scalapay",
                },
                {
                    "position": "Frontend Developer",
                    "company": "Apple",
                    "from_to": "2020-01-01 to 2021-01-01",
                    "description": "Frontend Developer at Scalapay",
                },
            ],
            "educations": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "Shiraz University",
                    "from_to": "2017-01-01 to 2021-09-01",
                },
            ],
        },
    )
