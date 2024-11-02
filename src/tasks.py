from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore  
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status
from pymongo import MongoClient
from src.explore.models import Explore, OperationsStatus
from src.explore.services import process_task_for_account
from src.account.models import TGAccount
from app.config import settings
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_SUBMITTED, EVENT_JOB_REMOVED
from datetime import datetime

jobstores = {
    # 'default': MemoryJobStore()
    'default': MongoDBJobStore(database='task_manager_db', collection='explorer_jobs', client=MongoClient(settings.MONGODB_URI))
}

scheduler = AsyncIOScheduler(jobstores=jobstores) 

running_jobs = {}

# Listener to manage running_jobs dictionary
def job_listener(event):
    job_id = event.job_id
    current_time = datetime.now()

    if event.code == EVENT_JOB_SUBMITTED:
        # Job has started, store the start time
        if job_id.startswith("job_for_"):
            running_jobs[job_id] = current_time
    elif event.code in (EVENT_JOB_EXECUTED, EVENT_JOB_ERROR):
        # Job has finished or been removed, delete from running jobs
        running_jobs.pop(job_id, None)

# Attach the listener to the scheduler
scheduler.add_listener(job_listener, EVENT_JOB_SUBMITTED | EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)



# # Add scheduled tasks, refer to the official documentation: https://apscheduler.readthedocs.io/en/master/
# # use when you want to run the job at fixed intervals of time
# @scheduler.scheduled_job('interval', seconds=5)
# def interval_task_test():
#     print('interval task is run...')
@scheduler.scheduled_job("interval", seconds=60)
async def schedule_jobs_for_accounts():
    accounts = await TGAccount.find(TGAccount.is_active == True).to_list()  # noqa: E712
    task = await Explore.find_one(Explore.status == OperationsStatus.pending,)
    if not task:
        return
    
    for account in accounts:
        
        job_id = f"job_for_{account.id}"

        # Check if job exists; skip if it does
        if scheduler.get_job(job_id) is not None:
            print(f"Job {job_id} already exists. Skipping...")
            continue

        try:
            # Add the job only if it doesn't already exist
            scheduler.add_job(
                process_task_for_account,
                args=[account],
                id=job_id,
                replace_existing=False
            )
            print(f"Job {job_id} added successfully.")
        except Exception as e:
            print(f"Failed to add job {job_id}: {e}")
            

# # use when you want to run the job periodically at certain time(s) of day
# @scheduler.scheduled_job('cron', hour=3, minute=30)
# def cron_task_test():
#     print('cron task is run...')


# # use when you want to run the job just once at a certain point of time
# @scheduler.scheduled_job('date', run_date=date(2022, 11, 11))
# def date_task_test():
#     print('date task is run...')

# scheduler.add_job(deactivate_invoice, 'date', run_date=run_time, id=f"deactivate_invoice_{str(invoice.id)}",misfire_grace_time=None,args=[invoice.id])


task_router = APIRouter()

@task_router.get('/')
async def list_jobs():
    jobs = scheduler.get_jobs()

    job_list = [{'id': job.id, 'name': job.name, 'next_run_time': str(job.next_run_time), 'trigger': str(job.trigger)} for job in jobs]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=job_list,
    )
    
    
# Route to list currently running jobs with start time
@task_router.get('/running_jobs')
async def list_running_jobs():
    running_job_list = [
        {'id': job_id, 'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S')}
        for job_id, start_time in running_jobs.items()
    ]
    return JSONResponse(status_code=status.HTTP_200_OK, content=running_job_list)

