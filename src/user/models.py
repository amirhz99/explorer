from datetime import datetime
from beanie import (
    Document,
    Indexed,
    Link,
    Insert,
    Replace,
    Save,
    SaveChanges,
    after_event,
)
from pydantic import Field


class TGUser(Document):
    _id: Indexed(int, unique=True)  # type: ignore
    first_name: str
    last_name: str | None
    username: str | None
    bio: str | None
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "tg_users"
