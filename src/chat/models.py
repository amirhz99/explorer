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
from src.user.models import TGUser

class ChatParent(UnionDoc):
    class Settings:
        name = "chats" 
        class_id = "_class_id"

class GroupTypes(str, Enum):
    private = "private"
    public = "public"
    
class Group(Document):
    __type__: str = GroupTypes.private
    _id: Indexed(int, unique=True) # type: ignore
    name: str
    members: List[Link[TGUser]]
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "groups"
        union_doc = ChatParent

class MegaGroup(Document):
    __type__: str = GroupTypes.public
    _id: Indexed(int, unique=True) # type: ignore
    name: str
    username: str
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "mega_groups"
        union_doc = ChatParent