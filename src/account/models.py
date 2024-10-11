from __future__ import annotations
from datetime import datetime
from beanie import Document, Link
from pydantic import Field

class TGAccount(Document):
    tg_id: int  # Telegram account ID
    session: str  # The session string required by Telethon (session file name)
    api_id: int  # API ID for Telethon
    api_hash: str  # API Hash for Telethon
    json: str| None = None  # Additional account configuration in JSON
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    class Settings:
        name = "tg_accounts"