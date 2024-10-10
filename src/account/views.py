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

account_router = APIRouter()
