from __future__ import annotations
from beanie import Document, Link
from src.chat import TGChat

class Account(Document):
    tg_id:int
    
    
class Action(Document):
    pass
