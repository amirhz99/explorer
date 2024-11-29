from src.chat.models import ChatTypes, TGChat
from beanie.operators import Set


async def insert_chat_data(chat, full_chat):

    if not getattr(chat, "username", None) and not getattr(chat, "usernames", False):
        print(chat.title)
        
    await TGChat.find_one(TGChat.tg_id == chat.id).upsert(
        Set(
            {
                TGChat.title: chat.title,
                TGChat.chat_type: type(chat).__name__,
                TGChat.username: getattr(chat, "username", None),
                TGChat.usernames: ((item.username for item in chat.usernames) if getattr(chat, "usernames", False) else None),
                TGChat.participants_count: getattr(full_chat, "participants_count", None),
                TGChat.call_active: getattr(chat, "call_active", False),
                TGChat.noforwards: getattr(chat, "noforwards", False),
                TGChat.verified: getattr(chat, "verified", False),
                TGChat.fake: getattr(chat, "fake", False),
                TGChat.scam: getattr(chat, "scam", False),
                TGChat.restricted: getattr(chat, "restricted", False),
                TGChat.restriction_reason: getattr(chat, "restriction_reason", None),
                TGChat.level: getattr(chat, "level", None),
                TGChat.emoji_status: chat.emoji_status.document_id if getattr(chat, "emoji_status", None) else None,
                TGChat.stories_unavailable: getattr(chat, "stories_unavailable", False),
                TGChat.stories_hidden: getattr(chat, "stories_hidden", False),
                TGChat.broadcast: getattr(chat, "broadcast", False),
                TGChat.forum: getattr(chat, "forum", False),
                TGChat.megagroup: getattr(chat, "megagroup", False),
                TGChat.gigagroup: getattr(chat, "gigagroup", False),
                TGChat.can_view_participants: getattr(
                    chat, "can_view_participants", False
                ),
                TGChat.participants_hidden: getattr(chat, "participants_hidden", None),
                TGChat.about: getattr(full_chat, "about", None),
                TGChat.pinned_msg_id: getattr(full_chat, "pinned_msg_id", None),
                TGChat.antispam: getattr(full_chat, "antispam", False),
                TGChat.hidden_prehistory: getattr(
                    full_chat, "hidden_prehistory", False
                ),
                TGChat.online_count: getattr(full_chat, "online_count", None),
                TGChat.location: getattr(full_chat, "location", None),
                TGChat.paid_media_allowed: getattr(
                    full_chat, "paid_media_allowed", None
                ),
                TGChat.paid_reactions_available: getattr(
                    full_chat, "paid_reactions_available", None
                ),
                TGChat.linked_chat_id: getattr(full_chat, "linked_chat_id", None),
            }
        ),
        on_insert=TGChat(
            tg_id=chat.id,
            type=(
                ChatTypes.Channel
                if getattr(chat, "broadcast", False)
                else ChatTypes.Group
            ),
            title=chat.title,
            chat_type=type(chat).__name__,
            username=getattr(chat, "username", None),
            usernames=((item.username for item in chat.usernames) if getattr(chat, "usernames", False) else None),
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
            emoji_status=chat.emoji_status.document_id if getattr(chat, "emoji_status", None) else None,
            stories_unavailable=getattr(chat, "stories_unavailable", False),
            stories_hidden=getattr(chat, "stories_hidden", False),
            broadcast=getattr(chat, "broadcast", False),
            forum=getattr(chat, "forum", False),
            megagroup=getattr(chat, "megagroup", False),
            gigagroup=getattr(chat, "gigagroup", False),
            can_view_participants=getattr(chat, "can_view_participants", False),
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
            linked_chat_id=getattr(full_chat, "linked_chat_id", None),
        ),
    )
    
    return await TGChat.find_one(TGChat.tg_id == chat.id)
