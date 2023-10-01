from datetime import datetime, timedelta
from interfaces.task import Task
from dotenv import load_dotenv
import tinytuya
import logging
import os
class Tuya(Task):
    load_dotenv(os.path.join('.secrets', '.env'))
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    MIN = timedelta(minutes=1)

    def __init__(self, user_id, dev1):
        self.user_id = user_id
        self.cloud = self._login(dev1)
        self.ts = datetime.now()
    
        
    @classmethod
    def set_deps(cls, db, fcm):
        cls.db = db
        cls.fcm = fcm
        
        
    def _login(self, dev1):
        cloud = tinytuya.Cloud(apiRegion="eu", apiKey=Tuya.API_KEY,
                apiSecret=Tuya.API_SECRET, apiDeviceID=dev1)
        return cloud
    
         
    def _get_appliances(self, id):
        map = {}
        appliances = Tuya.db.get_doc('Users', {'_id': id}, 
                        {'appliances._id': 1, 'appliances.meross_id': 1, 
                         'appliances.energy': 1, 'appliances.is_deleted': 1})
        appliances = appliances['appliances']
        for app in appliances:
            if not app['is_deleted']:
                map[app['meross_id']] = {'id':str(app['_id']), 'energy':app['energy']}
        self.app_map = map
    
    
    def _get_status(self, dev):
        result = self.cloud.getstatus(dev['id'])
        pow = (result['result'][4]['value']) /10.0
        on_off = result['result'][0]['value']
        return on_off, pow
    
    
    def _to_energy(self, prev_energy, power):
        return prev_energy + (power * 1/60) / 1000
    
    
    def _save_data(self, doc, updates):
        doc['user'] = self.user_id
        doc['timestamp'] = self.ts 
        Tuya.db.insert_doc('Test', doc)
        Tuya.db.update_appliances('Users', str(self.user_id), updates) 
        logging.info(f'meross: {self.ts} done')  
        self.ts += Tuya.MIN
        
        
    def run(self): 
        doc = {}
        updates = []
        self._get_appliances(self.user_id)
        devices = self.cloud.getdevices()
        for dev in devices:
            try:
                id = self.app_map[dev['id']]['id']  
            except:
                continue
            connection_status = self.cloud.getconnectstatus(dev['id'])
            if connection_status:
                on_off, pow = self._get_status(dev)
                doc[id] = pow
                energy = self._to_energy(self.app_map[dev['id']]['energy'], doc[id])
                updates.append((id, {'status': on_off,
                                    'connection_status': connection_status,
                                    'energy': energy}))
            else:
                updates.append((id, {'connection_status': connection_status}))
                Tuya.fcm.notify(self.user_id, 'disconnection', {'app_name': dev['name']})
                
        self._save_data(doc, updates)   

        