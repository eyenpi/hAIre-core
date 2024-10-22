from fastapi import FastAPI
from app.api.v1.routes import (
    speech_to_text,
    text_to_speech,
    cv_extraction,
    hr_chatbot,
    hr_panel,
)

app = FastAPI(
    title="CV Screening and Interview Bot",
    version="1.0.0",
    description="An end-to-end system for CV screening, interviewing using LLMs, and evaluation.",
)

# Including the individual routes
app.include_router(speech_to_text.router, prefix="/api/v1/stt", tags=["Speech-to-Text"])
app.include_router(text_to_speech.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
app.include_router(cv_extraction.router, prefix="/api/v1/cv", tags=["CV Extraction"])
app.include_router(hr_chatbot.router, prefix="/api/v1/hr-bot", tags=["HR Chatbot"])
app.include_router(hr_panel.router, prefix="/api/v1/hr-panel", tags=["HR Panel"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
