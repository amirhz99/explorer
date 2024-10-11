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
    after_event,
)
from pydantic import Field
from typing import TYPE_CHECKING

class OperationsStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    done = "done"
    cancel = "cancel"

class Search(Document):
    primary: str
    secondary: List[str]
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "searches"

class Explore(Document):
    search: Link[Search]
    text: str
    status: OperationsStatus.pending
    accounts: Union[int|List[str]]  # Can be int or list of account names
    use_all_accounts: bool = False
    is_primary: bool = False
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "explores"
    