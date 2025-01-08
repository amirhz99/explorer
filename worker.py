import asyncio
import logging
import os
import signal
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from src.models import initial_models
from src.task.models import Task
from src.account.models import TGAccount
from src.account.services import AccountManager
from src.task.services import TaskManager

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store accounts processed by this worker
WORKER_ID = f"worker-{os.getpid()}"

# Setup database connection
async def setup_database():
    try:
        await initial_models()
        # client = AsyncIOMotorClient("mongodb://localhost:27017")
        # await init_beanie(database=client["SocialExplorer"], document_models=[Task, TGAccount])
        logger.info("Database connection established.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def get_available_accounts(limit: int = 2):
    accounts = await TGAccount.find(
        {"is_active": True, "worker_id": None}  # Only pick accounts not assigned to any worker
    ).limit(limit).to_list()

    for account in accounts:
        account.worker_id = WORKER_ID  # Assign this worker's ID
        await account.save()

    return accounts

# Process a single account's tasks
async def process_account(account: TGAccount):
    account_manager = AccountManager(account)
    task_manager = TaskManager(account_manager)
    task = await task_manager.pick_pending_task()
    if not task:
        logger.info(f"No pending tasks for account {account.tg_id}.")
        return
    
    try:
        # Connect the account
        client = await account_manager.connect()
        if not client:
            logger.warning(f"Account {account.tg_id} failed to connect.")
            return
        
        # Process tasks for this account
        while True:
            task = await task_manager.pick_pending_task()
            if not task:
                logger.info(f"No pending tasks for account {account.tg_id}.")
                break

            await task_manager.process_task(task)

    except Exception as e:
        logger.error(f"Error while processing account {account.tg_id}: {e}")
    finally:
        # Disconnect the account and release it
        await account_manager.disconnect()
        account.worker_id = None  # Reset the worker_id
        await account.save()

# Worker logic
async def worker_logic():
    await setup_database()

    try:
        while True:
            try:
                # Fetch 1-2 available accounts
                available_accounts = await get_available_accounts(limit=2)
                if not available_accounts:
                    await asyncio.sleep(1)  # Wait if no accounts are available
                    continue

                # Process each account asynchronously
                tasks = [
                    asyncio.create_task(process_account(account))
                    for account in available_accounts
                ]
                await asyncio.gather(*tasks)  # Wait for all account tasks to complete
                await asyncio.sleep(0.1)  # Prevent busy looping
                
            except asyncio.CancelledError:
                    logger.info("Worker logic received cancellation request. Exiting loop.")
                    break
            
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(5)  # Backoff in case of repeated errors
    finally:
        logger.info("Worker loop exited. Performing final cleanup...")

# Graceful shutdown handler
async def shutdown(signal, loop):
    logger.info(f"Received exit signal {signal.name}. Shutting down gracefully...")
    
    # Cancel all running tasks except the current one
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    logger.info("Cancelled all running tasks.")

    # Wait for all tasks to finish
    # try:
    #     # Wait for tasks to complete with a timeout
    #     await asyncio.gather(*tasks, return_exceptions=True)
    # except Exception as e:
    #     logger.error(f"Error during task cleanup: {e}")
        
    # Reset `worker_id` for this worker's accounts
    logger.info(f"Resetting accounts assigned to {WORKER_ID}...")
    worker_account_ids = await TGAccount.find({"worker_id": WORKER_ID}).project(TGAccount.id).to_list()

    if worker_account_ids:
        # Remove accounts from `processing_accounts` in tasks
        await Task.find({"processing_accounts": {"$in": worker_account_ids}}).update_many(
            {"$pull": {"processing_accounts": {"$in": worker_account_ids}}}
        )
        logger.info(f"Removed accounts from processing in tasks: {worker_account_ids}")

        # Reset `worker_id` in TGAccount
        await TGAccount.find({"worker_id": WORKER_ID}).update_many(
            {"$set": {"worker_id": None}}
        )
        logger.info(f"Reset worker_id for accounts: {worker_account_ids}")

    # Stop the event loop
    loop.stop()
    logger.info("Shutdown complete.")

# Worker entry point
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    signals = (signal.SIGINT, signal.SIGTERM)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))
    loop.run_until_complete(worker_logic())