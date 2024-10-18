from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Union,TYPE_CHECKING
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
from pydantic import Field,BaseModel
from typing import TYPE_CHECKING
from src.chat.models import TGChat
from src.account.models import TGAccount
from src.user.models import TGBot, TGUser

if TYPE_CHECKING:
    from src.search.models import Search


class OperationsStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"
    failed = "failed"


class OperationType(str, Enum):
    search = "SEARCH"
    get_participants = "GET_PARTICIPANTS"
    get_pinned_messages = "GET_PINNED_MESSAGES"
    get_link_messages = "GET_LINK_MESSAGES"
    
                         
class Explore(Document):
    request: Link["Search"] = None
    target: str|int
    operation: OperationType = OperationType.search
    status: OperationsStatus = OperationsStatus.pending
    accounts_count: int | None = 1
    priority: int = 1
    is_primary: bool = False
    assigned_accounts: List[Link["TGAccount"]] = []
    completed_accounts: List[Link["TGAccount"]] = []
    processing_accounts: List[Link["TGAccount"]] = []
    results: List[Link[TGChat]|Link[TGUser]|Link[TGBot]] = []
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "explores"
        is_root = True
        use_state_management = True

        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()
            

async def reset_in_process_tasks():
    # Find all tasks that are still pending and have accounts in 'processing_accounts'
    tasks = await Explore.find(
        Explore.status == OperationsStatus.pending,
        {"$where": "this.processing_accounts.length > 0"}
    ).to_list()

    # Clean up the in_progress list for each task
    for task in tasks:
        print(
            f"Recovering task {task.target} - clearing processing_accounts accounts: {task.processing_accounts}"
        )
        task.processing_accounts.clear()  # Remove all processing_accounts accounts

        # Optionally, log a retry action or take any further actions for these tasks
        await task.save_changes()  # Save the updated task to the database

    print(f"Recovery complete. Cleared processing_accounts accounts for {len(tasks)} tasks.")
