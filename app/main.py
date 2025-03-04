from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import (
    speech_to_text,
    text_to_speech,
    cv_extraction,
    hr_panel,
    pseudonymize,
    flow,
)

app = FastAPI(
    title="CV Screening and Interview Bot",
    version="1.0.0",
    description="An end-to-end system for CV screening, interviewing using LLMs, and evaluation.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can specify specific domains instead of "*"
    allow_credentials=True,
    allow_methods=["*"],  # Allow specific HTTP methods like 'GET', 'POST' etc.
    allow_headers=["*"],  # Allow specific headers
)

# Including the individual routes
app.include_router(speech_to_text.router, prefix="/api/v1/stt", tags=["Speech-to-Text"])
app.include_router(text_to_speech.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])
app.include_router(cv_extraction.router, prefix="/api/v1/cv", tags=["CV Extraction"])
app.include_router(hr_panel.router, prefix="/api/v1/hr-panel", tags=["HR Panel"])
app.include_router(
    pseudonymize.router, prefix="/api/v1/pseudonymize", tags=["Pseudonymize"]
)
app.include_router(flow.router, prefix="/api/v1/flow", tags=["Flow"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
