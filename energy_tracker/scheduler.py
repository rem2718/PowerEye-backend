from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from datetime import datetime
from master import Master
from energy import Energy
from mongo import Mongo
import multiprocessing
import asyncio
import os

load_dotenv(os.path.join('.secrets', '.env'))
URL = os.getenv('DB_URL')
db = Mongo(URL, 'hemsproject')
num_cores = multiprocessing.cpu_count()    
executors = {
    'default': ThreadPoolExecutor(num_cores),
    'processpool': ProcessPoolExecutor(num_cores/2)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 1,
}
async_scheduler = AsyncIOScheduler(job_defaults)
sync_scheduler = BlockingScheduler(executors=executors)

master_job = Master(db)
async_scheduler.add_job(master_job.run, id='Master', trigger='interval', minutes=1, next_run_time=datetime.now(), args=[async_scheduler])

energy_job = Energy(db)
sync_scheduler.add_job(energy_job.run, id='Energy_transfer', trigger='date', run_date=datetime.now()) #trigger='cron', hour=0, minute=0

try:
    async_scheduler.start()
    sync_scheduler.start()
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
