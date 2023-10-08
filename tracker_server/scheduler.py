from multiprocessing import cpu_count
from datetime import datetime
import logging
import asyncio
import os

log_file = f'tracker_server/logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
logging.basicConfig(filename=log_file, level=logging.INFO,  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.external_dependencies.mongo import Mongo
from app.external_dependencies.fcm import FCM
from app.tasks.master import Master

 


class Scheduler():
    
    def __init__(self, url, db_name, cred):    
        self.db = Mongo(url, db_name)
        self.fcm = FCM(cred, self.db)
        self.logger = logging.getLogger(__name__)  
        num_cores = cpu_count()    
        executors = {
            'default': ThreadPoolExecutor(num_cores),
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
        }
        self.scheduler = BlockingScheduler(job_defaults, executors=executors)

       
    def run(self):
        master_job = Master('', self.db, self.fcm, self.scheduler)
        self.scheduler.add_job(master_job.run, id='Master', name='Master', trigger='interval', minutes=1, next_run_time=datetime.now())
        try:
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            asyncio.get_event_loop().stop()
            self.logger.info('program terminated gracefully')
  
def main(): 
    load_dotenv(os.path.join('tracker_server', '.secrets', '.env'))
    URL = os.getenv('DB_URL')
    CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 

    main_scheduler = Scheduler(URL, 'hemsproject', CRED)
    main_scheduler.run()             
    
main()