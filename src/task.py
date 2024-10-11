from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date
from apscheduler.jobstores.mongodb import MongoDBJobStore  
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status
from pymongo import MongoClient
from app.config import settings

jobstores = {
    # 'default': MemoryJobStore()
    'default': MongoDBJobStore(database='task_manager_db', collection='jobs', client=MongoClient(settings.MONGODB_URI))
}

scheduler = AsyncIOScheduler(jobstores=jobstores) 

# # Add scheduled tasks, refer to the official documentation: https://apscheduler.readthedocs.io/en/master/
# # use when you want to run the job at fixed intervals of time
# @scheduler.scheduled_job('interval', seconds=5)
# def interval_task_test():
#     print('interval task is run...')


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