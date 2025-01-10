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
    accounts = (
        await TGAccount.find(
            {
                "is_active": True,
                "worker_id": None,
            },  # Only pick accounts not assigned to any worker
            fetch_links=True,
        )
        .limit(limit)
        .to_list()
    )

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

        # Ensure all tasks are completed before performing shutdown cleanup
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error during final cleanup: {e}")

        # Final cleanup logic for the worker
        await cleanup_worker()


async def cleanup_worker():
    logger.info(f"Resetting accounts assigned to {WORKER_ID}...")

    # Find accounts assigned to this worker
    worker_account_ids = await TGAccount.find({"worker_id": WORKER_ID}).to_list()
    if worker_account_ids:

        # Extract only the id from each account document
        account_ids = [account.id for account in worker_account_ids]

        # Remove these accounts from `processing_accounts` in tasks
        await Task.find({"processing_accounts": {"$in": account_ids}}).update_many(
            {"$pull": {"processing_accounts": {"$in": account_ids}}}
        )
        logger.info(f"Removed accounts from processing in tasks: {account_ids}")

        # Reset `worker_id` in TGAccount
        await TGAccount.find({"worker_id": WORKER_ID}).update_many(
            {"$set": {"worker_id": None}}
        )
        logger.info(f"Reset worker_id for accounts: {account_ids}")


# Graceful shutdown handler
async def shutdown(signal, loop):
    logger.info(f"Received exit signal {signal.name}. Shutting down gracefully...")

    # Cancel all running tasks except the current one
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    logger.info(f"Cancelled {len(tasks)} running tasks.")

    # Wait for all tasks to finish
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All tasks finished.")
    except asyncio.CancelledError:
        logger.info("Some tasks were forcefully cancelled.")
    except Exception as e:
        logger.error(f"Error during task completion: {e}")

    # Perform final cleanup (reset `worker_id`, `processing_accounts`, etc.)
    await cleanup_worker()

    # Stop the event loop only after cleanup is complete
    loop.stop()
    logger.info("Shutdown complete.")


# Main entry point to handle shutdown signals
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    signals = (signal.SIGINT, signal.SIGTERM)

    # Setup shutdown signal handlers
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    # Start the worker logic
    loop.run_until_complete(worker_logic())
