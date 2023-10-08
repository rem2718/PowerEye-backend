from datetime import datetime, timedelta
from bson import ObjectId
import logging

from tasks.plug_controller import PlugController
from types_classes import NotifType
from interfaces.task import Task

class Collector(Task):
    min = timedelta(minutes=1)
    
    def __init__(self, id, db, fcm, additional:PlugController):
        self.user_id = id
        self.db = db 
        self.fcm = fcm
        self.cloud = additional
        self.ts = datetime.now()
        self.notified = False
        self.flags = {}
        self.logger = logging.getLogger(__name__)    
    
    def _get_appliances(self, id):
        map = {}
        appliances = self.db.get_doc('Users', 
                        {'_id': ObjectId(id)}, {'appliances._id': 1, 
                        'appliances.cloud_id': 1, 'appliances.is_deleted': 1,
                        'appliances.energy': 1, 'appliances.name': 1})
        appliances = appliances['appliances']
        for app in appliances:
            if not app['is_deleted']:
                map[app['cloud_id']] = {
                    'id': str(app['_id']), 
                    'name': app['name'], 
                    'energy': app['energy']
                    }
        return map  

    def _to_energy(self, prev_energy, power):
        return prev_energy + (power * 1/60) / 1000
    
    def _check_disconnected(self, id, name, connection_status):
        if not connection_status:
            if id not in self.flags or self.flags[id]:
                self.fcm.notify(self.user_id, NotifType.DISCONNECTION, {'app_name': name})
                self.flags[id] = False
        else:
            self.flags[id] = True          

    def _notify_disconnected(self, apps_ids, app_map, updates):
        for cloud_id in apps_ids:
            id = app_map[cloud_id]['id']
            if id not in self.flags or self.flags[id]:
                updates.append((cloud_id, {'connection_status': False})) 
                name = app_map[cloud_id]['name']
                self.fcm.notify(self.user_id, NotifType.DISCONNECTION, {'app_name': name})
                self.flags[id] = False
            
    def _get_doc_updates(self, cloud_devices, app_map):
        doc = {}
        updates = [] 
        apps_ids = list(app_map.keys())
        for dev in cloud_devices:
            dev_id = self.cloud.get_id(dev)
            if dev_id not in app_map:
                continue 
            apps_ids.remove(dev_id)
            id = app_map[dev_id]['id']
            on_off, connection_status, power = self.cloud.get_info(dev)     
            doc[id] = power
            energy = self._to_energy(app_map[dev_id]['energy'], doc[id]) 
            update = (id, {'status': on_off, 'connection_status': connection_status, 'energy': energy})
            updates.append(update) 
            self._check_disconnected(id, app_map[dev_id]['name'], connection_status)   
        self._notify_disconnected(apps_ids, app_map, updates)
        return doc, updates
       
    def _save_data(self, doc, updates):
        doc['user'] = ObjectId(self.user_id)
        doc['timestamp'] = self.ts 
        self.db.insert_doc('Test', doc)
        self.db.update_appliances('Users', self.user_id, updates)  
        self.logger.critical(f'cloud: {self.ts} -> done') 
        self.ts += Collector.min

    def run(self):
        try:  
            user = self.db.get_doc('Users', {'_id': ObjectId(self.user_id)}, {'cloud_password':1}) 
            if self.cloud.login(user['cloud_password']):
                self.notified = False 
                app_map = self._get_appliances(self.user_id)
                if len(app_map):
                    cloud_devices = self.cloud.get_devices()
                    doc, updates = self._get_doc_updates(cloud_devices, app_map)
                    self._save_data(doc, updates)
            elif not self.notified:
                self.fcm.notify(self.user_id, NotifType.CREDS)
                self.notified = True
        except:
            self.logger.error('cloud error', exc_info=True)
            self.cloud.update_creds() 