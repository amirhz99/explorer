import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from beanie import PydanticObjectId
from starlette.responses import JSONResponse
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
    UploadFile,
)
from src.explore.models import Explore, OperationsStatus

explore_router = APIRouter()