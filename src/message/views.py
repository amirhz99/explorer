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

message_router = APIRouter()
