# import pytest
# from pymongo import MongoClient
# from pymongo.errors import ServerSelectionTimeoutError
# from app.external_dependencies.mongo import Mongo

# MONGODB_URL = "mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/"
# TEST_DATABASE = "test"  # Replace with your database name

# # MongoDB database client for testing
# @pytest.fixture
# def mongo_client():
#     try:
#         client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=1000)
#         client.server_info()  # Check if the client can connect to the server
#         return client
#     except ServerSelectionTimeoutError:
#         pytest.skip("MongoDB server is not available")

# # # Fixture to drop the "Mongo" collection before running the tests
# # @pytest.fixture(autouse=True)
# # def drop_mongo_collection(request, mongo_client):
# #     # The finalizer function to drop the collection
# #     def drop():
# #         collection_name = "Mongo"  # Change to the actual collection name you want to drop
# #         if collection_name in mongo_client[TEST_DATABASE].list_collection_names():
# #             mongo_client[TEST_DATABASE][collection_name].drop()

# #     # Add the finalizer
# #     request.addfinalizer(drop)

# # Fixture to initialize the MongoDB class for testing
# @pytest.fixture
# def mongo_instance(mongo_client):
#     mongo = Mongo(MONGODB_URL, TEST_DATABASE)
#     return mongo

# # Your test functions (you can add your test functions here)
# # Example:
# def test_insert_and_retrieve_document(mongo_instance):
#     collection = "Mongo"
#     document = {"_id": 1, "name": "John"}
#     mongo_instance.insert_doc(collection, document)
#     retrieved = mongo_instance.get_doc(collection, {"_id": 1})
#     assert retrieved == document

# # # Example 2 (using the drop_mongo_collection fixture):
# # def test_another_function(drop_mongo_collection, mongo_instance):
# #     # This test function will automatically drop the "Mongo" collection before running
# #     # your test code, thanks to the drop_mongo_collection fixture.

# # Example 3 (with the test_update_document_field function):
# def test_update_document_field(mongo_instance):
#     collection = "Mongo"
#     document = {"_id": 1, "name": "John"}
#     mongo_instance.insert_doc(collection, document)
#     new_name = "Abdulrahman"
#     updated_document = {"name": new_name}
#     mongo_instance.update(collection, 1, "name", new_name)
#     retrieved = mongo_instance.get_doc(collection, {"_id": 1})
#     assert retrieved["name"] == new_name

# # Run your tests using pytest








import pytest
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.external_dependencies.mongo import Mongo
from pymongo import MongoClient

MONGODB_URL = "mongodb+srv://219410523:Maya2001@hems.kcuurlg.mongodb.net/"
TEST_DATABASE = "test"  # Replace with your database name

# MongoDB database client for testing
@pytest.fixture
def mongo_client():
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=1000)
        client.server_info()
        return client
    except ServerSelectionTimeoutError:
        pytest.skip("MongoDB server is not available")

# Fixture to drop the "Mongo" collection before running the tests
@pytest.fixture(autouse=True)
def drop_mongo_collection(request, mongo_client):
    # The finalizer function to drop the collection
    def drop():
        collection_name = "Mongo"
        if collection_name in mongo_client[TEST_DATABASE].list_collection_names():
            mongo_client[TEST_DATABASE][collection_name].drop()

    # Add the finalizer
    request.addfinalizer(drop)

@pytest.fixture
def create_mongo_collection(mongo_client):
    # Create the collection
    collection_name = "Mongo"
    db = mongo_client[TEST_DATABASE]
    db.create_collection(collection_name)
    yield db[collection_name]  # Return the collection

# Fixture to initialize the MongoDB class for testing
@pytest.fixture
def mongo_instance(mongo_client):
    mongo = Mongo(MONGODB_URL, TEST_DATABASE)
    return mongo

# Your test functions
 def test_insert_and_retrieve_document(mongo_instance):
     collection = "Mongo"
     document = {"_id": 1, "name": "John"}

     # Insert a document
     mongo_instance.insert_doc(collection, document)

     # Retrieve the inserted document
     retrieved = mongo_instance.get_doc(collection, {"_id": 1})

     assert retrieved == document

 # def test_insert_and_retrieve_multiple_documents(mongo_instance):
     collection = "Mongo"
     # Insert multiple documents into the collection

     documents = [
         {"_id": 2, "name": "Sara"},
         {"_id": 3, "name": "Alice"},
         {"_id": 4, "name": "Bob"},
     ]
     mongo_instance.db[collection].insert_many(documents)

     # Insert multiple documents
     mongo_instance.insert_docs(collection, documents)

     # Retrieve all documents from the collection
     retrieved_docs = list(mongo_instance.get_docs(collection))

     assert len(retrieved_docs) == len(documents)
     assert all(doc in retrieved_docs for doc in documents)


#  def test_update_document_field(mongo_instance):
#      collection = "Mongo"
#      document = {"_id": 1, "name": "John"}

#      # Insert a document
#      mongo_instance.insert_doc(collection, document)

#      # Update the "name" field of the document with _id=1
#      new_name = "Abdulrahman"
#      updated_document = {"name": new_name}

#      mongo_instance.update(collection, 1, "name", new_name)

#      # Retrieve the updated document
#      retrieved = mongo_instance.get_doc(collection, {"_id": 1})

#      assert retrieved["name"] == new_name

