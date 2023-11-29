"""
cloud_interface.py - Cloud interface for interacting with Meross and Tuya smart plugs.

This module defines a `Cloud_interface` class that serves as an interface 
for managing smart plugs from different cloud platforms,
such as Meross and Tuya. The module also includes separate implementations for Meross and Tuya, 
providing methods for verifying credentials, retrieving smart plugs, and switching plug status.

Classes:
- Cloud_interface: Interface for managing smart plugs from different cloud platforms.
- Meross: Implementation for interacting with Meross smart plugs.
- Tuya: Implementation for interacting with Tuya smart plugs.

Functions:
- verify_credentials(type, user): Verifies the credentials for the specified cloud platform.
- get_smartplugs(type, user): Retrieves a list of smart plugs for the specified cloud platform.
- switch(type, user, app_id, status): Switches the smart plug for the specified cloud platform.
"""
import asyncio
import os
import traceback
from dotenv import load_dotenv
from flask import jsonify
from meross_iot.model.credentials import MerossCloudCreds
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import tinytuya
from app.utils.enums import PlugType


load_dotenv(os.path.join('.secrets', '.env'))
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


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
        if manager is not None:
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
            traceback.print_exc()
            return False

    @staticmethod
    async def verify_credentials(user):
        try:
            client = None
            client = await MerossHttpClient.async_from_user_password(user['email'], user['password'])
            await Meross._logout(client)
            return True,None,None
        except Exception as e:
            if client is not None:
                await Meross._logout(client)
            traceback.print_exc()
            return False, jsonify({'message': f'Error occurred while validating Meross credentials: {str(e)}'}), 500

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
                smartplugs = [{'id': str(dev.uuid), 'name': dev.name} for dev in meross_devices]
                await Meross._logout(client, manager) #for testing only
                return smartplugs,None,None
            else:
                return [], None,None
        except Exception as e:
            await Meross._logout(client, manager)
            print('Error retrieving Meross smart plugs:', str(e))
            traceback.print_exc()
            return [], jsonify({'message': f'Error occurred while retrieving smart plugs: {str(e)}'}), 500

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
                return True,None,None
            else:
                return False,None,None
        except Exception as e:
            await Meross._logout(client, manager)
            print('Error Switching Meross smart plugs:', str(e))
            traceback.print_exc()
            return False, {'message': f'Error Switching Tuya appliance: {str(e)}'}, 500

class Tuya():
    # tuya doesnt require any email or password, it just needs any device id
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
            traceback.print_exc()
            return False

    @staticmethod
    def get_smartplugs(user, session):
        try:
            cloud = Tuya._login(user, session)
            tuya_devices = cloud.getdevices()
            smartplugs = [{'id': dev['id'], 'name': dev['name']} for dev in tuya_devices]
            return smartplugs,None,None

        except Exception as e:
            print('Error retrieving Tuya smart plugs:', str(e))
            traceback.print_exc()
            return [], jsonify({'message': f'Error occurred while retrieving smart plugs: {str(e)}'}), 500

    @staticmethod
    def switch(user, app_id, status, session):
        try:
            cloud = Tuya._login(user, session)
            command = {"commands": [{"code": "switch_1", "value": status}]}
            result = cloud.sendcommand(app_id, command)
            return result['result'], None, None
        except Exception as e:
            Tuya.verify_credentials(user)
            print('Error Switching Tuya appliance:', str(e))
            traceback.print_exc()
            return False, {'message': f'Error Switching Tuya appliance: {str(e)}'}, 500

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
cloud = Cloud_interface(loop)
