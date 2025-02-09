# File: response_models.py
from pydantic import BaseModel, Field
from typing import Any, List, Optional, TypeVar, Generic
from datetime import datetime
from enum import Enum
from src.task.models import TaskStatus, TaskType

class TaskFilter(BaseModel):
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    accounts_count: Optional[int] = None
    assigned_accounts: Optional[List[str]] = None

# Monitor Task Response Model
class MonitorTaskResponse(BaseModel):
    id: str
    task_type: str
    status: str
    assigned_accounts: int
    completed_accounts: int
    processing_accounts: int
    is_active: bool
    updated_at: datetime
    
    
class RetryTasksRequest(BaseModel):
    status: TaskStatus
    search_id: Optional[int] = None

class RetryTasksResponse(BaseModel):
    message: str
    updated_task_count: int
    updated_searches: int