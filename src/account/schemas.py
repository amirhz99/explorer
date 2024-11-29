from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


# Response models
class ProcessingInfo(BaseModel):
    id: PydanticObjectId
    operation: str
    status: str
    assigned_accounts: list = []
    completed_accounts: list = []
    processing_accounts: list = []

class TGAccountResponse(BaseModel):
    id: PydanticObjectId
    tg_id: Optional[int]
    session_string: str
    phone_number: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    flood_wait: Optional[Dict[str,datetime]] = {}
    is_active: bool
    updated_at: datetime
    created_at: datetime
    processing_info: List[ProcessingInfo] = []

class TGAccountListResponse(BaseModel):
    accounts: List[TGAccountResponse]
