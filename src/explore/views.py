from beanie import PydanticObjectId
from starlette.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status,UploadFile
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Chat, Channel
from src.user.models import TGUser
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth

explore_router = APIRouter()

api_id = 2040
api_hash = 'b18441a1ff607e10a989891a5462e627'
client = TelegramClient('sessions/60103274631', api_id, api_hash)

# Helper function to search globally and retrieve chat information
async def search_chats(query: str):
    
    await client.start()

    # Perform search in Telegram
    search_results = await client(SearchRequest(
        q=query,
        limit=100
    ))

    # Iterate over search results (users, bots)
    for user in search_results.users:
        
        user_id = user.id
        first_name = user.first_name
        last_name = getattr(user, 'last_name', None)
        
        lang_code = getattr(user, 'lang_code', None)
        
        username = getattr(user, 'username', None)
        usernames = getattr(user, 'usernames', None)
        phone = getattr(user, 'phone', None)
        
        premium = getattr(user, 'premium', False)
        emoji_status = getattr(user, 'emoji_status', None)
        
        
        status = type(user.status).__name__
        if isinstance(user.status, UserStatusOffline):
            was_online = getattr(user.status, 'was_online', None)
        
        support = getattr(user, 'support', False)
        
        verified = getattr(user, 'verified', False)
        fake = getattr(user, 'fake', False)
        scam = getattr(user, 'scam', False)
        restricted = getattr(user, 'restricted', False)
        restriction_reason = getattr(user, 'restriction_reason', None)
        deleted = getattr(user, 'deleted', False)
        
        stories_unavailable = getattr(user, 'stories_unavailable', False)
        stories_hidden = getattr(user, 'stories_hidden', False)
        
        bot = getattr(user, 'bot', None)
        
        full_user = (await client(GetFullUserRequest(user))).full_user
        about = getattr(full_user, 'about', None)
        birthday = getattr(full_user, 'birthday', None)
        
        private_forward_name = getattr(full_user, 'private_forward_name', None)
        
        contact_require_premium = getattr(full_user, 'contact_require_premium', False)
        
        phone_calls_available = getattr(full_user, 'phone_calls_available', False)
        phone_calls_private = getattr(full_user, 'phone_calls_private', False)
        
        personal_channel_id = getattr(full_user, 'personal_channel_id', None)
        personal_channel_message = getattr(full_user, 'personal_channel_message', None)        
        
        business_away_message = getattr(full_user, 'business_away_message', None)
        business_greeting_message = getattr(full_user, 'business_greeting_message', None)
        business_intro = getattr(full_user, 'business_intro', None)
        business_location = getattr(full_user, 'business_location', None)
        business_work_hours = getattr(full_user, 'business_work_hours', None)
        
        if bot:
            bot = full_user.bot_info
            bot_description = getattr(bot, 'description', None)
            bot_description_document = getattr(bot, 'description_document', None)
                   
    # Iterate over search results (groups, channels)
    for chat in search_results.chats:

        # Extract chat details
        chat_id = chat.id
        title = chat.title
        chat_type = type(chat).__name__
        username = getattr(chat, 'username', None)
        usernames = getattr(chat, 'usernames', None)
        
        participants_count = getattr(chat, 'participants_count', None)
        creation_date = getattr(chat, 'date', None)
        
        call_active = getattr(chat, 'call_active', False)
        noforwards = getattr(chat, 'noforwards', False)
                
        verified = getattr(chat, 'verified', False)
        fake = getattr(chat, 'fake', False)
        scam = getattr(chat, 'scam', False)
        restricted = getattr(chat, 'restricted', False)
        restriction_reason = getattr(chat, 'restriction_reason', False)
        
        level = getattr(chat, 'level', None)
        color = getattr(chat, 'color', None)
        profile_color = getattr(chat, 'profile_color', None)
        emoji_status = getattr(chat, 'emoji_status', None)
        
        has_geo = getattr(chat, 'has_geo', None)
        has_link = getattr(chat, 'has_link', False)
        
        stories_unavailable = getattr(chat, 'stories_unavailable', False)
        stories_hidden = getattr(chat, 'stories_hidden', False)
        
        broadcast = getattr(chat, 'broadcast', True)
        forum = getattr(chat, 'forum', False)
        megagroup = getattr(chat, 'megagroup', False)
        gigagroup = getattr(chat, 'gigagroup', False)
        
        full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
        
        can_view_participants = getattr(chat, 'can_view_participants', False)
        
        participants_hidden = getattr(chat, 'participants_hidden', None)
        about = getattr(full_chat, 'about', None)
        pinned_msg_id = getattr(full_chat, 'pinned_msg_id', None)
        antispam = getattr(full_chat, 'antispam', False)
        hidden_prehistory = getattr(full_chat, 'hidden_prehistory', None)
        online_count = getattr(full_chat, 'online_count', None)
        location = getattr(full_chat, 'location', None)
        paid_media_allowed = getattr(full_chat, 'paid_media_allowed', None)
        paid_reactions_available = getattr(full_chat, 'paid_reactions_available', None)
        
        
        if has_link:
            linked_chat_id = full_chat.linked_chat_id
            linked_chat = await client.get_entity(linked_chat_id)
            full_linked_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
            
        # Fetch full chat/channel information
        if isinstance(chat, Chat) or not broadcast:
            pass
            # full_chat = await client.get_entity(chat)
            
            # participants = await client.get_participants(chat)
            # participants_count = len(participants)

            # Store participants in MongoDB
            # async for participant in client.iter_participants(chat):

            #     full_user = (await client(GetFullUserRequest(participant))).full_user
            #     id = full_user.id
            #     bio = getattr(full_user, 'about', None)

            #     user_info = TGUser(
            #         user_id=participant.id,
            #         first_name=participant.first_name,
            #         last_name=participant.last_name,
            #         username=participant.username,
            #         chat_id=chat_id,
            #         is_admin=getattr(participant, 'admin_rights', None) is not None,
            #         bio=bio
            #     )
            #     # Insert participant into MongoDB
            #     await user_info.insert()

        elif isinstance(chat, Channel):
            pass
            # Store chat info into MongoDB
            # chat_doc = ChatInfo(
            #     chat_id=chat_id,
            #     title=title,
            #     chat_type=chat_type,
            #     username=username,
            #     participants_count=participants_count,
            #     creation_date=creation_date,
            #     description=description
            # )

            # await chat_doc.insert()

    await client.disconnect()
    

# FastAPI GET route to search for chats globally
@explore_router.get("/chats/")
async def search_telegram_chats(query: str = Query(..., description="Search term for Telegram chats")):
    await search_chats(query)
    return {"query": query}