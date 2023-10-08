from multiprocessing import cpu_count
from datetime import datetime
import logging
import asyncio
import os

# Define the log file path with the current timestamp
log_file = f'tracker_server/logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
# Configure the logging module
logging.basicConfig(filename=log_file, level=logging.INFO,  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.external_dependencies.mongo import Mongo
from app.external_dependencies.fcm import FCM
from app.tasks.master import Master

 


class Scheduler():
    """
    A scheduler for managing tasks in the tracker server.
    This class initializes and runs a scheduler that manages tasks using the `APScheduler` library.
    Attributes:
        db (Mongo): An instance of the Mongo database connection.
        fcm (FCM): An instance of the Firebase Cloud Messaging (FCM) service.
        logger (logging.Logger): The logger for logging messages.
        scheduler (BlockingScheduler): The scheduler for managing tasks.
    """
    
    def __init__(self, url, db_name, cred): 
        """
        Constructor for the Scheduler class.

        Args:
            url (str): The URL of the database.
            db_name (str): The name of the database.
            cred (str): The credentials for Firebase Cloud Messaging (FCM).
        """   
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
        """
        Run the scheduler and add the Master job.
        This method initializes the Master job and starts the scheduler, handling potential exceptions.
        """
        master_job = Master('', self.db, self.fcm, self.scheduler)
        self.scheduler.add_job(master_job.run, id='Master', name='Master', trigger='interval', minutes=1,
                               next_run_time=datetime.now())
        try:
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            asyncio.get_event_loop().stop()
            self.logger.critical('program terminated gracefully')
  
def main():
    """
    Main function for starting the scheduler.
    This function loads environment variables, initializes the Scheduler instance, and runs the scheduler.
    """ 
    load_dotenv(os.path.join('tracker_server', '.secrets', '.env'))
    URL = os.getenv('DB_URL')
    CRED = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 

    main_scheduler = Scheduler(URL, 'hemsproject', CRED)
    main_scheduler.run()             
    
main()