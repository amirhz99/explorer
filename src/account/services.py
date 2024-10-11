from telethon import TelegramClient
from src.account.models import TGAccount


async def start_telegram_client(account: TGAccount) -> TelegramClient:
    client = TelegramClient(account.session, account.api_id, account.api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"Account {account.tg_id} is not authorized. Please log in again.")
        await client.disconnect()
        return None

    print(f"Account {account.tg_id} connected to Telegram successfully.")
    return client