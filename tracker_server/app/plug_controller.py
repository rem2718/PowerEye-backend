import asyncio

from app.external_dependencies.meross_module import Meross
from app.external_dependencies.tuya_module import Tuya
from app.types_classes import PlugType
          
class PlugController():
    """
    A controller for different types of smart plug devices (sync and async).
    Attributes:
        loop (asyncio.AbstractEventLoop): The event loop for asynchronous operations.
        plug: An instance of the smart plug device (either Meross, Tuya or other).
        is_async (bool): True if the device interaction is asynchronous, False otherwise.
    """
    
    def __init__(self,  event_loop:asyncio.AbstractEventLoop, data:dict):
        """
        Constructor for the PlugController class.
        Args:
            event_loop (asyncio.AbstractEventLoop): The event loop for asynchronous operations.
            data (dict): A dictionary containing user data.
        """
        self.loop = event_loop
        self.plug, self.is_async = self._create_plug(data)
                
    def _create_plug(self, data):
        """
        Create a plug instance based on the 'type' field in the 'data' dictionary.
        Args:
            data (dict): A dictionary containing user data.
        Returns:
            tuple: A plug instance and a boolean indicating whether the device interaction is asynchronous (True) or not (False).
        """
        match data['type']:
            case PlugType.MEROSS.value: return Meross(data), True
            case PlugType.TUYA.value: return Tuya(data), False
     
    def _run_async(self, async_func):
        """
        Run an asynchronous function using the event loop.
        Args:
            async_func (Callable): The asynchronous function to run.
        Returns:
            Any: The result of the asynchronous function.
        """
        return self.loop.run_until_complete(async_func())
               
    def login(self, password):
        """
        Log in to the Plug device cloud using a password.
        Args:
            password (str): The password for authentication.
        Returns:
            bool: True if the login is successful, otherwise False.
        """
        if self.is_async:
            return self._run_async(lambda: self.plug.login(password))
        else:
            return self.plug.login(password)
           
    def update_creds(self):
        """
        Update the credentials used to log in to the Plug Cloud.
        """
        if self.is_async:
            self._run_async(lambda: self.plug.update_creds())
        else:
            self.plug.update_creds()
        
    def get_devices(self):  
        """
        Retrieve a list of devices associated with the Plug cloud.
        Returns:
            list: A list of device objects.
        """
        if self.is_async:
            return self._run_async(self.plug.get_devices)
        else:
            return self.plug.get_devices()

    def get_id(self, dev):
        """
        Get the unique identifier for a specific device.
        Args:
            dev: The device for which to retrieve the identifier.
        Returns:
            str: The unique identifier of the device.
        """
        if self.is_async:
            return self._run_async(lambda: self.plug.get_id(dev))
        else:
            return self.plug.get_id(dev)
        
    def get_info(self, dev): 
        """
        Get information about a specific device.
        Args:
            dev: The device for which to retrieve information.
        Returns:
            tuple: A tuple containing information about the device.
        """
        if self.is_async:
            return self._run_async(lambda: self.plug.get_info(dev))
        else:
            return self.plug.get_info(dev)    
            