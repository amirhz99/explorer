from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status

chat_router = APIRouter()
