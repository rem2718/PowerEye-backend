from enum import Enum
import asyncio
import os
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import tinytuya
from app.models.appliance_model import PlugType
from flask import session
from dotenv import load_dotenv


load_dotenv(os.path.join('.secrets', '.env'))
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

class PlugType(Enum):
    MEROSS = 1
    TUYA = 2

class Cloud_interface():
    # user for meross: {'id':_ , 'email':_, 'password':_}
    # user for tuya: {'id':_ , 'dev1':_}
    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.loop = event_loop
        self.session = {}  # Initialize the session dictionary
    
    def _run_async(self, async_func):
        return self.loop.run_until_complete(async_func())
    
    def verify_credentials(self, type, user):
        match type:
            case PlugType.MEROSS.value: return self._run_async(lambda: Meross.verify_credentials(user, session))
            case PlugType.TUYA.value: return Tuya.verify_credentials(user, self.session)
        
    def  get_smartplugs(self, type, user):
        match type:
            case PlugType.MEROSS.value: return self._run_async(lambda: Meross.get_smartplugs(user))
            case PlugType.TUYA: return Tuya.get_smartplugs(user, session)
 
    def switch(self, type, user, app_id, status):    
        match type:
            case PlugType.MEROSS.value: return self._run_async(lambda: Meross.switch(user, app_id, status))
            case PlugType.TUYA.value: return Tuya.switch(user, app_id, status)   
 
        
class Meross():
    
    @staticmethod
    async def verify_credentials(user, session):
        try:
            id = user['id']
            client = await MerossHttpClient.async_from_user_password(user['email'], user['password'])
            session[id]['token'] = client.cloud_credentials.token
            session[id]['key'] = client.cloud_credentials.key
            session[id]['issued_on'] = client.cloud_credentials.issued_on
            return True
        except Exception as e:
            print('Login failed:', str(e))
            return False

    @staticmethod
    async def get_smartplugs(user):
        try:
            id = user['id']
            client = await MerossHttpClient.async_from_cloud_creds(MerossCloudCreds(session[id]['token'], session[id]['key'], session[id]['issued_on']))
            manager = MerossManager(http_client=client)
            await manager.async_init()
            await manager.async_device_discovery()
            meross_devices = manager.find_devices(device_type="mss310")
            appliances = [{'id': str(dev.uuid), 'name': dev.name} for dev in meross_devices]
            return appliances
        except: 
            Meross.verify_credentials(user)
            return None

    @staticmethod
    async def switch(user, app_id, status):
        try:
            id = user['id']
            client = await MerossHttpClient.async_from_cloud_creds(MerossCloudCreds(session[id]['token'], session[id]['key'], session[id]['issued_on']))
            manager = MerossManager(http_client=client)
            await manager.async_init()
            await manager.async_device_discovery()
            [dev] = manager.find_devices(device_uuids=[app_id])
            if status:
                await dev.async_turn_on(channel=0)
            else:
                await dev.async_turn_off(channel=0)  
            return True  
        except: 
            Meross.verify_credentials(user)
            return None
            
class Tuya():
    # tuya dont require any email or password, it just needs any device id
    # one trick we can do here it just replacing the passwords of ward and qater, with the first device id
    @staticmethod
    def verify_credentials(user, session): 
        try:
            id = user['id']
            # Create a new session for the user if it doesn't exist
            if id not in session:
                session[id] = {}  
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                    apiSecret=API_SECRET, apiDeviceID=user['dev1'])
            session[id]['token'] = cloud._gettoken()
            return True
        except Exception as e:
            print('Login failed:', str(e))
            return False

    @staticmethod
    def get_smartplugs(user, session):
        try:
            id = user['id']
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                apiSecret=API_SECRET, apiDeviceID=user['dev1']) 
            tuya_devices = cloud.getdevices()
            appliances = [{'id': dev['id'], 'name': dev['name']} for dev in tuya_devices]
            print(tuya_devices)
            return appliances
        except Exception as e:
            print('Error retrieving Tuya smart plugs:', str(e))
            return False

    @staticmethod
    async def switch(user, app_id, status):
        try:
            id = user['id']
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                apiSecret=API_SECRET, apiDeviceID=user['dev1'], initial_token=session[id]['token']) 
            tuya_devices = cloud.getdevices()
            command = {"commands": [{"code": "switch_1", "value": status}]}
            cloud.sendcommand(app_id, command)
            return True  
        except: 
            return False
            
    
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop) 
cloud = Cloud_interface(loop)