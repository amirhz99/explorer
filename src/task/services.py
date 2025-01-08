# from datetime import datetime, timedelta, timezone
# from beanie import Link
# from telethon import TelegramClient
# from telethon.tl.functions.contacts import SearchRequest
# from src.task.utils import generate_words_from_title, pre_characters, unique_list
# from src.account.services import start_telegram_client
# from src.account.models import TGAccount
# from src.task.models import Explore, OperationsStatus, OperationType
# from src.search.models import Search
# from src.chat.services import insert_chat_data
# from telethon.tl.functions.channels import GetFullChannelRequest
# from telethon.tl.functions.users import GetFullUserRequest
# from telethon.errors import FloodWaitError
# from src.user.services import insert_bot_data, insert_user_data
# from beanie.operators import Push
# from beanie import PydanticObjectId
# import asyncio
# from traceback import print_exc

# async def create_explore_task(request: PydanticObjectId | Search, query: str = None):

#     if isinstance(request, PydanticObjectId):
#         request = await Search.get(request)
#         if not request:
#             return

#     if query and query not in request.primary:
#         is_primary = False
#         texts = generate_words_from_title(
#             query, request.primary, use_pre_characters=False
#         )
#     else:
#         is_primary = True
#         seconderies = unique_list(request.secondaries)
#         primeries_texts = [
#             f"{request.primary.strip().lower()} {character}".strip().lower()
#             for character in pre_characters
#         ]
#         seconderies_texts = [
#             f"{request.primary.strip().lower()} {text} {character}".strip().lower()
#             for character in pre_characters
#             for text in seconderies
#         ]
#         texts = primeries_texts + seconderies_texts

#     for text in texts:
#         explore = await Explore.find_one(
#             Explore.request.id == request.id, Explore.target == text
#         )
#         if explore:
#             continue

#         new_task = Explore(
#             request=request,
#             target=text,
#             status=OperationsStatus.pending,
#             is_primary=is_primary,
#         )
#         await new_task.insert()


# async def explore_search(task: Explore, client: TelegramClient):

#     query = task.target
#     search_results = await client(SearchRequest(q=query, limit=10000))

#     for user in search_results.users:

#         full_user = (await client(GetFullUserRequest(user))).full_user
#         if user.bot:
#             tg_bot = await insert_bot_data(user, full_user)
#             await task.update(Push({Explore.results: tg_bot}))
#         else:
#             tg_user = await insert_user_data(user, full_user)
#             await task.update(Push({Explore.results: tg_user}))

#     for chat in search_results.chats:

#         if task.is_primary:
#             await task.fetch_link("request")
#             await create_explore_task(request=task.request, query=chat.title)

#         full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
#         tg_chat = await insert_chat_data(chat, full_chat)
#         await task.update(Push({Explore.results: tg_chat}))

#         linked_chat_id = getattr(full_chat, "linked_chat_id", None)
#         if linked_chat_id:
#             linked_chat = await client.get_entity(linked_chat_id)
#             linked_full_chat = (
#                 await client(GetFullChannelRequest(channel=linked_chat))
#             ).full_chat
#             tg_chat = await insert_chat_data(linked_chat, linked_full_chat)
#             await task.update(Push({Explore.results: tg_chat}))

#         # deactivated = getattr(chat, 'deactivated', None)
#         migrated_to = getattr(chat, "migrated_to", None)
#         if migrated_to:
#             migrated_to_chat = await client.get_entity(migrated_to)
#             migrated_to_full_chat = (
#                 await client(GetFullChannelRequest(channel=migrated_to_chat))
#             ).full_chat
#             tg_chat = await insert_chat_data(migrated_to_chat, migrated_to_full_chat)
#             await task.update(Push({Explore.results: tg_chat}))

#         # can_view_participants = getattr(chat, "can_view_participants", False)
#         # if can_view_participants:
#         #     async for participant in client.iter_participants(chat):
#         #         pass


# async def pick_pending_task_for_account(account: TGAccount):

#     current_time = datetime.now()

