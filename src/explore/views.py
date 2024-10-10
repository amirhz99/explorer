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
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Chat, Channel
from src.chat.services import insert_chat_data
from src.chat.models import TGChat
from src.user.models import TGBot, TGUser
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    UserStatusOnline,
    UserStatusOffline,
    UserStatusRecently,
    UserStatusLastWeek,
    UserStatusLastMonth,
)
from telethon import functions

from src.user.services import insert_bot_data, insert_user_data

explore_router = APIRouter()

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
client = TelegramClient("sessions/60103274631", api_id, api_hash)



# Helper function to search globally and retrieve chat information
async def search_chats(query: str):

    await client.start()

    me = await client.get_me()

    # Perform search in Telegram
    search_results = await client(SearchRequest(q=query, limit=100))

    # Iterate over search results (users, bots)
    for user in search_results.users:
        
        full_user = (await client(GetFullUserRequest(user))).full_user
        
        # If the user is a bot, insert bot data
        if user.bot:
            await insert_bot_data(user, full_user)
        else:
            await insert_user_data(user,full_user)


    # Iterate over search results (groups, channels)
    for chat in search_results.chats:

        full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
        
        await insert_chat_data(chat,full_chat)

        linked_chat_id = getattr(full_chat, "linked_chat_id", None)
        if linked_chat_id:
            pass

        # deactivated = getattr(chat, 'deactivated', None)
        migrated_to = getattr(chat, "migrated_to", None)
        if migrated_to:
            pass

        can_view_participants = getattr(chat, "can_view_participants", False)
        if can_view_participants:
            async for participant in client.iter_participants(chat):
                pass


    await client.disconnect()


# FastAPI GET route to search for chats globally
@explore_router.get("/chats/")
async def search_telegram_chats(
    query: str = Query(..., description="Search term for Telegram chats")
):
    await search_chats(query)
    return {"query": query}
