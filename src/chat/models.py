from datetime import datetime
from enum import Enum
from typing import List, Optional
from beanie import (
    Document,
    UnionDoc,
    Indexed,
    Link,
    Insert,
    Update,
    Replace,
    Save,
    SaveChanges,
    after_event,
    before_event,
)
from pydantic import Field
from telethon.types import Channel, Chat, ChatFull
from src.user import TGUser


class ChatTypes(str, Enum):
    Group = "group"
    Channel = "channel"  # noqa: F811


class TGChat(Document):
    tg_id: Indexed(int, unique=True)  # type: ignore
    type: ChatTypes

    title: str = Field(..., description="Title of the chat")
    chat_type: str = Field(
        ..., description="Type of the chat (e.g., Channel, Chat, etc.)"
    )

    username: Optional[str] = Field(
        None, description="Username of the chat, if available"
    )
    usernames: Optional[List[str]] = Field(
        None, description="List of all usernames associated with the chat"
    )

    participants_count: Optional[int] = Field(
        None, description="Number of participants in the chat"
    )
    creation_date: Optional[datetime] = Field(
        None, description="Date the chat was created"
    )

    call_active: bool = Field(False, description="Is there an active call in the chat?")
    noforwards: bool = Field(False, description="Are forwards not allowed in the chat?")

    verified: bool = Field(False, description="Is the chat verified?")
    fake: bool = Field(False, description="Is the chat marked as fake?")
    scam: bool = Field(False, description="Is the chat marked as a scam?")
    restricted: bool = Field(False, description="Is the chat restricted?")
    restriction_reason: Optional[str] = Field(
        None, description="Reason for the restriction, if any"
    )

    level: Optional[int] = Field(None, description="Level of the chat")
    emoji_status: Optional[str] = Field(None, description="Emoji status of the chat")

    stories_unavailable: bool = Field(
        False, description="Are stories unavailable for the chat?"
    )
    stories_hidden: bool = Field(False, description="Are stories hidden in the chat?")

    broadcast: bool = Field(True, description="Is the chat a broadcast channel?")
    forum: bool = Field(False, description="Is the chat a forum?")
    megagroup: bool = Field(False, description="Is the chat a megagroup?")
    gigagroup: bool = Field(False, description="Is the chat a gigagroup?")

    can_view_participants: bool = Field(
        False, description="Can members view the participants?"
    )

    participants_hidden: Optional[bool] = Field(
        None, description="Are participants hidden?"
    )
    about: Optional[str] = Field(None, description="About information for the chat")
    pinned_msg_id: Optional[int] = Field(
        None, description="ID of the pinned message in the chat"
    )
    antispam: bool = Field(False, description="Is anti-spam enabled?")
    hidden_prehistory: Optional[bool] = Field(
        False, description="Is the prehistory hidden?"
    )
    online_count: Optional[int] = Field(
        None, description="Number of online members in the chat"
    )
    location: Optional[str] = Field(
        None, description="Location of the chat, if available"
    )
    paid_media_allowed: Optional[bool] = Field(
        None, description="Are paid media allowed in the chat?"
    )
    paid_reactions_available: Optional[bool] = Field(
        None, description="Are paid reactions available in the chat?"
    )
    linked_chat_id: Optional[int] = Field(None, description="linked chat id")

    invitation_links: Optional[List[str]] = Field(None, description="Invitation links")
    members: Optional[List[Link[TGUser]]] = Field(None, description="Chat members list")
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "chats"
        
        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()
