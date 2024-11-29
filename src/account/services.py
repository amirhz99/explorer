from telethon import TelegramClient
from src.account.models import TGAccount
# from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import rpcerrorlist

async def start_telegram_client(account: TGAccount) -> TelegramClient:
    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    
    try:
        await client.connect()
    except rpcerrorlist.AuthKeyDuplicatedError:
        print(f"Account {account.tg_id} is not authorized. Please log in again.")
        await client.disconnect()
        account.is_active = False
        await account.save()
        return None
    
    if not await client.is_user_authorized():
        print(f"Account {account.tg_id} is not authorized. Please log in again.")
        await client.disconnect()
        account.is_active = False
        await account.save()
        return None

    print(f"Account {account.tg_id} connected to Telegram successfully.")
    
    account_info = await client.get_me()
    
    is_updated = True
    
    if not account.tg_id:
        account.tg_id = account_info.id
        is_updated = False
    if account.first_name != account_info.first_name:
        account.first_name = account_info.first_name
        is_updated = False
    if account.last_name != account_info.last_name:
        account.last_name = account_info.last_name
        is_updated = False
    if account.username != account_info.username:
        account.username = account_info.username
        is_updated = False
    if account.phone_number != account_info.phone:
        account.phone_number = account_info.phone
        is_updated = False
        
    if not is_updated:
        await account.save_changes()
        
    return client



# Convert session file to session string using the provided method
async def convert_session_to_string(session_path: str, api_id: int, api_hash: str) -> str:
    client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash)
    async with client:
        return StringSession.save(client.session)
