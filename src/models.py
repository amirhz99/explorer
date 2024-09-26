from beanie import init_beanie
from app.db import db
from src.chat import ChatParent, Group, MegaGroup


async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            ChatParent,
            Group,
            MegaGroup,
        ],
    )
