from external_dependencies.FCM import FCM
from abc import ABC, abstractmethod
from db import DB

class Task(ABC):
    
    @abstractmethod
    @classmethod    
    def set_deps(cls, db:DB, fcm:FCM):
        cls.db = db
        cls.fcm = fcm
        
    @abstractmethod
    def run(self):
        pass

            
    
