from datetime import datetime 
import logging
import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler

from tasks.plug_controller import PlugController
from tasks.collector import Collector
from types_classes import PlugType
from tasks.updater import Updater
from tasks.checker import Checker
from interfaces.task import Task

class Master(Task):
    
    def __init__(self, id, db, fcm, additional:BlockingScheduler):
        self.db = db
        self.fcm = fcm
        self.scheduler = additional
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.logger = logging.getLogger(__name__)   
       
    def _add_jobs(self, user:dict, type:PlugType):
        # plug_controller = PlugController(self.loop, user, type)
        # tuya_job = Collector(user['id'], self.db, self.fcm, plug_controller)
        
        checker_job = Checker(user['id'], self.db, self.fcm)
        # updater_job = Updater()
        
        # self.scheduler.add_job(tuya_job.run, id=f'collector_{user["id"]}', name=f'collector_{user["id"]}',
                                # trigger='interval', minutes=1, coalesce=False, max_instances=1)
        self.scheduler.add_job(checker_job.run, id=f'checker_{user["id"]}', name=f'checker_{user["id"]}',
                                    trigger='date', run_date=datetime.now()) #trigger='cron', hour=0, minute=0
        # self.scheduler.add_job(updater_job.run, id=f'updater_{user["id"]}', name=id=f'updater_{user["id"]}'
                                    # trigger='date') #trigger='cron', hour=0, minute=0     
                
    def run(self):
        users = self.db.get_docs('Users', projection={
                                'email': 1, 'cloud_password': 1, 'tuya': 1, 
                                'is_deleted': 1, 'appliances.cloud_id': 1})
        self.logger.info('done retrieving users')
        
        for user in users:
            id = str(user["_id"])
            if not self.scheduler.get_job(f'pow_{id}') and not user['is_deleted']:
                if user['tuya']: 
                    u = {'id': id, 'dev1': user['appliances'][0]['cloud_id']}
                    type = PlugType.TUYA
                else:
                    continue
                    u = {'id': id, 'email': user['email']}
                    type = PlugType.MEROSS
                self._add_jobs(u, type) 
                break         
            elif user['is_deleted']:
                self.scheduler.remove_job(f'collector_{id}')
                self.scheduler.remove_job(f'checker_{id}')
                self.scheduler.remove_job(f'updater_{id}')
                
        self.logger.info('done checking users')
                
        
    
