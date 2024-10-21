from fastapi import APIRouter

router = APIRouter()


@router.post("/extract")
async def cv_extraction(cv_file: bytes):
    # Mock implementation for now
    return {"message": "CV details extracted successfully!"}
