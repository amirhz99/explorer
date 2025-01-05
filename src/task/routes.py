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
from src.task.models import Explore, OperationsStatus

from fastapi import APIRouter, JSONResponse, status
from apscheduler.schedulers.asyncio import AsyncIOScheduler

task_router = APIRouter()

# Route to list currently running jobs with start time
@task_router.get('/running_jobs')
async def list_running_jobs():
    running_job_list = [{'id': job_id, 'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S')} for job_id, start_time in running_jobs.items()]
    return JSONResponse(status_code=status.HTTP_200_OK, content=running_job_list)