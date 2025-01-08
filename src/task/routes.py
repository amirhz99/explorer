import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
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
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.task.models import Task
from src.task.schemas import MonitorTaskResponse  # Import your Task model

task_router = APIRouter()


@task_router.get("/monitor/{task_id}", response_model=MonitorTaskResponse)
async def monitor_task(task_id: str):
    """
    Monitor a specific task by ID, providing a summary of its current status.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return MonitorTaskResponse(
        id=str(task.id),
        task_type=task.task_type.value,
        status=task.status.value,
        assigned_accounts=len(task.assigned_accounts),
        completed_accounts=len(task.completed_accounts),
        processing_accounts=len(task.processing_accounts),
        is_active=task.is_active,
        updated_at=task.updated_at,
    )


@task_router.get("/tasks", response_model=List[Task])
async def list_tasks(
    skip: int = Query(0, description="Number of tasks to skip"),
    limit: int = Query(10, description="Max number of tasks to return"),
):
    """
    List all tasks with pagination.
    """
    tasks = await Task.find().skip(skip).limit(limit).to_list()
    return tasks


@task_router.post("/tasks", response_model=Task)
async def create_task(task: Task):
    """
    Create a new task.
    """
    await task.insert()
    return task


@task_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Retrieve a task by its ID.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: Task):
    """
    Update a task by its ID.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_data = task_update.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(task, key, value)

    await task.save()
    return task


@task_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task by its ID.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await task.delete()
    return {"message": "Task deleted successfully"}
