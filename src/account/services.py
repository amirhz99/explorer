# from telethon import TelegramClient
# from src.account.models import TGAccount
# # from telethon.sync import TelegramClient
# from telethon.sessions import StringSession
# from telethon.errors import rpcerrorlist

# async def start_telegram_client(account: TGAccount) -> TelegramClient:
#     client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    
#     try:
#         await client.connect()
#     except rpcerrorlist.AuthKeyDuplicatedError:
#         print(f"Account {account.tg_id} is not authorized. Please log in again.")
#         await client.disconnect()
#         account.is_active = False
#         await account.save()
#         return None
    
#     if not await client.is_user_authorized():
#         print(f"Account {account.tg_id} is not authorized. Please log in again.")
#         await client.disconnect()
#         account.is_active = False
#         await account.save()
#         return None

#     print(f"Account {account.tg_id} connected to Telegram successfully.")
    
#     account_info = await client.get_me()
    
#     is_updated = True
    
#     if not account.tg_id:
#         account.tg_id = account_info.id
#         is_updated = False
#     if account.first_name != account_info.first_name:
#         account.first_name = account_info.first_name
#         is_updated = False
#     if account.last_name != account_info.last_name:
#         account.last_name = account_info.last_name
#         is_updated = False
#     if account.username != account_info.username:
#         account.username = account_info.username
#         is_updated = False
#     if account.phone_number != account_info.phone:
#         account.phone_number = account_info.phone
#         is_updated = False
        
#     if not is_updated:
#         await account.save_changes()
        
#     return client



# # Convert session file to session string using the provided method
# async def convert_session_to_string(session_path: str, api_id: int, api_hash: str) -> str:
#     client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash)
#     async with client:
#         return StringSession.save(client.session)



from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import AuthKeyDuplicatedError
from src.account.models import TGAccount


class AccountManager:
    """
    Class to manage account-related operations, including connecting to Telegram, updating account info,
    and handling session conversions.
    """
    def __init__(self, account: TGAccount):
        self.account = account
        self.client: TelegramClient | None = None

    async def connect(self) -> TelegramClient:
        """
        Starts and connects the Telegram client for the account.
        """
        self.client = TelegramClient(
            StringSession(self.account.session_string),
            self.account.api_id,
            self.account.api_hash
        )

        try:
            await self.client.connect()
        except AuthKeyDuplicatedError:
            print(f"Account {self.account.tg_id} is not authorized. Please log in again.")
            await self._deactivate_account()
            return None

        if not await self.client.is_user_authorized():
            print(f"Account {self.account.tg_id} is not authorized. Please log in again.")
            await self._deactivate_account()
            return None

        print(f"Account {self.account.tg_id} connected to Telegram successfully.")
        await self._update_account_info()
        return self.client

    async def disconnect(self):
        """
        Disconnects the Telegram client.
        """
        if self.client:
            await self.client.disconnect()
            print(f"Account {self.account.tg_id} disconnected from Telegram.")

    async def _deactivate_account(self):
        """
        Marks the account as inactive due to an authorization error.
        """
        self.account.is_active = False
        await self.account.save()
        if self.client:
            await self.client.disconnect()

    async def _update_account_info(self):
        """
        Updates the account information in the database based on Telegram's account data.
        """
        account_info = await self.client.get_me()
        is_updated = True

        if not self.account.tg_id:
            self.account.tg_id = account_info.id
            is_updated = False
        if self.account.first_name != account_info.first_name:
            self.account.first_name = account_info.first_name
            is_updated = False
        if self.account.last_name != account_info.last_name:
            self.account.last_name = account_info.last_name
            is_updated = False
        if self.account.username != account_info.username:
            self.account.username = account_info.username
            is_updated = False
        if self.account.phone_number != account_info.phone:
            self.account.phone_number = account_info.phone
            is_updated = False

        if not is_updated:
            await self.account.save_changes()
            print(f"Account {self.account.tg_id} information updated.")

    def is_operation_blocked(self, task_type: str) -> bool:
        """
        Checks if the account is blocked for a specific operation due to flood limits.
        """
        current_time = datetime.now()
        end_time = (self.account.flood_wait or {}).get(task_type)
        return end_time and current_time < end_time

    async def handle_flood_wait(self, task_type: str, seconds: int):
        """
        Updates the flood wait time for the account after a FloodWaitError.
        """
        self.account.flood_wait[task_type] = datetime.now() + timedelta(seconds=seconds)
        await self.account.save_changes()
        print(f"Account {self.account.tg_id} blocked for {seconds} seconds.")

    @staticmethod
    async def convert_session_to_string(session_path: str, api_id: int, api_hash: str) -> str:
        """
        Converts a session file to a session string.
        """
        async with TelegramClient(session_path, api_id=api_id, api_hash=api_hash) as client:
            return StringSession.save(client.session)
