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
from typing import TYPE_CHECKING
from src.chat.models import TGChat
from src.account.models import TGAccount
from src.user.models import TGBot, TGUser


class OperationsStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"
    failed = "failed"

class Search(Document):
    primary: str
    secondaries: List[str] = []
    real_time: bool = False
    repeat_time: int | None = 1
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

        # @after_event(Insert)
        # async def create_base_explore(self):
        #     if self.real_time:
        #         task = Explore(
        #             search=self,
        #             text=self.primary,
        #             accounts_count=self.accounts_count,
        #             status=OperationsStatus.pending,
        #             is_primary=True,
        #         )
        #         await task.insert()
                
class Explore(Document):
    search: Link[Search]
    text: str
    status: OperationsStatus = OperationsStatus.pending
    accounts_count: int | None = 1
    is_primary: bool = False
    accounts: List[Link[TGAccount]]  = []  # Completed TGAccount references
    in_progress: List[Link[TGAccount]] = []
    results: List[Link[TGChat]|Link[TGUser]|Link[TGBot]] = []
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "explores"
        use_state_management = True

        @before_event(Update)
        def update_time(self):
            self.updated_at = datetime.now()
            

async def reset_in_process_tasks():
    # Find all tasks that are still pending and have accounts in 'in_progress'
    tasks = await Explore.find(
        Explore.status == OperationsStatus.pending,
        {"$where": "this.in_progress.length > 0"}
    ).to_list()

    # Clean up the in_progress list for each task
    for task in tasks:
        print(
            f"Recovering task {task.text} - clearing in-progress accounts: {task.in_progress}"
        )
        task.in_progress.clear()  # Remove all in-progress accounts

        # Optionally, log a retry action or take any further actions for these tasks
        await task.save_changes()  # Save the updated task to the database

    print(f"Recovery complete. Cleared in-progress accounts for {len(tasks)} tasks.")
