from enum import Enum
import asyncio
import os
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import tinytuya
from app.models.user_model import PlugType
from flask import session
from dotenv import load_dotenv


load_dotenv(os.path.join('.secrets', '.env'))
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

class PlugType(Enum):
    MEROSS = 1
    TUYA = 2

class Cloud_interface():
    # user for meross: {'id':_ , 'email':, 'password':}
    # user for tuya: {'id':_ , 'dev1':_}
    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.loop = event_loop
        self.session = {}  # Initialize the session dictionary
    
    def _run_async(self, async_func):
        return self.loop.run_until_complete(async_func())
    
    def verify_credentials(self, type, user):
        match type:
            case PlugType.MEROSS: return self._run_async(lambda: Meross.verify_credentials(user))
            case PlugType.TUYA: return Tuya.verify_credentials(user)
        
    def  get_smartplugs(self, type, user):
        match type:
            case PlugType.MEROSS: return self._run_async(lambda: Meross.get_smartplugs(user, self.session))
            case PlugType.TUYA: return Tuya.get_smartplugs(user, self.session)
 

    def switch(self, type, user, app_id, status):    
        match type:
            case PlugType.MEROSS: return self._run_async(lambda: Meross.switch(user, app_id, status, self.session))
            case PlugType.TUYA: return Tuya.switch(user, app_id, status, self.session)   
        
class Meross():

    @staticmethod
    async def _logout(client, manager=None):
        if manager != None:
            manager.close()
        await client.async_logout()

    @staticmethod
    async def _login(user, session):
        try:
            id = user['id']
            manager = None
            if id not in session:
                session[id] = {}
            try:
                creds = MerossCloudCreds(session[id]['token'], session[id]['key'], 
                                        session[id]['user_id'], user['email'], session[id]['issued_on'])
                client = await MerossHttpClient.async_from_cloud_creds(creds)
            except:
                client = await MerossHttpClient.async_from_user_password(user['email'], user['password'])
            session[id]['token'] = client.cloud_credentials.token
            session[id]['key'] = client.cloud_credentials.key
            session[id]['user_id'] = client.cloud_credentials.user_id
            session[id]['issued_on'] = client.cloud_credentials.issued_on 
            manager = MerossManager(http_client=client)
            return client, manager
        except Exception as e:
            print(str(e)) 
            return False
        
    @staticmethod
    async def verify_credentials(user):
        try:
            client = None
            client = await MerossHttpClient.async_from_user_password(user['email'], user['password'])
            await Meross._logout(client)
            return True
        except Exception as e:
            if client != None:
                await Meross._logout(client)
            print('Login failed:', str(e))
            return False

    @staticmethod
    async def get_smartplugs(user, session):
        try:
            if id not in session:
                session[id] = {} 
            res = await Meross._login(user, session)
            if res:
                client, manager = res
                await manager.async_init()
                await manager.async_device_discovery()
                meross_devices = manager.find_devices(device_type="mss310")
                appliances = [{'id': str(dev.uuid), 'name': dev.name} for dev in meross_devices]
                await Meross._logout(client, manager) #for testing only
                return appliances
            else: 
                return []
        except Exception as e:
            await Meross._logout(client, manager)
            print('Error retrieving Meross smart plugs:', str(e)) 
            return []

    @staticmethod
    async def switch(user, app_id, status, session):
        try:
            if id not in session:
                session[id] = {} 
            res = await Meross._login(user, session)
            if res:
                client, manager = res
                await manager.async_init()
                await manager.async_device_discovery()
                [dev] = manager.find_devices(device_uuids=[app_id])
                if status:
                    await dev.async_turn_on(channel=0)
                else:
                    await dev.async_turn_off(channel=0)
                    await Meross._logout(client, manager) #for testing only
                return True 
            else:
                return False
        except Exception as e:
            await Meross._logout(client, manager)
            print('Error Switching Meross smart plugs:', str(e))
            return False
            
class Tuya():
    # tuya dont require any email or password, it just needs any device id
    
    @staticmethod
    def _login(user, session):
        id = user['id']
        if id in session and 'token' in session[id]:  
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                apiSecret=API_SECRET, apiDeviceID=user['dev1'], initial_token=session[id]['token'])
        else:
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                apiSecret=API_SECRET, apiDeviceID=user['dev1']) 
            session[id] = {} 
            session[id]['token'] = cloud._gettoken()
        return cloud
        
    @staticmethod
    def verify_credentials(user): 
        try:
            cloud = tinytuya.Cloud(apiRegion="eu", apiKey=API_KEY,
                    apiSecret=API_SECRET, apiDeviceID=user['dev1'])
            return True
        except Exception as e:
            print('Login failed:', str(e))
            return False

    @staticmethod
    def get_smartplugs(user, session):
        try:
            cloud = Tuya._login(user, session)
            tuya_devices = cloud.getdevices()
            appliances = [{'id': dev['id'], 'name': dev['name']} for dev in tuya_devices]
            return appliances
        except Exception as e:
            print('Error retrieving Tuya smart plugs:', str(e))
            return []

    @staticmethod
    def switch(user, app_id, status, session):
        try:
            cloud = Tuya._login(user, session)  
            command = {"commands": [{"code": "switch_1", "value": status}]}
            result = cloud.sendcommand(app_id, command)
            return result['result']  
        except Exception as e:
            Tuya.verify_credentials(user, session)
            print('Error Switching Tuya appliance:', str(e))
            return False
            
    
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop) 
cloud = Cloud_interface(loop)