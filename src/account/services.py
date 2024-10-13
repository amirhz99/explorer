from telethon import TelegramClient
from src.account.models import TGAccount
# from telethon.sync import TelegramClient
from telethon.sessions import StringSession

async def start_telegram_client(account: TGAccount) -> TelegramClient:
    client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"Account {account.tg_id} is not authorized. Please log in again.")
        await client.disconnect()
        return None

    print(f"Account {account.tg_id} connected to Telegram successfully.")
    return client



# Convert session file to session string using the provided method
async def convert_session_to_string(session_path: str, api_id: int, api_hash: str) -> str:
    client = TelegramClient(session_path, api_id=api_id, api_hash=api_hash)
    async with client:
        return StringSession.save(client.session)
