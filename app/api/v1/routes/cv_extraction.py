from fastapi import APIRouter, UploadFile, File, Depends
from app.utils.singleton import AgentSingleton
from app.utils.file_reader import get_hr_questions

router = APIRouter()


@router.post("/extract")
async def cv_extraction(cv_file: UploadFile = File(...)):
    file_content = await cv_file.read()

    # Update the agent's questions
    updated_questions = get_hr_questions()
    AgentSingleton.update_instance(updated_questions)

    return {"message": "CV details extracted successfully!"}
