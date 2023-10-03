import logging
import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from plug_controller import PlugController
from tasks.collector import Collector
from types_classes import PlugType
from tasks.updater import Updater
from tasks.checker import Checker
from interfaces.task import Task

class Master(Task):
    
    def __init__(self, id, db, fcm, plug=None):
        self.db = db
        self.fcm = fcm
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.logger = logging.getLogger(__name__)   
       
    def _add_jobs(self, scheduler:BlockingScheduler, user:dict, type:PlugType):
        plug_controller = PlugController(self.loop, user.copy(), type)
        tuya_job = Collector(user['id'], self.db, self.fcm, plug_controller)
        
        # checker_job = Checker()
        # updater_job = Updater()
        
        scheduler.add_job(tuya_job.run, trigger='interval', minutes=1, 
                                     id=f'pow_{user["id"]}', coalesce=False, max_instances=1)
        # self.scheduler.add_job(checker_job.run, id=f'checker_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0
        # self.scheduler.add_job(updater_job.run, id=f'updater_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0     
                
    def run(self, scheduler:BlockingScheduler):
        
        users = self.db.get_docs('Users', projection={
                                'email': 1, 'meross_password': 1, 'tuya': 1, 
                                'is_deleted': 1, 'appliances.meross_id': 1})
        self.logger.info('done retrieving users')
        
        for user in users:
            id = str(user["_id"])
            if not scheduler.get_job(f'pow_{id}') and not user['is_deleted']:
                if user['tuya']: 
                    u = {'id': id, 'dev1': user['appliances'][0]['meross_id']}
                    type = PlugType.TUYA
                else:
                    u = {'id': id, 'email': user['email']}
                    type = PlugType.MEROSS
                self._add_jobs(scheduler, u, type)          
            elif user['is_deleted']:
                scheduler.remove_job(f'meross_{id}')
                scheduler.remove_job(f'checker_{id}')
                scheduler.remove_job(f'updater_{id}')
                
        self.logger.info('done checking users')
                
        
    
