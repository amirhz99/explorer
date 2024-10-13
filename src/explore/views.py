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
from src.explore.models import Explore, OperationsStatus, Search

explore_router = APIRouter()


@explore_router.get("/")
async def create_search(
    primary: str,
    secondaries: Optional[List[str]] = Query(
        default=[]
    ),  # Optional list with default value of empty list
    real_time: bool = False,
    accounts_count: Optional[int] = Query(1, description="Number of accounts to use"),
):
    search = Search(
        primary=primary,
        secondaries=secondaries,
        real_time=real_time,
        accounts_count=accounts_count,
    )
    await search.insert()

    if real_time:
        task = Explore(
            search=search,
            text=primary,
            accounts_count=accounts_count,
            status=OperationsStatus.pending,
            is_primary=True,
        )
        await task.insert()
    
    return JSONResponse(
        content={"message": "Searching...", "search_id": str(search.id)},
        status_code=200,
    )


@explore_router.get("/{search_id}/status")
async def get_search_status(search_id: PydanticObjectId) -> JSONResponse:
    # Fetch the Search document by ID
    search = await Search.get(search_id)
    if not search:
        raise HTTPException(status_code=404, detail="Search not found")

    # Fetch all Explore documents linked to the Search
    explores = await Explore.find(Explore.search.id == search.id).to_list()

    if not explores:
        raise HTTPException(
            status_code=404, detail="No Explore tasks found for this Search"
        )

    # Count Explore tasks based on status
    total_tasks = len(explores)
    completed_tasks = sum(
        1 for exp in explores if exp.status == OperationsStatus.completed
    )
    failed_tasks = sum(1 for exp in explores if exp.status == OperationsStatus.failed)
    in_process_tasks = sum(
        1 for exp in explores if exp.status == OperationsStatus.in_process
    )
    pending_tasks = sum(1 for exp in explores if exp.status == OperationsStatus.pending)

    # Calculate percentage of completion
    completed_percentage = (
        (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    )

    # Determine search status based on explore statuses
    if completed_tasks == total_tasks:
        search_status = OperationsStatus.completed
    elif failed_tasks == total_tasks:
        search_status = OperationsStatus.failed
    elif in_process_tasks == 0 and pending_tasks == 0:
        search_status = OperationsStatus.completed
    else:
        search_status = search.status

    search.status = search_status
    search.save_changes()

    # Prepare the response
    return JSONResponse(
        content={
            "search_id": str(search.id),
            "status": search_status,
            "completed_percentage": completed_percentage,
            "total_tasks": total_tasks,
            "tasks_summary": {
                "completed": completed_tasks,
                "failed": failed_tasks,
                "in_process": in_process_tasks,
                "pending": pending_tasks,
            },
        },
        status_code=200,
    )
