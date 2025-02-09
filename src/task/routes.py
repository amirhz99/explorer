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
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.search.models import Search, SearchStatus
from src.task.models import Task, TaskStatus, TaskType
from src.task.schemas import MonitorTaskResponse, RetryTasksRequest, RetryTasksResponse  # Import your Task model

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


# @task_router.get("/tasks", response_model=List[Task])
# async def list_tasks(
#     skip: int = Query(0, description="Number of tasks to skip"),
#     limit: int = Query(10, description="Max number of tasks to return"),
# ):
#     """
#     List all tasks with pagination.
#     """
#     tasks = await Task.find().skip(skip).limit(limit).to_list()
#     return tasks
@task_router.get("/", response_model=List[Task])
async def get_tasks(
    task_type: Optional[TaskType] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    accounts_count: Optional[int] = Query(None),
    assigned_accounts: Optional[List[PydanticObjectId]] = Query(None),
    search_id: Optional[PydanticObjectId] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Retrieve tasks with filters, including pagination.
    - Use search_id to filter tasks by Search ID.
    - Pagination parameters: `skip` and `limit`.
    """
    filters = {}
    
    if task_type:
        filters["task_type"] = task_type
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority
    if is_active is not None:
        filters["is_active"] = is_active
    if created_after:
        filters["created_at"] = {"$gte": created_after}
    if created_before:
        filters.setdefault("created_at", {}).update({"$lte": created_before})
    if accounts_count:
        filters["accounts_count"] = accounts_count
    if assigned_accounts:
        filters["assigned_accounts"] = {"$in": assigned_accounts}
    if search_id:
        filters["request"] = search_id  # Use the search_id to filter by `request` field
    
    # Fetch tasks from the database with filters, skip, and limit
    tasks = await Task.find(filters).skip(skip).limit(limit).to_list()
    
    # Handle empty results
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found matching the criteria.")
    
    return tasks
@task_router.post("/", response_model=Task)
async def create_task(task: Task):
    """
    Create a new task.
    """
    await task.insert()
    return task


@task_router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Retrieve a task by its ID.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@task_router.put("/{task_id}", response_model=Task)
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


@task_router.delete("/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task by its ID.
    """
    task = await Task.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await task.delete()
    return {"message": "Task deleted successfully"}



@task_router.post("/retry")
async def retry_tasks(request: RetryTasksRequest):
    """
    Retry tasks by changing their status to 'pending'.
    Update the `Search` status to `in_process` for all affected searches.
    """
    try:
        # Build query for filtering tasks
        query = {"status": request.status}
        if request.search_id is not None:
            query["target"] = request.search_id

        # Find tasks matching the query
        tasks = await Task.find(query).to_list()

        if not tasks:
            raise HTTPException(status_code=404, detail="No tasks found matching the criteria.")

        # Update task status and gather search IDs
        updated_count = 0
        search_ids = set()
        for task in tasks:
            task.status = TaskStatus.pending
            task.updated_at = datetime.now()
            task.processing_accounts = []  # Clear processing accounts
            await task.save()
            updated_count += 1
            if task.request:  # Ensure it's an ID
                search_ids.add(task.request)

        # Update the status of all related searches
        updated_searches = 0
        for search_id in search_ids:
            search = await Search.find_one({"_id": search_id})
            if search and search.status != SearchStatus.in_process:
                search.status = SearchStatus.in_process
                await search.save()
                updated_searches += 1

        return RetryTasksResponse(
            message="Tasks and related searches successfully updated.",
            updated_task_count=updated_count,
            updated_searches=updated_searches,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")