#     def is_operation_blocked(operation_type: OperationType) -> bool:
#         # Safely fetch end time from flood_wait or return None
#         end_time = (account.flood_wait or {}).get(operation_type.value)

#         if not end_time:
#             return False

#         return current_time > end_time

#     # Fetch all pending tasks sorted by creation date
#     tasks_cursor = Explore.find(
#         Explore.status == OperationsStatus.pending,
#         {"completed_accounts": {"$nin": [account]}},
#         {"processing_accounts": {"$nin": [account]}},
#         {"$expr": {"$lt": [{"$size": "$processing_accounts"}, "$accounts_count"]}},
#     ).sort("created_at")

#     async for task in tasks_cursor:
#         if not is_operation_blocked(task.operation):
#             return task  # Return the first eligible task
#         break

#     return None

# async def process_task_for_account(account: TGAccount):

#     task = await pick_pending_task_for_account(account)
#     if not task:
#         print(f"No pending tasks left for account {account.tg_id}.")
#         return

#     client = await start_telegram_client(account)
#     if client is None:
#         print(f"Failed to connect TGAccount {account.tg_id}. Skipping task processing.")
#         return

#     while task and client:

#         try:
#             task.processing_accounts.append(account)
#             await task.save_changes()
#             print(f"Processing task {task.target} for account {account.tg_id}...")

#             await asyncio.sleep(3)

#             match task.operation:
#                 case OperationType.search:
#                     await explore_search(task, client)
#                 case _:
#                     print("Operation Type Error")

#             task.completed_accounts.append(account)

#             all_accounts_count = await TGAccount.find(
#                 TGAccount.is_active == True
#             ).count()

#             if (
#                 len(task.completed_accounts) >= task.accounts_count
#                 or len(task.completed_accounts) == all_accounts_count
#             ):
#                 task.status = OperationsStatus.completed
#                 print(f"Task {task.target} completed by {account.tg_id}.")


#         except FloodWaitError as e:
#             task.status = OperationsStatus.failed
#             account.flood_wait[task.operation.value] = datetime.now() + timedelta(
#                 seconds=e.seconds
#             )
#             await account.save_changes()
#             print(f"Task failed for account {account.tg_id}: {str(e)}")

#         except Exception as e:
#             print(f"Task failed for account {account.tg_id}: {str(e)}")
#             print_exc()
#             task.status = OperationsStatus.failed
#             print(f"Task failed for account {account.tg_id}: {str(e)}")

#         finally:
#             if account in task.processing_accounts:
#                 task.processing_accounts.remove(account)
#             else:
#                 print(f"Account {account} not in processing_accounts, skipping removal.")

#             await task.save_changes()
#             task = await pick_pending_task_for_account(account)

#     await client.disconnect()

from datetime import datetime
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import FloodWaitError
from beanie.operators import Push
from src.search.models import Search
from src.account.services import AccountManager
from src.task.models import Task, TaskStatus, TaskType
from src.task.utils import (
    generate_words_from_title,
    characters,
    genrate_words_with_characters,
    unique_list,
)
from src.chat.services import insert_chat_data
from src.user.services import insert_bot_data, insert_user_data


