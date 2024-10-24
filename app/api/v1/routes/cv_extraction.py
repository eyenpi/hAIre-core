import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pseudonymize import AnonymizationProcessor, EntityRecognizer
from app.utils.file_reader import get_hr_config
from fastapi.responses import JSONResponse
from app.utils.singleton import AgentSingleton
from dotenv import load_dotenv
from app.services.cv_extraction_service import CVProcessor
import os
import json

load_dotenv()

# Create the logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging with FileHandler explicitly
logger = logging.getLogger("cv_extraction_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/cv_extraction.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Add a StreamHandler to see logs in console too (optional)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

router = APIRouter()

# Initialize services and processors
processor = CVProcessor(os.getenv("OPENAI_API_KEY"))
entity_recognizer = EntityRecognizer()


@router.post("/extract")
async def cv_extraction(cv_file: UploadFile = File(...)):
    try:
        dp = AnonymizationProcessor(entity_recognizer)

        updated_config = get_hr_config()

        logger.info("New user registered. HR questions updated.")

        pdf_bytes = await cv_file.read()

        # Write to a file
        file_path = f"assets/temp.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        logger.info(f"CV file saved to {file_path}")

        # Pass the file path to extract text from the CV
        text = processor.extract_text_from_cv(file_path)
        logger.info(
            "CV text extracted successfully. Extracted text: %s", text[:500]
        )  # Log first 500 characters

        # Pseudonymize the extracted CV text
        pseudonymized_text = dp.anonymize_text(text)
        logger.info(
            "Pseudonymization completed. Pseudonymized text: %s",
            pseudonymized_text,
        )
        logger.info("Pseudonymized entity dict: %s", dp.entity_map)

        # Segment the pseudonymized text
        segmented_text = processor.segment_cv(pseudonymized_text)
        logger.info("CV segmented successfully. Segmented text: %s", segmented_text)

        with open("assets/segmented_cv.json", "w") as f:
            f.write(segmented_text)

        # Depseudonymize the segmented text to get the original data back
        depseudonymized_text = dp.reverse_anonymization(segmented_text)
        logger.info(
            "Depseudonymization completed. Final text: %s", depseudonymized_text
        )
        AgentSingleton.update_instance(updated_config)

        return JSONResponse(
            status_code=200,
            content=json.loads(depseudonymized_text),
        )

    except Exception as e:
        logger.error(f"Error during CV extraction: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred during CV extraction."
        )
