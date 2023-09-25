from energy_tracker.external_dependencies.meross import Meross
from energy_tracker.external_dependencies.tuya import Tuya
import logging

class Master():
    
    def __init__(self, db):
        self.db = db
        Meross.set_db(db)
        Tuya.set_db(db)
       
    async def run(self, scheduler):
        users = self.db.get_docs('Users', projection={
                                'email': 1, 'meross_password': 1, 'tuya': 1, 
                                'is_deleted': 1, 'appliances.meross_id': 1})
        logging.info('done retrieving users')
        for user in users:
            job_id = str(user['_id'])
            if not scheduler.get_job(job_id):
                if user['tuya']:  
                    dev1 = user['appliances'][0]['meross_id']
                    tuya_job = Tuya(user['_id'], dev1)
                    scheduler.add_job(tuya_job.run, trigger='interval', minutes=1,  id=job_id, coalesce=False, max_instances=1)
                else:
                    u = {'email':user['email'], 'password': user['meross_password'], 'id': job_id}
                    meross_job = Meross(u.copy())
                    await meross_job.login()
                    scheduler.add_job(meross_job.run, trigger='interval', minutes=1,  id=job_id, coalesce=False, max_instances=1)
            elif user['is_deleted']:
                scheduler.remove_job(job_id)

            
    
