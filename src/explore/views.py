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
from src.chat.models import TGChat
from src.user.models import TGUser
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

        user_id = user.id

        first_name = user.first_name
        last_name = getattr(user, "last_name", None)

        lang_code = getattr(user, "lang_code", None)

        username = getattr(user, "username", None)
        usernames = getattr(user, "usernames", None)
        phone = getattr(user, "phone", None)

        premium = getattr(user, "premium", False)
        emoji_status = getattr(user, "emoji_status", None)

        status = type(user.status).__name__
        if isinstance(user.status, UserStatusOffline):
            was_online = getattr(user.status, "was_online", None)

        support = getattr(user, "support", False)

        verified = getattr(user, "verified", False)
        fake = getattr(user, "fake", False)
        scam = getattr(user, "scam", False)
        restricted = getattr(user, "restricted", False)
        restriction_reason = getattr(user, "restriction_reason", None)
        deleted = getattr(user, "deleted", False)

        stories_unavailable = getattr(user, "stories_unavailable", False)
        stories_hidden = getattr(user, "stories_hidden", False)

        bot = getattr(user, "bot", False)

        full_user = (await client(GetFullUserRequest(user))).full_user
        about = getattr(full_user, "about", None)
        birthday = getattr(full_user, "birthday", None)

        private_forward_name = getattr(full_user, "private_forward_name", None)

        contact_require_premium = getattr(full_user, "contact_require_premium", False)

        phone_calls_available = getattr(full_user, "phone_calls_available", False)
        phone_calls_private = getattr(full_user, "phone_calls_private", False)

        personal_channel_id = getattr(full_user, "personal_channel_id", None)
        personal_channel_message = getattr(full_user, "personal_channel_message", None)

        business_away_message = getattr(full_user, "business_away_message", None)
        business_greeting_message = getattr(
            full_user, "business_greeting_message", None
        )
        business_intro = getattr(full_user, "business_intro", None)
        business_location = getattr(full_user, "business_location", None)
        business_work_hours = getattr(full_user, "business_work_hours", None)

        bot_description = getattr(bot, "bot_info.description", None)
        bot_description_document = getattr(bot, "bot_info.description_document", None)
        privacy_policy_url = getattr(bot, "bot_info.privacy_policy_url", None)

    # Iterate over search results (groups, channels)
    for chat in search_results.chats:

        full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat

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

        chat = TGChat(
            chat_id=chat.id,
            title=chat.title,
            chat_type=type(chat).__name__,
            username=getattr(chat, "username", None),
            usernames=getattr(chat, "usernames", None),
            participants_count=getattr(chat, "participants_count", None),
            creation_date=getattr(chat, "date", None),
            call_active=getattr(chat, "call_active", False),
            noforwards=getattr(chat, "noforwards", False),
            verified=getattr(chat, "verified", False),
            fake=getattr(chat, "fake", False),
            scam=getattr(chat, "scam", False),
            restricted=getattr(chat, "restricted", False),
            restriction_reason=getattr(chat, "restriction_reason", None),
            level=getattr(chat, "level", None),
            emoji_status=getattr(chat, "emoji_status", None),
            stories_unavailable=getattr(chat, "stories_unavailable", False),
            stories_hidden=getattr(chat, "stories_hidden", False),
            broadcast=getattr(chat, "broadcast", True),
            forum=getattr(chat, "forum", False),
            megagroup=getattr(chat, "megagroup", False),
            gigagroup=getattr(chat, "gigagroup", False),
            can_view_participants=can_view_participants,
            participants_hidden=getattr(chat, "participants_hidden", None),
            about=getattr(full_chat, "about", None),
            pinned_msg_id=getattr(full_chat, "pinned_msg_id", None),
            antispam=getattr(full_chat, "antispam", False),
            hidden_prehistory=getattr(full_chat, "hidden_prehistory", False),
            online_count=getattr(full_chat, "online_count", None),
            location=getattr(full_chat, "location", None),
            paid_media_allowed=getattr(full_chat, "paid_media_allowed", None),
            paid_reactions_available=getattr(
                full_chat, "paid_reactions_available", None
            ),
            linked_chat_id=linked_chat_id,
            scrapers=[me.id],
        )

        await chat.insert()

    await client.disconnect()


# FastAPI GET route to search for chats globally
@explore_router.get("/chats/")
async def search_telegram_chats(
    query: str = Query(..., description="Search term for Telegram chats")
):
    await search_chats(query)
    return {"query": query}
