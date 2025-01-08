from beanie import init_beanie
from src.account.models import TGAccount
from src.db import db
from src.task import Task
from src.search import Search
from src.chat import TGChat
from src.user import TGUser, TGBot, TekegramUserParent

async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            TGAccount,
            TGChat,
            TekegramUserParent,
            TGUser,
            TGBot,
            Search,
            Task,
        ],
    )
    # await Task.reset_in_process_tasks()
