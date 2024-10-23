from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.chatbot_model import QuestionRequest
from app.utils.singleton import AgentSingleton

router = APIRouter()


@router.post("/chat")
async def handle_question(request: QuestionRequest):
    """
    This endpoint either asks the next question or processes the candidate's answer and returns the next step.
    """
    agent = AgentSingleton.get_instance()

    # Call the merged function, passing the answer if provided
    response = agent.handle_question_and_answer(request.answer)

    if response["status"]:
        return JSONResponse(status_code=200, content=response)

    raise HTTPException(status_code=400, detail="Invalid request.")
