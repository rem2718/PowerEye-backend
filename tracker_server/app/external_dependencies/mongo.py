from bson import ObjectId
import logging

from pymongo import MongoClient

from app.interfaces.db import DB


class Mongo(DB):
    """
    MongoDB database interface for performing database operations.
    This class provides methods for interacting with MongoDB, including retrieving documents, inserting documents,
    updating documents, and more.

    Attributes:
        logger (logging.Logger): The logger for logging messages.
        client (pymongo.MongoClient): The MongoDB client instance
        db (pymongo.database.Database): The MongoDB database instance.
    """

    def __init__(self, URL, database):
        """
        Constructor for the Mongo class.
        Args:
            URL (str): The URL of the MongoDB server.
            database (str): The name of the MongoDB database.
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.client = MongoClient(URL)
            self.db = self.client[database]
        except:
            self.logger.error("mongodb init error", exc_info=True)

    def get_doc(self, collection, query={}, projection={}, sort=None):
        """
        Retrieve a single document from the specified collection.
        Args:
            collection (str): The name of the collection.
            query (dict, optional): The query criteria for finding the document.
            projection (dict, optional): The fields to include or exclude in the result.
            sort (list, optional): The sorting criteria for the result.
        Returns:
            dict or None: The retrieved document or None if not found.
        """
        try:
            doc = self.db[collection].find_one(query, projection, sort=sort)
            return doc
        except:
            self.logger.error("mongodb read error", exc_info=True)
            return None

    def get_docs(self, collection, query={}, projection={}, sort=None):
        """
        Retrieve multiple documents from the specified collection.
        Args:
            collection (str): The name of the collection.
            query (dict, optional): The query criteria for finding the documents.
            projection (dict, optional): The fields to include or exclude in the results.
            sort (list, optional): The sorting criteria for the results.

        Returns:
            pymongo.cursor.Cursor or None: A cursor for the retrieved documents or None if not found.
        """
        try:
            docs = self.db[collection].find(query, projection, sort=sort)
            return docs
        except:
            self.logger.error("mongodb read all error", exc_info=True)
            return None

    def insert_doc(self, collection, doc):
        """
        Insert a single document into the specified collection.
        Args:
            collection (str): The name of the collection.
            doc (dict): The document to be inserted.
        """
        try:
            self.db[collection].insert_one(doc)
        except:
            self.logger.error("mongodb insert error", exc_info=True)

    def insert_docs(self, collection, docs):
        """
        Insert multiple documents into the specified collection.

        Args:
            collection (str): The name of the collection.
            docs (list): The list of documents to be inserted.
        """
        try:
            self.db[collection].insert_many(docs)
        except Exception as e:
            self.logger.error("mongodb insert all error", exc_info=True)

    def update_appliances(self, collection, id, updates):
        """
        Update appliances information in a document.
        Args:
            collection (str): The name of the collection.
            id (str): The identifier of the owner (user) of the appliances.
            updates (list): A list of device updates, each containing a device_id and values to update.
        """
        try:
            for device_id, values in updates:
                filter = {"_id": ObjectId(id), "appliances._id": ObjectId(device_id)}
                update = {
                    "$set": {
                        f"appliances.$.{key}": value for key, value in values.items()
                    }
                }
                self.db[collection].update_one(filter, update)
        except:
            self.logger.error("mongodb update appliances error", exc_info=True)

    def update(self, collection, id, field, value, array_filters=None):
        """
        Update a field in a document.
        Args:
            collection (str): The name of the collection.
            id (str): The identifier of the document.
            field (str): The field to be updated.
            value: The new value for the field.
            array_filters (list, optional): Filters for array updates.
        """
        try:
            filter = {"_id": ObjectId(id)}
            update = {"$set": {field: value}}
            self.db[collection].update_one(filter, update, array_filters=array_filters)
        except:
            self.logger.error("mongodb update all error", exc_info=True)
