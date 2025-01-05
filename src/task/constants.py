from enum import Enum
from typing import Dict, Union
from pydantic import BaseModel

class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]

class ExploreErrorCode(str, Enum):
    NOT_FOUND = "Not found"
    