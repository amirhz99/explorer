from src.account.models import TGAccount
from src.account.services import AccountManager
from src.task.models import Task
from src.task.services import TaskManager


async def process_account(account: TGAccount):
    """
    Processes tasks for a single account using AccountManager and TaskManager.
    """
    account_manager = AccountManager(account)

    try:
        # Connect the account
        client = await account_manager.connect()
        if not client:
            return  # Skip if the account failed to connect

        # Process tasks for this account
        task_manager = TaskManager(account_manager)
        while True:
            task = await task_manager.pick_pending_task()
            if not task:
                print(f"No pending tasks for account {account.tg_id}.")
                break

            await task_manager.process_task(task)

    except Exception as e:
        print(f"Error while processing account {account.tg_id}: {str(e)}")
    finally:
        # Disconnect the account
        await account_manager.disconnect()
