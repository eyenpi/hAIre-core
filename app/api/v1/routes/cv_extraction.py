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

# Configure logging
logging.basicConfig(
    filename="cv_extraction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

router = APIRouter()

# Initialize services and processors
processor = CVProcessor(os.getenv("OPENAI_API_KEY"))
entity_recognizer = EntityRecognizer()


@router.post("/extract")
async def cv_extraction(cv_file: UploadFile = File(...)):
    try:
        dp = AnonymizationProcessor(entity_recognizer)

        updated_config = get_hr_config()
        print(type(updated_config))
        AgentSingleton.update_instance(updated_config)
        logging.info("New user registered. HR questions updated.")

        pdf_bytes = await cv_file.read()

        # Write to a file
        file_path = f"temp.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        logging.info(f"CV file saved to {file_path}")

        # Pass the file path to extract text from the CV
        text = processor.extract_text_from_cv(file_path)
        logging.info(
            "CV text extracted successfully. Extracted text: %s", text
        )  # Log first 500 characters

        # Pseudonymize the extracted CV text
        pseudonymized_text = dp.anonymize_text(text)
        logging.info(
            "Pseudonymization completed. Pseudonymized text: %s",
            pseudonymized_text,
        )
        logging.info("Pseudonymized entity dict: %s", dp.entity_map)

        # Segment the pseudonymized text
        segmented_text = processor.segment_cv(pseudonymized_text)
        logging.info("CV segmented successfully. Segmented text: %s", segmented_text)

        # Depseudonymize the segmented text to get the original data back
        depseudonymized_text = dp.reverse_anonymization(segmented_text)
        logging.info(
            "Depseudonymization completed. Final text: %s", depseudonymized_text
        )

        return JSONResponse(
            status_code=200,
            content=json.loads(depseudonymized_text),
        )

    except Exception as e:
        logging.error(f"Error during CV extraction: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred during CV extraction."
        )
