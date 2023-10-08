from abc import ABC, abstractmethod

class DB(ABC):
    
    @abstractmethod
    def __init__(self, URL:str, database:str):
        pass

    @abstractmethod
    def get_doc(self, collection:str, query:dict={}, projection:dict={}, sort:list=[]):
        pass
    
    @abstractmethod 
    def get_docs(self, collection:str, query:dict={}, projection:dict={}):
        pass

    @abstractmethod
    def insert_doc(self, collection:str ,doc:dict):
        pass
    
    @abstractmethod      
    def insert_docs(self, collection:str ,docs:dict):
        pass
     
    @abstractmethod
    def update_appliances(self, collection:str, id:str, updates:tuple):
        pass

    @abstractmethod
    def update(self, collection:str, id:str, field:str, value, array_filter:list=None):
        pass


       


    
