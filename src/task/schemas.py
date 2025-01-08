# File: response_models.py
from pydantic import BaseModel, Field
from typing import Any, List, Optional, TypeVar, Generic
from datetime import datetime


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