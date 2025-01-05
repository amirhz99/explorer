import redis
from rq import Queue

# Redis connection for the queues
redis_conn = redis.Redis(host='localhost', port=6379, db=0)

# Queues for different task types
explore_queue = Queue('explore_queue', connection=redis_conn)
other_task_queue = Queue('other_task_queue', connection=redis_conn)

def enqueue_task(task_type, account, task_data):
    if task_type == "search":
        explore_queue.enqueue(process_task_for_account, task_type, account, task_data)
    else:
        other_task_queue.enqueue(process_task_for_account, task_type, account, task_data)




