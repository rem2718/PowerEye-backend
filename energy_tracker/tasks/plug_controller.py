import asyncio

from external_dependencies.meross_module import Meross
from external_dependencies.tuya_module import Tuya
from types_classes import PlugType
          
class PlugController():
    
    def __init__(self,  event_loop:asyncio.AbstractEventLoop, user:dict, type:PlugType):
        self.loop = event_loop
        if type == PlugType.MEROSS:
            self.plug = Meross(user)
            self.is_async = True
        elif type == PlugType.TUYA:
            self.plug = Tuya(user)
            self.is_async = False
     
    def _run_async(self, async_func):
        return self.loop.run_until_complete(async_func())
               
    def login(self, password):
        if self.is_async:
            return self._run_async(lambda: self.plug.login(password))
        else:
            return self.plug.login(password)
           
    def update_creds(self):
        if self.is_async:
            self._run_async(lambda: self.plug.update_creds())
        else:
            self.plug.update_creds()
        
    def get_devices(self):  
        if self.is_async:
            return self._run_async(self.plug.get_devices)
        else:
            return self.plug.get_devices()

    def get_id(self, dev):
        if self.is_async:
            return self._run_async(lambda: self.plug.get_id(dev))
        else:
            return self.plug.get_id(dev)
        
    def get_info(self, dev): 
        if self.is_async:
            return self._run_async(lambda: self.plug.get_info(dev))
        else:
            return self.plug.get_info(dev)    
            