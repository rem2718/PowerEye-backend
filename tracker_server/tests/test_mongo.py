import pytest
from pymongo.errors import ServerSelectionTimeoutError
from pymongo import MongoClient
from unittest.mock import Mock
from app.interfaces.db import DB
from app.external_dependencies.mongo import Mongo

# Mocked database connection for testing
class MockDB:
    def __init__(self):
        self.database = {}

    def insert_one(self, collection, document):
        if collection not in self.database:
            self.database[collection] = []
        self.database[collection].append(document)

    def find_one(self, collection, query):
        if collection in self.database:
            for document in self.database[collection]:
                if all(document[key] == value for key, value in query.items()):
                    return document
        return None

# Replace with your MongoDB URL and database name
MONGODB_URL = "mongodb://localhost:27017/"
TEST_DATABASE = "test_db"

# MongoDB database client for testing
@pytest.fixture
def mongo_client():
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=1000)
        client.server_info()
        return client
    except ServerSelectionTimeoutError:
        pytest.skip("MongoDB server is not available")

# Fixture to initialize the MongoDB class for testing
@pytest.fixture
def mongo_instance():
    db = MockDB()
    mongo = Mongo(MONGODB_URL, TEST_DATABASE)
    mongo.db = db
    return mongo

def test_insert_and_retrieve_document(mongo_instance):
    collection = "test_collection"
    document = {"_id": 1, "name": "John"}

    # Insert a document
    mongo_instance.insert_doc(collection, document)

    # Retrieve the inserted document
    retrieved = mongo_instance.get_doc(collection, {"_id": 1})

    assert retrieved == document

def test_insert_and_retrieve_multiple_documents(mongo_instance):
    collection = "test_collection"
    documents = [
        {"_id": 1, "name": "John"},
        {"_id": 2, "name": "Alice"},
        {"_id": 3, "name": "Bob"},
    ]

    # Insert multiple documents
    mongo_instance.insert_docs(collection, documents)

    # Retrieve all documents from the collection
    retrieved_docs = list(mongo_instance.get_docs(collection))

    assert len(retrieved_docs) == len(documents)
    assert all(doc in retrieved_docs for doc in documents)

def test_update_document_field(mongo_instance):
    collection = "test_collection"
    document = {"_id": 1, "name": "John"}

    # Insert a document
    mongo_instance.insert_doc(collection, document)

    # Update the "name" field of the document
    new_name = "Alice"
    mongo_instance.update(collection, 1, "name", new_name)

    # Retrieve the updated document
    retrieved = mongo_instance.get_doc(collection, {"_id": 1})

    assert retrieved["name"] == new_name
