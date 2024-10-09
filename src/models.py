from beanie import init_beanie
from app.db import db
from src.chat import ChatParent, Group, MegaGroup
from src.channel import ChannelParent, PublicChannel, PrivateChannel
from src.user import TGUser

async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            ChatParent,
            Group,
            MegaGroup,
            ChannelParent,
            PublicChannel,
            PrivateChannel,
            TGUser,
        ],
    )
