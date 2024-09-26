from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    UploadFile,
    status,
    Query,
)

tg_user_router = APIRouter()
