from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # handle encryption + storage
    return {"filename": file.filename}
