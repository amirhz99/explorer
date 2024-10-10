from beanie import init_beanie
from app.db import db
from src.chat import TGChat
from src.user import TGUser

async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            TGChat,
            TGUser,
        ],
    )
