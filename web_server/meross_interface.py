# This file will be moved later on to its correct place
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import tinytuya
import asyncio
from types_classes import PlugType
from flask import session
import os
from dotenv import load_dotenv

load_dotenv(os.path.join('.secrets', '.env'))
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

class cloud_interface():
    # user for meross: {'id':_ , 'email':_, 'password':_}
    # user for tuya: {'id':_ , 'dev1':_}
    def __init__(self, event_loop:asyncio.AbstractEventLoop):
        self.loop = event_loop
    
    def _run_async(self, async_func):
        return self.loop.run_until_complete(async_func())
    
    def verify_credentials(self, type, user):
        match type:
            case PlugType.MEROSS.value: return self._run_async(Meross.verify_credentials(user))
            case PlugType.TUYA.value: return Tuya.verify_credentials(user)
        
    def get_appliances(self, type, user):
        match type:
            case PlugType.MEROSS.value: return self._run_async(Meross.get_appliances(user))
            case PlugType.TUYA.value: return Tuya.get_appliances(user)
 
    def switch(self, type, user, app_id, status):    
        match type:
            case PlugType.MEROSS.value: return self._run_async(Meross.switch(user, app_id, status))
            case PlugType.TUYA.value: return Tuya.switch(user, app_id, status)   
 
        
class Meross():
    
    @staticmethod
    async def verify_credentials(user):
        try:
            id = user['id']
            client = await MerossHttpClient.async_from_user_password(user['email'], user['password'])
            session[id]['token'] = client.cloud_credentials.token
            session[id]['key'] = client.cloud_credentials.key
            session[id]['issued_on'] = client.cloud_credentials.issued_on
            return True
        except:
            print('login failed')
            return False

    @staticmethod
    async def get_appliances(user):
        try:
            id = user['id']
            client = await MerossHttpClient.async_from_cloud_creds(MerossCloudCreds(session[id]['token'], session[id]['issued_on']))
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
            client = await MerossHttpClient.async_from_cloud_creds(MerossCloudCreds(session[id]['token'], session[id]['issued_on']))
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
    def verify_credentials(user): 
        try:
            id = user['id']
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                    apiSecret=API_SECRET, apiDeviceID=user['dev1'])
            session[id]['token'] = cloud._gettoken()
            return True
        except:
            print('login failed')
            return False

    @staticmethod
    def get_appliances(user):
        try:
            id = user['id']
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                apiSecret=API_SECRET, apiDeviceID=user['dev1'], initial_token=session[id]['token']) 
            tuya_devices = cloud.getdevices()
            appliances = [{'id': dev['id'], 'name': dev['name']} for dev in tuya_devices]
            return appliances
        except:
            return None

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
            return None
            