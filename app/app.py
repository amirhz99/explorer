from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from src.routers import api_router
from src.models import initial_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initial_models()
    yield
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip().strip('"') for item in settings.ALLOWED_HOSTS.split(',')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router
)

app.mount("/static", StaticFiles(directory="static"), name="static")
