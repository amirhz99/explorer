from enum import Enum
from typing import Dict, Union
from fastapi import HTTPException,status
from pydantic import BaseModel

class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]


class ErrorCodeReasonModel(BaseModel):
    code: str
    reason: str


class MessageErrorCode(str, Enum):
    MESSAGE_NOT_FOUND = "Message with this id not found"

