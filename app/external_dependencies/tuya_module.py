from datetime import timedelta
import logging
import os

from dotenv import load_dotenv
import tinytuya

from interfaces.plug import Plug
class Tuya(Plug):
    MIN = timedelta(minutes=1)

    def __init__(self, user):
        load_dotenv(os.path.join('.secrets', '.env'))
        self.API_KEY = os.getenv('API_KEY')
        self.API_SECRET = os.getenv('API_SECRET')
        self.dev1 = user['dev1']
        self.first = True
        self.logger = logging.getLogger(__name__)
    
    def update_creds(self):
        pass
              
    def login(self, password=None):
        if self.first:
            self.cloud = tinytuya.Cloud(apiRegion="eu", apiKey=self.API_KEY,
                    apiSecret=self.API_SECRET, apiDeviceID=self.dev1)
            self.first = False
        return True
    
    def get_devices(self): 
        tuya_devices = self.cloud.getdevices()
        self.logger.info(f'{len(tuya_devices)} devices')
        return tuya_devices
    
    def get_id(self, dev):
        return dev['id']
    
    def get_info(self, dev):
        try:
            connection_status = self.cloud.getconnectstatus(dev['id'])
            result = self.cloud.getstatus(dev['id'])
            power = (result['result'][4]['value']) /10.0
            on_off = result['result'][0]['value']
            return on_off, connection_status, power
        except:
            self.logger.error('status error', exc_info=True)
            return None, False, None     

        