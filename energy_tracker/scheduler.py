from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from external_dependencies.mongo import Mongo
from external_dependencies.FCM import FCM
from multiprocessing import cpu_count
from tasks.master import Master
from dotenv import load_dotenv
from datetime import datetime
import logging
import asyncio
import os

class Scheduler():
    
    def __init__(self, url, db_name, cred):    
        self.db = Mongo(url, db_name)
        self.fcm = FCM(cred, self.db)  
        
        
    def _init_schedulers(self):
        num_cores = cpu_count()    
        executors = {
            'default': ThreadPoolExecutor(num_cores),
            'processpool': ProcessPoolExecutor(num_cores/2)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
        }
        self.async_scheduler = AsyncIOScheduler(job_defaults)
        self.sync_scheduler = BlockingScheduler(job_defaults, executors=executors)
       
        
    def run(self):
        self._init_schedulers()
        
        master_job = Master(self.async_scheduler, self.sync_scheduler)
        master_job.set_deps(self.db, self.fcm)
        self.async_scheduler.add_job(master_job.run, id='Master', trigger='interval',
                                     minutes=1, next_run_time=datetime.now())

        try:
            self.async_scheduler.start()
            asyncio.get_event_loop().run_forever()
            
        except (KeyboardInterrupt, SystemExit):
            self.sync_scheduler.shutdown()
            self.async_scheduler.shutdown()
            asyncio.get_event_loop().stop()
            logging.info('program terminated gracefully')
            
        except:
            logging.error('terminate error', exc_info=True)


load_dotenv(os.path.join('.secrets', '.env'))
URL = os.getenv('DB_URL')
CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 

scheduler = Scheduler(URL, 'hemsproject', CRED)
scheduler.run()
