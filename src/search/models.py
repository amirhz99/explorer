from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Union
from beanie import (
    BackLink,
    Document,
    Indexed,
    Link,
    Insert,
    Replace,
    Save,
    SaveChanges,
    Update,
    after_event,
    before_event,
)
from pydantic import Field


class OperationsStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"
    failed = "failed"


class Search(Document):
    primary: str
    secondaries: List[str] = []
    real_time: bool = False
    depth: int | None = 1
    accounts_count: int | None = 1
    status: OperationsStatus = OperationsStatus.pending
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "searches"
        use_state_management = True

        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()
