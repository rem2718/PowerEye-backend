from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from external_dependencies.meross import Meross
from external_dependencies.tuya import Tuya
from tasks.checker import Checker
from tasks.updater import Updater
from interfaces.task import Task
import logging

class Master(Task):
    
    def __init__(self, async_scheduler:AsyncIOScheduler, sync_scheduler:BlockingScheduler):
        self.async_scheduler = async_scheduler
        self.sync_scheduler = sync_scheduler
       
        
    @classmethod
    def set_deps(cls, db, fcm):
        cls.db = db
        Meross.set_deps(db, fcm)
        Tuya.set_deps(db, fcm) 
       
       
    def _create_tuya(self, user, job_id):
        dev1 = user['appliances'][0]['meross_id']
        tuya_job = Tuya(user['_id'], dev1)
        # checker_job = Checker()
        # updater_job = Updater()
        
        self.async_scheduler.add_job(tuya_job.run, trigger='interval', minutes=1, 
                                     id=f'pow_{job_id}', coalesce=False, max_instances=1)
        # self.sync_scheduler.add_job(checker_job.run, id=f'checker_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0
        # self.sync_scheduler.add_job(updater_job.run, id=f'updater_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0     

                
    async def _create_meross(self, user, job_id):
        u = {'email':user['email'], 'password': user['meross_password'], 'id': job_id}
        meross_job = Meross(u.copy())
        await meross_job.login()
        # checker_job = Checker()
        # updater_job = Updater()
        
        self.async_scheduler.add_job(meross_job.run, trigger='interval', minutes=1,  
                                     id=f'pow_{job_id}', coalesce=False, max_instances=1)
        # self.sync_scheduler.add_job(checker_job.run, id=f'checker_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0
        # self.sync_scheduler.add_job(updater_job.run, id=f'updater_{job_id}',
        #                             trigger='date') #trigger='cron', hour=0, minute=0   
      
        
    async def run(self):
        users = Master.db.get_docs('Users', projection={
                                'email': 1, 'meross_password': 1, 'tuya': 1, 
                                'is_deleted': 1, 'appliances.meross_id': 1})
        logging.info('done retrieving users')
        
        for user in users:
            job_id = str(user["_id"])
            if not self.async_scheduler.get_job(f'pow_{job_id}') and not user['is_deleted']:
                if user['tuya']:  
                    self._create_tuya(user, job_id)
                else:
                    # await self._create_meross(user, job_id)
                    print()
                    
                   
            elif user['is_deleted']:
                self.async_scheduler.remove_job(f'meross_{job_id}')
                self.async_scheduler.remove_job(f'checker_{job_id}')
                self.async_scheduler.remove_job(f'updater_{job_id}')
                
        logging.info('done checking users')
                

            
    
