from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat_with_hr_bot(user_message: str):
    # Mock implementation for now
    return {"response": "Hello, this is your HR bot! How can I help?"}
