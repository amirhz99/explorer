from __future__ import annotations
from beanie import Document, Link
from src.chat.models import Group,MegaGroup
from src.channel import PrivateChannel,PublicChannel

class Message(Document):
    id:int
    chat:Link[Group|MegaGroup|PrivateChannel|PublicChannel]
