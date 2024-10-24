from fastapi import APIRouter, UploadFile, File

from app.services.cv_extraction_service import extract_text_from_cv, segment_cv
from app.services.pseudonymize import DataProcessor

router = APIRouter()


@router.post("/extract")
async def cv_extraction(cv_file: UploadFile = File(...)):
    pdf_bytes = await cv_file.read()
    text = extract_text_from_cv(pdf_bytes)

    # dp = DataProcessor()

    # pseudonymized_text, pseudonymized_entity_dict = dp.process_text(text)
    # segmented_text = segment_cv(pseudonymized_text)
    #
    # dipseudonymized_text = dp.depseudonymize_text(segmented_text, pseudonymized_entity_dict)
    segmented_text = segment_cv(text)
    return {'message': segmented_text}


    #####################################################################
    # Update the agent's questions
    # updated_questions = get_hr_questions()
    # AgentSingleton.update_instance(updated_questions)
    #
    # return JSONResponse(
    #     status_code=200,
    #     content={
    #         "name": "Hosein",
    #         "email": "hoseinmirhoseini64@gmail.com",
    #         "work_experiences": [
    #             {
    #                 "position": "Software Engineer",
    #                 "company": "Scalapay",
    #                 "from_to": "2021-01-01 to Present",
    #                 "description": "Software Engineer at Scalapay",
    #             },
    #             {
    #                 "position": "Frontend Developer",
    #                 "company": "Apple",
    #                 "from_to": "2020-01-01 to 2021-01-01",
    #                 "description": "Frontend Developer at Scalapay",
    #             },
    #         ],
    #         "educations": [
    #             {
    #                 "degree": "Bachelor of Computer Science",
    #                 "institution": "Shiraz University",
    #                 "from_to": "2017-01-01 to 2021-09-01",
    #             },
    #         ],
    #     },
    # )
