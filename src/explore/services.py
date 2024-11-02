from datetime import datetime, timedelta, timezone
from beanie import Link
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from src.explore.utils import generate_words_from_title,pre_characters, unique_list
from src.account.services import start_telegram_client
from src.account.models import TGAccount
from src.explore.models import Explore, OperationsStatus,OperationType
from src.search.models import Search
from src.chat.services import insert_chat_data
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import FloodWaitError
from src.user.services import insert_bot_data, insert_user_data
from beanie.operators import Push
from beanie import PydanticObjectId
import asyncio

async def create_explore_task(request: PydanticObjectId|Search,query:str=None):
    
    if isinstance(request,PydanticObjectId):
        request = await Search.get(request)
        if not request:
            return
    
    if query and query not in request.primary: 
        is_primary = False
        texts = generate_words_from_title(query, request.primary,use_pre_characters=False)
    else:
        is_primary = True
        seconderies = unique_list(request.secondaries)
        primeries_texts = [f'{request.primary.strip().lower()} {character}'.strip().lower() for character in pre_characters]
        seconderies_texts = [(f'{request.primary.strip().lower()} {text} {character}'.strip().lower() for character in pre_characters) for text in seconderies]
        texts = primeries_texts + seconderies_texts
        
    for text in texts:
        explore = await Explore.find_one(Explore.request.id == request.id,Explore.target == text)
        if explore:
            continue
        
        new_task = Explore(
            request=request,
            target=text,
            status=OperationsStatus.pending,
            is_primary=is_primary,
        )
        await new_task.insert()
    
async def explore_search(task: Explore, client: TelegramClient):
    
    query = task.target
    search_results = await client(SearchRequest(q=query, limit=10000))


    for user in search_results.users:
        
        full_user = (await client(GetFullUserRequest(user))).full_user
        if user.bot:
            tg_bot = await insert_bot_data(user, full_user)
            await task.update(Push({Explore.results: tg_bot}))
        else:
            tg_user = await insert_user_data(user,full_user)
            await task.update(Push({Explore.results: tg_user}))


    for chat in search_results.chats:
        
        if task.is_primary:
            await task.fetch_link('request')
            await create_explore_task(request=task.request,query=chat.title)
                
        full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
        tg_chat = await insert_chat_data(chat,full_chat)
        await task.update(Push({Explore.results: tg_chat}))

        linked_chat_id = getattr(full_chat, "linked_chat_id", None)
        if linked_chat_id:
            linked_chat = await client.get_entity(linked_chat_id)
            linked_full_chat = (await client(GetFullChannelRequest(channel=linked_chat))).full_chat
            tg_chat = await insert_chat_data(linked_chat,linked_full_chat)
            await task.update(Push({Explore.results: tg_chat}))

        # deactivated = getattr(chat, 'deactivated', None)
        migrated_to = getattr(chat, "migrated_to", None)
        if migrated_to:
            migrated_to_chat = await client.get_entity(migrated_to)
            migrated_to_full_chat = (await client(GetFullChannelRequest(channel=migrated_to_chat))).full_chat
            tg_chat = await insert_chat_data(migrated_to_chat,migrated_to_full_chat)
            await task.update(Push({Explore.results: tg_chat}))

        # can_view_participants = getattr(chat, "can_view_participants", False)
        # if can_view_participants:
        #     async for participant in client.iter_participants(chat):
        #         pass

async def pick_pending_task_for_account(account: TGAccount):
    
    current_time = datetime.now(timezone.utc)

    def is_operation_blocked(operation_type: OperationType) -> bool:
        # Safely fetch end time from flood_wait or return None
        end_time = (account.flood_wait or {}).get(operation_type.value)

        # If end_time is None or empty, the operation isn't blocked
        if not end_time:
            return False
        
        # Check if the current time is still within the flood wait period
        return current_time > end_time

    # Fetch all pending tasks sorted by creation date
    tasks_cursor = Explore.find(
        Explore.status == OperationsStatus.pending,
        {"completed_accounts": {"$nin": [account]}},
        {"processing_accounts": {"$nin": [account]}},
        {
            "$expr": {
                "$lt": [{"$size": "$processing_accounts"}, "$accounts_count"]
            }
        },
    ).sort("created_at")

    async for task in tasks_cursor:
        if not is_operation_blocked(task.operation):
            return task  # Return the first eligible task

    return None
    
    # task = await Explore.find(
    #     Explore.status == OperationsStatus.pending,
    #     {"completed_accounts": {"$nin": [account.id]}},  
    #     {"processing_accounts": {"$nin": [account.id]}},
    #     {
    #         "$expr": {
    #             "$lt": [{"$size": "$processing_accounts"}, "$accounts_count"]
    #         }
    #     },
    # ).sort("created_at").first_or_none()

    # return task

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
            task.processing_accounts.append(account)
            await task.save_changes()
            print(f"Processing task {task.target} for account {account.tg_id}...")
            
            match task.operation:
                case OperationType.search:
                    await explore_search(task, client)
                case _:
                    print("Operation Type Error")

            task.completed_accounts.append(account)
            task.processing_accounts.remove(account)

            all_accounts_count = await TGAccount.find(TGAccount.is_active == True).count()

            if len(task.completed_accounts) >= task.accounts_count or len(task.completed_accounts) == all_accounts_count:
                task.status = OperationsStatus.completed
                print(f"Task {task.target} completed by {account.tg_id}.")
            
            await task.save_changes()
            await asyncio.sleep(1)
        except FloodWaitError as e:
            task.status = OperationsStatus.failed
            task.processing_accounts.remove(account)
            await task.save_changes()
            account.flood_wait[task.operation.value] = datetime.now(timezone.utc) + timedelta(seconds=e.seconds) 
            await account.save_changes()
            print(f"Task failed for account {account.tg_id}: {str(e)}")

                        
        except Exception as e:
            task.status = OperationsStatus.failed
            task.processing_accounts.remove(account)
            await task.save_changes()
            print(f"Task failed for account {account.tg_id}: {str(e)}")

            

    await client.disconnect()
        
