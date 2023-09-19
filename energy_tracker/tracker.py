from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from tuya import get_pow
import multiprocessing

num_cores = multiprocessing.cpu_count()    
executors = {
    'default': ThreadPoolExecutor(num_cores),
    'processpool': ProcessPoolExecutor(num_cores/2)
}
scheduler = BlockingScheduler(executors=executors)

scheduler.add_job(get_pow, 'interval', minutes=1)
# scheduler.add_job(insert_into_db, 'interval', args= ,minutes=1)

try:
    # init()
    scheduler.start()
except KeyboardInterrupt:
    scheduler.shutdown()