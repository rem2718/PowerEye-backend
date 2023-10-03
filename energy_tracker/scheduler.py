from multiprocessing import cpu_count
from datetime import datetime
import logging
import asyncio
import os

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from external_dependencies.mongo import Mongo
from external_dependencies.fcm import FCM
from tasks.master import Master

class Scheduler():
    
    def __init__(self, url, db_name, cred):    
        self.db = Mongo(url, db_name)
        self.fcm = FCM(cred, self.db)
        self.logger = logging.getLogger(__name__)          
        
    def _init_schedulers(self):
        num_cores = cpu_count()    
        executors = {
            'default': ThreadPoolExecutor(num_cores),
            'processpool': ProcessPoolExecutor(num_cores/2),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
        }
        self.scheduler = BlockingScheduler(job_defaults, executors=executors)
       
    def run(self):
        self._init_schedulers()
        master_job = Master('', self.db, self.fcm)
        self.scheduler.add_job(master_job.run, id='Master', args=[self.scheduler], trigger='interval', minutes=1, next_run_time=datetime.now())

        try:
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            asyncio.get_event_loop().stop()
            self.logger.info('program terminated gracefully')
  
  
load_dotenv(os.path.join('.secrets', '.env'))
URL = os.getenv('DB_URL')
CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 

main_scheduler = Scheduler(URL, 'hemsproject', CRED)
main_scheduler.run()             