from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from datetime import datetime, timedelta
from bson import ObjectId
import asyncio
import logging
class Meross():
    db = None
    DAY = timedelta(hours=20)
    MIN = timedelta(hours=20)
    
    def __init__(self, user):
        self.user_id = user['id']
        self.email = user['email']
        self.password = user['password']
        self.app_map = None
        self.client = None
        self.manager = None
        self.prev = datetime.now()
        self.ts = datetime.now()
        
    @classmethod    
    def set_db(cls, db):
        cls.db = db
        
    async def login(self):
        try:
            self.client = await MerossHttpClient.async_from_user_password(email=self.email, password=self.password)
            self.manager = MerossManager(http_client=self.client)
        except Exception as e:
            # TO-DO: wrong creds notify()
            logging.error('meross login error', exc_info=True)
        
    async def _update_creds(self): 
        try:
            self.manager.close()
            await self.client.async_logout()  
        except Exception as e:
            logging.error('meross logout error', exc_info=True)
            
        await self.login()  
    
    async def _daily_update_creds(self):
        current = datetime.now()
        if current - self.prev >= Meross.DAY:
            await self._update_creds()
            prev += Meross.DAY
            
    def _app_map(self, appliances):
        map = {}
        for app in appliances:
            if not app['is_deleted']:
                map[app['meross_id']] = (str(app['_id']), app['energy'])
        return map 
         
    def _get_appliances(self, id):
        appliances = Meross.db.get_doc('Users', {'_id': ObjectId(id)}, 
                        {'appliances._id': 1, 'appliances.meross_id': 1, 
                         'appliances.energy': 1, 'appliances.is_deleted': 1})
        
        return self._app_map(appliances['appliances'])
        
    def _to_energy(self, prev_energy, power):
        return prev_energy + (power * 1/60) / 1000 
    
    async def _get_status(self, dev):
        try:
            await dev.async_update(timeout=2)        
            on_off = dev.is_on()
            connection_status = True if dev.online_status.value == 1 else False
            if not connection_status:
                # TO-DO: notify()
                print(f'device {dev.name} is offline')
            return on_off, connection_status
        except Exception as e:
            logging.error('status error', exc_info=True)
            return None, None         

    async def _one_reading(self, dev):
        try:
            reading = await dev.async_get_instant_metrics(timeout=5)
            return reading.power
        except Exception as e:
            logging.error('power error', exc_info=True)
            return None

    async def run(self):
        try:
            doc = {}
            updates = []
            self.app_map = self._get_appliances(self.user_id)
            await self._daily_update_creds()    
            await self.manager.async_init()
            await self.manager.async_device_discovery()
            meross_devices = self.manager.find_devices(device_type="mss310")
            logging.info(f'{len(meross_devices)} devices')
            apps = [elem[0] for elem in self.app_map.values()]
            
            for dev in meross_devices:
                try:
                    id = self.app_map[str(dev.uuid)][0] 
                except:
                    continue
                apps.remove(id)
                on_off, connection_status = await self._get_status(dev)   
                doc[id] = await self._one_reading(dev)
                updates.append((id, {'status': on_off,
                                    'connection_status': connection_status,
                                    'energy': self._to_energy(self.app_map[str(dev.uuid)][1], doc[id])}))
            for app in apps:
                updates.append((app, {'connection_status': False})) 
                # TO-DO: notify()
                # get dev name
        except Exception as e:
            # TO-DO: wrong creds
            logging.error('meross error', exc_info=True)
            await self._update_creds() 
            
        doc['user'] = ObjectId(self.user_id)
        doc['timestamp'] = self.ts 
        Meross.db.insert_doc('Test', doc)
        Meross.db.update_appliances('Users', self.user_id, updates)  
        logging.info(f'meross: {self.ts} done') 
        self.ts += timedelta(minutes=1)
            
                    
    


