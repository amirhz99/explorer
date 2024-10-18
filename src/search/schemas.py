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
    username: Optional[str]
    usernames: Optional[List[str]]
    participants_count: Optional[int]
    creation_date: Optional[datetime]
    level: Optional[int]
    emoji_status: Optional[int]
    forum: Optional[bool] = False
    linked_chat_id: Optional[int]
    verified: bool
    source: Optional[str] = None


class TGUserResponse(BaseModel):
    tg_id: int
    type: str = "user"
    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]
    usernames: Optional[List[str]]
    phone: Optional[str]
    premium: bool
    emoji_status: Optional[int]
    status: Optional[str]
    was_online: Optional[datetime]
    birthday: Optional[datetime]
    contact_require_premium: bool = False
    personal_channel_id: Optional[int]
    personal_channel_message: Optional[str]
    business_location: Optional[str]
    business_work_hours: Optional[str]
    verified: bool
    source: Optional[str] = None


class TGBotResponse(BaseModel):
    tg_id: int
    type: str = "bot"
    first_name: Optional[str]
    last_name: Optional[str]
    about: Optional[str]
    username: Optional[str]
    bot_active_users: Optional[int]
    description: Optional[str]
    verified: bool
    source: Optional[str] = None


class Pagination(BaseModel):
    data: List[TGChatResponse | TGUserResponse | TGBotResponse]
    page: int
    limit: int
    total_count: int
    total_pages: int
    next_page: Optional[int] = None
    previous_page: Optional[int] = None


class SearchRequest(BaseModel):
    primary: str
    secondaries: Optional[List[str]] = []  
    real_time: bool = False
    accounts_count: Optional[int] = 1
