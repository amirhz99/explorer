from beanie import init_beanie
from app.db import db
from src.explore.views import reset_in_process_tasks
from src.chat import TGChat
from src.user import TGUser,TGBot,TekegramUserParent

async def initial_models():
    await init_beanie(
        database=db,
        document_models=[
            TGChat,
            TekegramUserParent,
            TGUser,
            TGBot,
        ],
    )
    
    await reset_in_process_tasks()
