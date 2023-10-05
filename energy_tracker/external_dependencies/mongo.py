# from pymongo.operations import UpdateOne
from bson import ObjectId
import logging

from pymongo import MongoClient

from interfaces.db import DB
class Mongo(DB):
    
    def __init__(self, URL, database):
        self.logger = logging.getLogger(__name__)
        try:
            client = MongoClient(URL)
            self.db = client[database]
        except:
            self.logger.error('mongodb init error', exc_info=True)


    def get_doc(self, collection, query={}, projection={}, sort=None):
        try: 
            doc = self.db[collection].find_one(query, projection, sort=sort)
            return doc  
        except:
            self.logger.error('mongodb read error', exc_info=True) 
            return False
        
        
    def get_docs(self, collection, query={}, projection={}, sort=None):
        try: 
            docs = self.db[collection].find(query, projection)
            return docs  
        except:
            self.logger.error('mongodb read all error', exc_info=True) 
            return False


    def insert_doc(self, collection ,doc):
        try:
            self.db[collection].insert_one(doc)  
        except:
            self.logger.error('mongodb insert error', exc_info=True) 
      
            
    def insert_docs(self, collection ,docs):
        try:
            self.db[collection].insert_many(docs)  
        except Exception as e:
            self.logger.error('mongodb insert all error', exc_info=True)
     
            
    def update_appliances(self, collection, id, updates):
        try:
            for device_id, values in updates:
                filter_query = {'_id':ObjectId(id), 'appliances._id': ObjectId(device_id)}
                update_query = {
                    '$set': {
                        f'appliances.$.{key}': value for key, value in values.items()
                    }
                }
                self.db[collection].update_one(filter_query, update_query)
                
        except:
            self.logger.error('mongodb update appliances error', exc_info=True) 


    def update_all(self, collection, field, value):
        try:
            self.db[collection].update_many({}, {"$set": 
                {field: value}})
        
        except:
            self.logger.error('mongodb update all error', exc_info=True)

    # def update_docs(collection, update_value):
    #     try:  
    #         update_requests = []
    #         for _id, new_values in update_values:
    #             update_requests.append(UpdateOne({'_id': _id}, {'$set': new_values}))

    #         result = collection.bulk_write(update_requests)

    #         if result.modified_count > 0:
    #             print(f"Updated {result.modified_count} documents")
    #         else:
    #             print("No documents were updated")  
                
    #     except Exception as e:
    #         print(f'mongodb update error: {repr(e)}') 



    
