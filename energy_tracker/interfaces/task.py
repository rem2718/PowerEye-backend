from abc import ABC, abstractmethod

from external_dependencies.fcm import FCM
from plug_controller import PlugController
from interfaces.db import DB

class Task(ABC):
    
    @abstractmethod
    def __init__(self, id:str, db:DB, fcm:FCM, plug:PlugController=None):
        pass
        
    @abstractmethod
    def run(self):
        pass

            
    
