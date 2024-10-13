from datetime import datetime
from beanie import Link
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from src.account.services import start_telegram_client
from src.account.models import TGAccount
from src.explore.models import Explore, OperationsStatus, Search
from src.chat.services import insert_chat_data
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from src.user.services import insert_bot_data, insert_user_data
from beanie.operators import Push

api_id = 2040
api_hash = "b18441a1ff607e10a989891a5462e627"
client = TelegramClient("sessions/60103274631", api_id, api_hash)

async def search_chats(task: Explore, account: TGAccount, client: TelegramClient):  # noqa: F811
    
    query = task.text

    # Perform search in Telegram
    search_results = await client(SearchRequest(q=query, limit=10000))

    # Iterate over search results (users, bots)
    for user in search_results.users:
        
        full_user = (await client(GetFullUserRequest(user))).full_user
        
        # If the user is a bot, insert bot data
        if user.bot:
            tg_bot = await insert_bot_data(user, full_user)
            await task.update(Push({Explore.results: tg_bot}))
        else:
            tg_user = await insert_user_data(user,full_user)
            await task.update(Push({Explore.results: tg_user}))


    # Iterate over search results (groups, channels)
    for chat in search_results.chats:
        
        if task.is_primary:
            await task.fetch_link('search')
            for text in task.search.secondaries:
                new_text = (chat.title).replace(task.text,text)
                new_task = Explore(
                    search=task.search,
                    text=new_text,
                    status=OperationsStatus.pending,
                )
                await new_task.insert()
                
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
    
    task = await Explore.find(
        Explore.status == OperationsStatus.pending,
        {"accounts": {"$nin": [account.id]}},  # Ensure account.id is not in accounts
        {"in_progress": {"$nin": [account.id]}},  # Ensure account.id is not in in_progress
        {
            "$expr": {  # Compare length of in_progress with accounts_count
                "$lt": [{"$size": "$in_progress"}, "$accounts_count"]
            }
        },
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

            if len(task.accounts) >= task.accounts_count or len(task.accounts) == all_accounts_count:
                task.status = OperationsStatus.completed
                print(f"Task {task.text} completed by {account.tg_id}.")
            
            await task.save_changes()

        except Exception as e:
            task.status = OperationsStatus.failed
            task.in_progress.remove(account)
            task.updated_at = datetime.now()
            await task.save_changes()
            print(f"Task failed for account {account.tg_id}: {str(e)}")

            

    await client.disconnect()
        
