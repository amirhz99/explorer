from __future__ import annotations
from beanie import Document, Link
from src.chat import TGChat

class Message(Document):
    id:int
    chat:Link[TGChat]
