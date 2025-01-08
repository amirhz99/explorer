# from __future__ import annotations
from pydantic import Field,BaseModel
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, TYPE_CHECKING
from beanie import (
    Document,
    Link,
    Update,
    before_event,
)

if TYPE_CHECKING:
    from src.account.models import TGAccount
    from src.chat.models import TGChat
    from src.user.models import TGBot, TGUser
    from src.search.models import Search


class TaskStatus(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"
    failed = "failed"


class TaskType(str, Enum):
    search = "SEARCH"
    get_participants = "GET_PARTICIPANTS"
    get_pinned_messages = "GET_PINNED_MESSAGES"
    get_link_messages = "GET_LINK_MESSAGES"


class Task(Document):
    """
    Represents a generic task in the system, such as search or participant retrieval.
    """
    request: Link["Search"] = None
    target: str | int
    task_type: TaskType = TaskType.search
    status: TaskStatus = TaskStatus.pending
    accounts_count: int | None = 1
    priority: int = 1
    parent_task: Optional[Link["Task"]] = None
    level: int = 1
    assigned_accounts: List[Link["TGAccount"]] = []
    completed_accounts: List[Link["TGAccount"]] = []
    processing_accounts: List[Link["TGAccount"]] = []
    results: List[Link["TGChat"] | Link["TGUser"] | Link["TGBot"]] = []
    is_active: bool = True
    updated_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "tasks"
        is_root = True
        use_state_management = True

    @before_event(Update)
    def update_time(self):
        """
        Automatically update the `updated_at` timestamp whenever a task is modified.
        """
        self.updated_at = datetime.now()

    async def mark_completed(self):
        """
        Mark the task as completed if all accounts have processed it.
        """
        all_accounts_count = await TGAccount.find(TGAccount.is_active == True).count()
        if (
            len(self.completed_accounts) >= self.accounts_count
            or len(self.completed_accounts) == all_accounts_count
        ):
            self.status = TaskStatus.completed
            await self.save_changes()

    async def assign_account(self, account: "TGAccount"):
        """
        Assign an account to the task and move it to the processing list.
        """
        if account not in self.assigned_accounts:
            self.assigned_accounts.append(account)
        if account not in self.processing_accounts:
            self.processing_accounts.append(account)
        await self.save_changes()

    async def complete_account(self, account: "TGAccount"):
        """
        Mark an account as having completed this task.
        """
        if account in self.processing_accounts:
            self.processing_accounts.remove(account)
        if account not in self.completed_accounts:
            self.completed_accounts.append(account)
        await self.mark_completed()
        await self.save_changes()

    async def reset_processing_accounts(self):
        """
        Reset all accounts currently marked as processing this task.
        """
        if self.processing_accounts:
            self.processing_accounts.clear()
            self.status = TaskStatus.pending
            await self.save_changes()


    @staticmethod
    async def reset_in_process_tasks():
        """
        Resets tasks stuck in the `in_process` state by clearing `processing_accounts`.
        """
        tasks = await Task.find(
            Task.status == TaskStatus.in_process,
            {"$where": "this.processing_accounts.length > 0"}
        ).to_list()

        for task in tasks:
            print(f"Recovering task {task.target}. Clearing processing accounts: {task.processing_accounts}")
            await task.reset_processing_accounts()

        print(f"Recovery complete. Cleared processing accounts for {len(tasks)} tasks.")