class TaskManager:
    """
    Class to manage task-related operations, including picking and processing tasks.
    """

    def __init__(self, account_manager: "AccountManager"):
        self.account_manager = account_manager

    async def pick_pending_task(self) -> Task | None:
        """
        Picks the next pending task for the associated account.
        """

        def is_task_eligible(task: Task) -> bool:
            return not self.account_manager.is_operation_blocked(task.task_type)

        tasks_cursor = Task.find(
            Task.status == TaskStatus.pending,
            {"completed_accounts": {"$nin": [self.account_manager.account]}},
            {"processing_accounts": {"$nin": [self.account_manager.account]}},
            {"$expr": {"$lt": [{"$size": "$processing_accounts"}, "$accounts_count"]}},
        ).sort("created_at")

        async for task in tasks_cursor:
            if is_task_eligible(task):
                return task

        return None

    async def process_task(self, task: Task):
        """
        Processes the given task for the account.
        """
        try:
            await task.assign_account(self.account_manager.account)
            print(
                f"Processing task {task.target} for account {self.account_manager.account.tg_id}..."
            )

            match task.task_type:
                case TaskType.search:
                    await self._process_search_task(task)
                case _:
                    raise NotImplementedError(
                        f"Task type {task.task_type} is not supported."
                    )

            await task.complete_account(self.account_manager.account)

        except FloodWaitError as e:
            task.status = TaskStatus.failed
            await self.account_manager.handle_flood_wait(task.task_type, e.seconds)

        except Exception as e:
            task.status = TaskStatus.failed
            print(f"Error processing task {task.id}: {str(e)}")

        finally:
            await task.save_changes()
            search = await Search.get(task.search_id)  # Assuming Task has a `search_id` field
            if not search:
                # logger.error(f"Search {task.search_id} not found for task {task.id}.")
                return

            pending_tasks_count = await Task.find(
                {"search_id": task.search_id, "status": {"$ne": TaskStatus.completed}}
            ).count()

            if pending_tasks_count == 0:
                await search.mark_as_completed()
                # logger.info(f"Search {search.id} marked as completed.")

    async def _process_search_task(self, task: Task):
        """
        Handles the `search` task type.
        """
        query = task.target
        client = self.account_manager.client
        search_results = await client(SearchRequest(q=query, limit=10000))

        for user in search_results.users:
            full_user = (await client(GetFullUserRequest(user))).full_user
            if user.bot:
                tg_bot = await insert_bot_data(user, full_user)
                await task.update(Push({Task.results: tg_bot}))
            else:
                tg_user = await insert_user_data(user, full_user)
                await task.update(Push({Task.results: tg_user}))

        for chat in search_results.chats:
            await task.fetch_link("request")
            await self.create_sub_tasks(task, chat.title)

            full_chat = (await client(GetFullChannelRequest(channel=chat))).full_chat
            tg_chat = await insert_chat_data(chat, full_chat)
            await task.update(Push({Task.results: tg_chat}))

    @staticmethod
    async def create_sub_tasks(task: Task, query: str):
        """
        Creates subtasks for search results.
        """

        current_level = task.level + 1
        if current_level > task.request.depth:
            return

        texts = []

        texts.extend(generate_words_from_title(query, task.request.primary))
        
        if task.level == 0:
            texts.extend(genrate_words_with_characters(task.target))
            
        elif task.level == 1:
            texts.extend(genrate_words_with_characters(task.target))
            texts.extend(generate_words_from_title(query, task.target))

        for text in texts:
            existing_task = await Task.find_one(
                Task.target == text,
                # Task.request.id == task.request.id,
            )
            if not existing_task:
                new_task = Task(
                    request=task.request,
                    target=text,
                    parent_task=task,
                    level=current_level,
                    task_type=TaskType.search,
                    status=TaskStatus.pending,
                )
                await new_task.insert()

    @staticmethod
    async def create_secondary_tasks(task: Task):
        """
        Recursively create secondary tasks based on the depth parameter.
        """

        seconderies = unique_list(task.request.secondaries)
        seconderies_texts = [
            f"{task.target.strip().lower()} {text}".strip().lower()
            for text in seconderies
        ]

        for text in seconderies_texts:
            existing_task = await Task.find_one(
                Task.request.id == task.request.id, Task.target == text
            )
            if not existing_task:
                secondary_task = Task(
                    request=task.request,
                    target=text,
                    task_type=task.task_type,
                    status=TaskStatus.pending,
                    accounts_count=1,
                    priority=task.priority,
                    parent_task=task,
                    level=1,  # Incremented level
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                await secondary_task.insert()

    @staticmethod
    async def create_primary_task(search: Search) -> Task:
        """
        Create the primary task (level 0) for the search request.
        """
        primary_task = Task(
            request=search,
            target=search.primary,
            task_type=TaskType.search,
            status=TaskStatus.pending,
            accounts_count=1,
            priority=1,
            level=0,  # Primary task level
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        await primary_task.insert()

        return primary_task
