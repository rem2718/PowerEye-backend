from abc import ABC, abstractmethod

class Plug(ABC):

    @abstractmethod
    def __init__(self, user:dict):
        pass

    @abstractmethod
    def login(self, password:str=None) -> bool:
        pass

    @abstractmethod
    def update_creds(self):
        pass 
    
    @abstractmethod          
    def get_devices(self) -> list:  
        pass

    @abstractmethod
    def get_id(self, dev) -> str:
        pass
    
    @abstractmethod    
    def get_info(self, dev) -> tuple[bool, bool, float]: 
        pass   
            
            

       


    
