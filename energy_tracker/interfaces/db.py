from abc import ABC, abstractmethod

class DB(ABC):

    @abstractmethod
    def get_doc(self, collection:str, query:dict={}, projection:dict={}):
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
    def update_all(self, collection:str, field:str, value):
        pass


       


    
