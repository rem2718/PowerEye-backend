from abc import ABC, abstractmethod

from external_dependencies.fcm import FCM
from interfaces.db import DB

class Task(ABC):
    
    @abstractmethod
    def __init__(self, id:str, db:DB, fcm:FCM, additional=None):
        pass
        
    @abstractmethod
    def run(self):
        pass

            
    
