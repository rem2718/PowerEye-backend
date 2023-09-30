from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from datetime import datetime, timedelta
from interfaces.task import Task
from bson import ObjectId
import logging
class Meross(Task):
    DAY = timedelta(hours=20)
    MIN = timedelta(hours=20)
    
    def __init__(self, user):
        self.user_id = user['id']
        self.email = user['email']
        self.password = user['password']
        self.prev = datetime.now()
        self.ts = datetime.now()
       
        
    @classmethod
    def set_deps(cls, db, fcm):
        cls.db = db
        cls.fcm = fcm
      
        
    async def login(self):
        try:
            self.client = await MerossHttpClient.async_from_user_password(email=self.email, password=self.password)
            self.manager = MerossManager(http_client=self.client)
        except:
            self.fcm.notify(self.user_id, 'creds')
            logging.error('meross login error', exc_info=True)
       
        
    async def _update_creds(self): 
        try:
            self.manager.close()
            await self.client.async_logout()  
        except:
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
                self.fcm.notify(self.user_id, 'disconnection', {'app_name': dev.name})
                print(f'device {dev.name} is offline')
            return on_off, connection_status
        except Exception:
            logging.error('status error', exc_info=True)
            return None, None         


    async def _one_reading(self, dev):
        try:
            reading = await dev.async_get_instant_metrics(timeout=5)
            return reading.power
        except:
            logging.error('power error', exc_info=True)
            return None


    async def _meross_init(self):
        self.app_map = self._get_appliances(self.user_id)
        await self._daily_update_creds()    
        await self.manager.async_init()
        await self.manager.async_device_discovery()
        meross_devices = self.manager.find_devices(device_type="mss310")
        logging.info(f'{len(meross_devices)} devices')
        apps = [elem[0] for elem in self.app_map.values()]
        return meross_devices, apps
    
    
    def _save_data(self, doc, updates):
        doc['user'] = ObjectId(self.user_id)
        doc['timestamp'] = self.ts 
        Meross.db.insert_doc('Powers', doc)
        Meross.db.update_appliances('Users', self.user_id, updates)  
        logging.info(f'meross: {self.ts} done') 
        self.ts += timedelta(minutes=1)
            
            
    async def run(self):
        try:
            doc = {}
            updates = []
            meross_devices, apps = self._meross_init()
            
            for dev in meross_devices:
                try:
                    id = self.app_map[str(dev.uuid)][0] 
                except:
                    continue
                apps.remove(id)
                on_off, connection_status = await self._get_status(dev)   
                doc[id] = await self._one_reading(dev)
                energy = self._to_energy(self.app_map[str(dev.uuid)][1], doc[id])
                updates.append((id, {'status': on_off,
                                    'connection_status': connection_status,
                                    'energy': energy}))
            for app in apps:
                updates.append((app, {'connection_status': False})) 
                self.fcm.notify(self.user_id, 'disconnection', {'app_name': dev.name})
                # get dev name
        except:
            self.fcm.notify(self.user_id, 'creds')
            logging.error('meross error', exc_info=True)
            await self._update_creds() 
            
        self._save_data(doc, updates)
            

            
                    
    


