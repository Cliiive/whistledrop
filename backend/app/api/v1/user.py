# Will be used to manage the users via ALias
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.get("/")
async def get_user():
    # generate a random alias
    return {"alias": "test"}