from abc import ABC, abstractmethod


class DB(ABC):
    """
    Abstract base class for database interaction.
    """

    @abstractmethod
    def __init__(self, URL: str, database: str):
        """
        Constructor for the database interface.
        Args:
            URL (str): The database connection URL.
            database (str): The name of the database.
        """
        pass

    @abstractmethod
    def get_doc(
        self, collection: str, query: dict = {}, projection: dict = {}, sort: list = []
    ):
        """
        Get a single document from a collection.
        Args:
            collection (str): The name of the collection.
            query (dict, optional): The query criteria for document retrieval.
            projection (dict, optional): The fields to include or exclude in the retrieved document.
            sort (list, optional): The sorting criteria for the retrieved document.
        """
        pass

    @abstractmethod
    def get_docs(self, collection: str, query: dict = {}, projection: dict = {}):
        """
        Get multiple documents from a collection.
        Args:
            collection (str): The name of the collection.
            query (dict, optional): The query criteria for document retrieval.
            projection (dict, optional): The fields to include or exclude in the retrieved documents.
        """
        pass

    @abstractmethod
    def insert_doc(self, collection: str, doc: dict):
        """
        Insert a single document into a collection.
        Args:
            collection (str): The name of the collection.
            doc (dict): The document to be inserted.
        """
        pass

    @abstractmethod
    def insert_docs(self, collection: str, docs: dict):
        """
        Insert multiple documents into a collection.
        Args:
            collection (str): The name of the collection.
            docs (dict): The documents to be inserted as a dictionary.
        """
        pass

    @abstractmethod
    def update_appliances(self, collection: str, id: str, updates: tuple):
        """
        Update appliances data in a document.
        Args:
            collection (str): The name of the collection.
            id (str): The unique identifier of the owner (user) of the appliances.
            updates (tuple): A tuple containing updates to be applied to the document.
        """
        pass

    @abstractmethod
    def update(
        self, collection: str, id: str, field: str, value, array_filters: list = None
    ):
        """
        Update a specific field in a document.
        Args:
            collection (str): The name of the collection.
            id (str): The unique identifier of the owner (user) of the appliances.
            field (str): The name of the field to be updated.
            value: The new value for the field.
            array_filters (list, optional): A list specifying the filter conditions for array updates. Defaults to None.
        """
        pass
