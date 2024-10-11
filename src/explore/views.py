import asyncio
from datetime import datetime
from typing import Any, Dict
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
from src.explore.services import search_chats
from src.task import scheduler

explore_router = APIRouter()


accounts_data: Dict[str, Dict[str, Any]] = {
    "account1": {"in_use": False, "lock": asyncio.Lock()},
    "account2": {"in_use": False, "lock": asyncio.Lock()},
    "account3": {"in_use": False, "lock": asyncio.Lock()},
}
account_semaphore = asyncio.Semaphore(3)
# async with account_semaphore():

async def process_task(task_id):
    task = await Explore.get(task_id)
    if not task or task.status != OperationsStatus.pending:
        return

    task.status = OperationsStatus.in_process
    task.updated_at = datetime.now()
    await task.save_changes()

    search_tasks = []

    

    available_accounts = [
        name for name, data in accounts_data.items() if not data["in_use"]
    ]

    selected_accounts = []

    if isinstance(task.accounts, int):
        if task.use_all_accounts:
            accounts_to_use = min(task.accounts, len(accounts_data))
            selected_accounts = [name for name, data in accounts_data.items()][
                :accounts_to_use
            ]
        else:
            accounts_to_use = min(task.accounts, len(available_accounts))
            selected_accounts = available_accounts[:accounts_to_use]
    else:
        selected_accounts = task.accounts

    if not selected_accounts:
        print(
            "No available accounts to process the task. Marking task as pending again."
        )
        task.status = OperationsStatus.pending
        await task.save_changes()
        return

    for account_name in selected_accounts:
        async with accounts_data[account_name]["lock"]:

            accounts_data[account_name]["in_use"] = True

            try:
                search_tasks.append(search_chats(account_name, task.text))
            except Exception as e:
                print(f"Error processing with account {account_name}: {e}")
            finally:
                accounts_data[account_name]["in_use"] = False

    await asyncio.gather(*search_tasks)

    task.status = OperationsStatus.done
    task.updated_at = datetime.now()
    await task.save_changes()


@scheduler.scheduled_job("interval", seconds=5)
async def scheduler_job():
    pending_tasks = (
        await Explore.find(Explore.status == OperationsStatus.pending)
        .sort(Explore.created_at)
        .to_list()
    )
    for task in pending_tasks:
        scheduler.add_job(process_task, args=[task.id])


async def reset_in_process_tasks():
    in_process_tasks = await Explore.find(
        Explore.status == OperationsStatus.in_process
    ).to_list()
    for task in in_process_tasks:
        task.status = OperationsStatus.pending
        await task.save()
    print("Reset all in_process tasks to pending status.")


# FastAPI routes
@explore_router.get("/")
async def search_telegram_chats(
    query: str = Query(..., description="Search term for Telegram chats"),
    accounts: int = Query(1, description="Number of accounts to use"),
    use_all: bool = Query(False, description="Use all available accounts"),
):
    task = Explore(
        text=query,
        accounts=accounts,
        use_all_accounts=use_all,
        status=OperationsStatus.pending,
    )
    await task.insert()  # Insert task into the database
    return JSONResponse(
        content={"message": "Task added to queue. Searching..."}, status_code=200
    )
