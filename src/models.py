from beanie import init_beanie
from src.account.models import TGAccount
from app.db import db
from src.explore import reset_in_process_tasks, Explore
from src.search import Search
from src.chat import TGChat
from src.user import TGUser, TGBot, TekegramUserParent

async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            TGChat,
            TekegramUserParent,
            TGUser,
            TGBot,
            TGAccount,
            Explore,
            Search,
        ],
    )

    await reset_in_process_tasks()
