from datetime import datetime
from enum import Enum
from typing import List
from beanie import (
    Document,
    UnionDoc,
    Indexed,
    Link,
    Insert,
    Replace,
    Save,
    SaveChanges,
    after_event,
)
from pydantic import Field
from typing import TYPE_CHECKING
from telethon.types import Channel,Chat,ChatFull
from src.user import TGUser

class ChannelParent(UnionDoc):
    class Settings:
        name = "channels" 
        class_id = "_class_id"

class ChannelTypes(str, Enum):
    private = "private"
    public = "public"
    
class PublicChannel(Document):
    __type__: str = ChannelTypes.private
    id: Indexed(int, unique=True) # type: ignore
    name: str
    members: List[Link[TGUser]]
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "groups"
        union_doc = ChannelParent

class PrivateChannel(Document):
    __type__: str = ChannelTypes.public
    id: Indexed(int, unique=True) # type: ignore
    name: str
    username: str
    members: List[Link[TGUser]]
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "mega_groups"
        union_doc = ChannelParent