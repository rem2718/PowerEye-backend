from multiprocessing import cpu_count
from datetime import datetime
import logging
import asyncio
import os

log_file = f'logs/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'
format_style = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format=format_style,
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(format_style))
logging.getLogger("").addHandler(console_handler)


from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from dotenv import load_dotenv

from app.external_dependencies.mongo import Mongo
from app.external_dependencies.fcm import FCM
from app.tasks.master import Master


class Scheduler:
    """
    A scheduler for managing tasks in the tracker server.
    This class initializes and runs a scheduler that manages tasks using the `APScheduler` library.
    Attributes:
        db (Mongo): An instance of the Mongo database connection.
        fcm (FCM): An instance of the Firebase Cloud Messaging (FCM) service.
        logger (logging.Logger): The logger for logging messages.
        scheduler (BlockingScheduler): The scheduler for managing tasks.
    """

    def __init__(self, db, fcm):
        """
        Constructor for the Scheduler class.

        Args:
            db: The database instance.
            fcm: The FCM (Firebase Cloud Messaging) instance.
        """
        self.db = db
        self.fcm = fcm
        self.logger = logging.getLogger(__name__)
        num_cores = cpu_count()
        executors = {
            "default": ThreadPoolExecutor(num_cores),
        }
        job_defaults = {
            "coalesce": True,
            "max_instances": 3,
        }
        self.scheduler = BlockingScheduler(job_defaults, executors=executors)

    def run(self):
        """
        Run the scheduler and add the Master job.
        This method initializes the Master job and starts the scheduler, handling potential exceptions.
        """
        master_job = Master("", self.db, self.fcm, self.scheduler)
        self.scheduler.add_job(
            master_job.run,
            id="Master",
            name="Master",
            trigger="interval",
            minutes=1,
            next_run_time=datetime.now(),
        )
        try:
            self.scheduler.start()

        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            asyncio.get_event_loop().stop()
            self.logger.critical("program terminated gracefully")


def main():
    """
    Main function for starting the scheduler.
    This function loads environment variables, initializes the Scheduler instance, and runs the scheduler.
    """
    load_dotenv(os.path.join(".secrets", ".env"))
    URL = os.getenv("DB_URL")
    CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if os.getenv("ENV") == "PRODUCTION":
        database_name = "hemsproject"
    else:
        database_name = "test"
    db = Mongo(URL, database_name)
    fcm = FCM(CRED, db)
    main_scheduler = Scheduler(db, fcm)
    main_scheduler.run()


if __name__ == "__main__":
    main()
