# File: response_models.py
from pydantic import BaseModel, Field
from typing import Any, List, Optional, TypeVar, Generic
from datetime import datetime

class TaskSummary(BaseModel):
    completed: int
    failed: int
    in_process: int
    pending: int

class SearchStatusResponse(BaseModel):
    search_id: str
    status: str
    completed_percentage: float
    total_tasks: int
    tasks_summary: TaskSummary
    
class TGChatResponse(BaseModel):
    tg_id: int
    type: str
    title: str
    about: Optional[str]
    chat_type: str
    username: Optional[str]
    participants_count: Optional[int]
    verified: bool
    scam: bool
    broadcast: bool
    source: Optional[str] = None

class TGUserResponse(BaseModel):
    tg_id: int
    type: str = "user"
    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]
    phone: Optional[str]
    premium: bool
    verified: bool
    scam: bool
    restricted: bool
    source: Optional[str] = None

class TGBotResponse(BaseModel):
    tg_id: int
    type: str = "bot"
    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]
    verified: bool
    description: Optional[str]
    source: Optional[str] = None

class Pagination(BaseModel):
    data: List[TGChatResponse|TGUserResponse|TGBotResponse]
    page: int
    limit: int
    total_count: int
    total_pages: int
    next_page: Optional[int] = None
    previous_page: Optional[int] = None