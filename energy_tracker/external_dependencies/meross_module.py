from datetime import datetime, timedelta
import logging

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

from interfaces.plug import Plug
class Meross(Plug):
    day = timedelta(hours=20)
    
    def __init__(self, user):
        self.email = user['email']
        self.client = None
        self.manager = None
        self.loggedin = None
        self.first = True
        self.prev = datetime.now()
        self.logger = logging.getLogger(__name__)
              
    async def _inner_login(self, password=None):
        try:     
            if password != None:
                self.password = password
            self.client = await MerossHttpClient.async_from_user_password(email=self.email, password=self.password)
            self.manager = MerossManager(http_client=self.client)
            self.loggedin = True
        except:
            self.loggedin = False
            self.logger.error('meross login error')
              
    async def _logout(self):
        try:
            self.manager.close()
            await self.client.async_logout()  
        except:
            self.logger.error('meross logout error')
            
    async def update_creds(self):
        await self._logout()
        await self._inner_login()
        
    async def _daily_update_creds(self):
        current = datetime.now()
        if current - self.prev >= Meross.day:
            await self.update_creds()
            prev += Meross.day
            
    async def login(self, password):
        if self.first:
            await self._inner_login(password)
            self.first = False
        elif not self.loggedin:
            await self._inner_login(password)  
        await self._daily_update_creds()
        return self.loggedin 
           
    async def get_devices(self):  
        await self.manager.async_init()
        await self.manager.async_device_discovery()
        meross_devices = self.manager.find_devices(device_type="mss310")
        self.logger.info(f'{len(meross_devices)} devices')
        return meross_devices
        
    async def get_id(self, dev):
        return str(dev.uuid)
    
    async def get_info(self, dev): 
        try:     
            await dev.async_update(timeout=2)        
            on_off = dev.is_on()
            connection_status = dev.online_status.value == 1
            reading = await dev.async_get_instant_metrics(timeout=5)
            return on_off, connection_status, reading.power
        except Exception:
            self.logger.error('status error', exc_info=True)
            return None, False, None    