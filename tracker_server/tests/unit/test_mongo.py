from datetime import datetime
from bson import ObjectId
import os

from dotenv import load_dotenv
import pytest

from app.external_dependencies.mongo import Mongo

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture
def db_instance():
    URL = os.getenv("DB_URL")
    database = "test"
    db = Mongo(URL, database)
    return db


def test_get_doc(db_instance):
    projection = {"_id": 0}
    sort = [("timestamp", -1)]
    doc = db_instance.get_doc(
        "Powers_test",
        {"user": ObjectId("64d1548894895e0b4c1bc07f")},
        projection=projection,
        sort=sort,
    )
    expected_res = {
        "timestamp": datetime(2023, 11, 15, 1, 51, 31, 872000),
        "64d161e193d44252699aa219": 261.613,
        "64d162bf93d44252699aa21c": 10.795,
        "64d15f9393d44252699aa215": 0.0,
        "user": ObjectId("64d1548894895e0b4c1bc07f"),
        "64d1605493d44252699aa216": None,
        "64d160d293d44252699aa218": 100.9,
        "64d1629393d44252699aa21b": 0.0,
    }
    assert doc == expected_res


def test_get_docs(db_instance):
    projection = {"_id": 1}
    sort = [("timestamp", -1)]
    docs = db_instance.get_docs(
        "Powers_test",
        {"user": ObjectId("64d154d494895e0b4c1bc081")},
        projection=projection,
        sort=sort,
    )

    expected_res = [
        {"_id": ObjectId("6553f9f3c05547956e38e797")},
        {"_id": ObjectId("6553f9b7c05547956e38e794")},
        {"_id": ObjectId("6553f97bc05547956e38e791")},
    ]

    assert list(docs) == expected_res


def test_insert_doc(db_instance):
    doc = {"dummy_field": "dummy_value"}
    db_instance.insert_doc("Mongo_test", doc)

    assert db_instance.db["Mongo_test"].find_one(doc) is not None


def test_insert_docs(db_instance):
    docs = [{"key": "value1"}, {"key": "value2"}, {"key": "value3"}]

    db_instance.insert_docs("Mongo_test", docs)
    assert all(db_instance.db["Mongo_test"].find(doc) is not None for doc in docs)


def test_update_appliances(db_instance):
    collection_name = "Update_test"
    db_instance.db[collection_name].drop()
    user_id = "64d1548894895e0b4c1bc07f"
    device_updates = [
        ("6553f9b7c05547956e38e791", {"key1": "value1", "key2": "value2"}),
        ("6553f9b7c05547956e38e792", {"key2": "value2"}),
    ]

    test_doc = {
        "_id": ObjectId(user_id),
        "appliances": [
            {
                "_id": ObjectId("6553f9b7c05547956e38e791"),
                "key1": "old_value1",
                "key2": "old_value2",
            },
            {"_id": ObjectId("6553f9b7c05547956e38e792"), "key2": "old_value2"},
        ],
    }

    db_instance.db[collection_name].insert_one(test_doc)
    db_instance.update_appliances(collection_name, user_id, device_updates)

    updated_doc = db_instance.db[collection_name].find_one({"_id": ObjectId(user_id)})
    assert updated_doc is not None
    assert updated_doc["appliances"][0]["key1"] == "value1"
    assert updated_doc["appliances"][1]["key2"] == "value2"


def test_update(db_instance):
    collection_name = "Update_test"
    document_id = "6553f9f3c05547956e38e797"
    field_to_update = "field1"
    new_value = "new_value"
    test_doc = {"_id": ObjectId(document_id), "field1": "old_value"}

    db_instance.db[collection_name].insert_one(test_doc)
    db_instance.update(collection_name, document_id, field_to_update, new_value)

    updated_doc = db_instance.db[collection_name].find_one(
        {"_id": ObjectId(document_id)}
    )
    assert updated_doc is not None
    assert updated_doc[field_to_update] == new_value
