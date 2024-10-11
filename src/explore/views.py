import asyncio
from datetime import datetime
from typing import Any, Dict, List
from beanie import PydanticObjectId
from starlette.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
    UploadFile,
)
from telethon import TelegramClient
from src.account.models import TGAccount
from src.explore.models import Explore, OperationsStatus
from src.explore.services import search_chats

explore_router = APIRouter()

@explore_router.get("/")
async def search_telegram_chats(
    query: str = Query(..., description="Search term for Telegram chats"),
    repeat_time: int = Query(1, description="Number of accounts to use"),
):
    task = Explore(
        text=query,
        repeat_time=repeat_time,
        status=OperationsStatus.pending,
    )
    await task.insert()
    return JSONResponse(
        content={"message": "Task added to queue. Searching..."}, status_code=200
    )
