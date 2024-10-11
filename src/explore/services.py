from datetime import datetime
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
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Chat, Channel
from src.account.models import TGAccount
from explore.models import Explore, OperationsStatus
from explore.services import search_chats
from src.chat.services import insert_chat_data
from src.chat.models import TGChat
from src.user.models import TGBot, TGUser
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    UserStatusOnline,
    UserStatusOffline,
    UserStatusRecently,
    UserStatusLastWeek,
    UserStatusLastMonth,
)
from telethon import functions
from src.task import scheduler


from src.user.services import insert_bot_data, insert_user_data

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
client = TelegramClient("sessions/60103274631", api_id, api_hash)

async def search_chats(task: Explore, account: TGAccount, client: TelegramClient):  # noqa: F811
    
    query = task.search

    # Perform search in Telegram
    search_results = await client(SearchRequest(q=query, limit=10000))

    # Iterate over search results (users, bots)
    for user in search_results.users:
        
        full_user = (await client(GetFullUserRequest(user))).full_user
        
        # If the user is a bot, insert bot data
        if user.bot:
            await insert_bot_data(user, full_user)
        else:
            await insert_user_data(user,full_user)


    # Iterate over search results (groups, channels)
    for chat in search_results.chats:

        full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
        
        await insert_chat_data(chat,full_chat)

        linked_chat_id = getattr(full_chat, "linked_chat_id", None)
        if linked_chat_id:
            pass

        # deactivated = getattr(chat, 'deactivated', None)
        migrated_to = getattr(chat, "migrated_to", None)
        if migrated_to:
            pass

        can_view_participants = getattr(chat, "can_view_participants", False)
        if can_view_participants:
            async for participant in client.iter_participants(chat):
                pass


async def start_telegram_client(account: TGAccount) -> TelegramClient:
    client = TelegramClient(account.session, account.api_id, account.api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"Account {account.tg_id} is not authorized. Please log in again.")
        await client.disconnect()
        return None

    print(f"Account {account.tg_id} connected to Telegram successfully.")
    return client

async def pick_pending_task_for_account(account: TGAccount):
    task = await Explore.find(
        Explore.status == OperationsStatus.pending,
        Explore.accounts.ne(account.id),
        Explore.in_progress.size.lt(Explore.repeat_time),
        Explore.in_progress.ne(account.id)
    ).sort("created_at").first_or_none()

    return task

async def process_task_for_account(account: TGAccount):
    client = await start_telegram_client(account)
    if client is None:
        print(f"Failed to connect TGAccount {account.tg_id}. Skipping task processing.")
        return

    while True:
        task = await pick_pending_task_for_account(account)

        if not task:
            print(f"No pending tasks left for account {account.tg_id}.")
            break
        
        try:
            task.in_progress.append(account)
            task.updated_at = datetime.now()
            await task.save_changes()
            print(f"Processing task {task.text} for account {account.tg_id}...")
            
        
            await search_chats(task, account, client)

            task.accounts.append(account)
            task.in_progress.remove(account)
            task.updated_at = datetime.now()

            all_accounts_count = await TGAccount.find(TGAccount.is_active == True).count() # noqa: E712

            if len(task.accounts) >= task.repeat_time or len(task.accounts) == all_accounts_count:
                task.status = OperationsStatus.completed
                print(f"Task {task.text} completed by {account.tg_id}.")
            
            await task.save_changes()

        except Exception as e:
            task.status = OperationsStatus.failed
            task.in_progress.remove(account)
            task.updated_at = datetime.now()
            await task.save()
            print(f"Task failed for account {account.tg_id}: {str(e)}")

            

    await client.disconnect()
        
@scheduler.scheduled_job("interval", seconds=5)
async def schedule_jobs_for_accounts():
    accounts = await TGAccount.find(TGAccount.is_active == True).to_list()  # noqa: E712

    for account in accounts:
        job_id = f"job_for_{account.id}"
        if scheduler.get_job(job_id) is None:
            scheduler.add_job(
                process_task_for_account,
                args=[account],
                id=job_id,
                replace_existing=False
            )