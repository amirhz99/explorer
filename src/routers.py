from fastapi import APIRouter
from src.user import tg_user_router
from src.message import message_router
from src.explore import explore_router
from src.chat import chat_router

api_router = APIRouter()

api_router.include_router(tg_user_router, prefix="/users", tags=["Users"])
api_router.include_router(message_router,prefix="/messages", tags=["Messages"])
api_router.include_router(explore_router, prefix="/explore", tags=["Explore"])
api_router.include_router(chat_router, prefix="/chats", tags=["Chats"])

