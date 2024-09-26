from beanie import PydanticObjectId
from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status,UploadFile

explore_router = APIRouter()
