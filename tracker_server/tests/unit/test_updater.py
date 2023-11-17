from unittest.mock import MagicMock
from unittest.mock import call
from datetime import datetime
from bson import ObjectId
import pickle
import os

from pandas.testing import assert_frame_equal
import pandas as pd
import pytest

from app.tasks.updater import Updater


@pytest.fixture(scope="module")
def mocked_db():
    db = MagicMock()
    db.update = MagicMock()
    return db

class Model:
    def __init__(self, name):
        self.name = name

@pytest.fixture
def model():
    return Model(name='test_model')


@pytest.fixture(scope="module")
def updater_instance(mocked_db):
    updater = Updater("5f5b940f60a37c2b4012b971", mocked_db)
    return updater


@pytest.mark.parametrize(
    ("date"),
    (
        (datetime(2023, 11, 16)),
        (datetime(2023, 11, 1)),
    ),
)
def test_update_energy(updater_instance, date):
    user = {
        "_id": ObjectId("5f5b940f60a37c2b4012b971"),
        "current_month_energy": 0,
        "appliances": [
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b973"),
                "energy": 1,
            },
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b974"),
                "energy": 0.1,
            },
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b975"),
                "energy": 4.5,
            },
        ],
    }
    doc = {
        "user": ObjectId("5f5b940f60a37c2b4012b971"),
        "date": updater_instance.date,
        "5f5b940f60a37c2b4012b973": 1,
        "5f5b940f60a37c2b4012b974": 0.1,
        "5f5b940f60a37c2b4012b975": 4.5,
    }
    res = updater_instance._update_energy(user, date)
    assert res == doc
    if date.day == 1:
        updater_instance.db.update.assert_has_calls(
            [call("Users", "5f5b940f60a37c2b4012b971", "current_month_energy", 0)]
        )
    else:
        updater_instance.db.update.assert_has_calls(
            [call("Users", "5f5b940f60a37c2b4012b971", "current_month_energy", 5.6)]
        )


def test_yesterday_powers(updater_instance):
    docs = [
        {
            "5f5b940f60a37c2b4012b973": 1,
            "5f5b940f60a37c2b4012b974": 0.1,
            "5f5b940f60a37c2b4012b975": 4,
        },
        {
            "5f5b940f60a37c2b4012b973": 6,
            "5f5b940f60a37c2b4012b974": 0.3,
            "5f5b940f60a37c2b4012b975": 0.4,
        },
        {
            "5f5b940f60a37c2b4012b973": 1,
            "5f5b940f60a37c2b4012b974": 8,
            "5f5b940f60a37c2b4012b975": 0.45,
        },
    ]
    updater_instance.db.get_docs = MagicMock(return_value=docs)
    res = updater_instance._yesterday_powers()
    output = pd.DataFrame(docs)
    assert_frame_equal(res, output)


def test_cur_month_energy(updater_instance):
    docs = [
        {
            "5f5b940f60a37c2b4012b973": 1,
            "5f5b940f60a37c2b4012b974": 0.1,
            "5f5b940f60a37c2b4012b975": 4,
        },
        {
            "5f5b940f60a37c2b4012b973": 6,
            "5f5b940f60a37c2b4012b974": 0.3,
            "5f5b940f60a37c2b4012b975": 0.4,
        },
        {
            "5f5b940f60a37c2b4012b973": 1,
            "5f5b940f60a37c2b4012b974": 8,
            "5f5b940f60a37c2b4012b975": 0.45,
        },
    ]
    res = updater_instance._cur_month_energy()
    output = pd.DataFrame(docs)
    assert_frame_equal(res, output)


def test_dump_model(updater_instance, model):
    type = "test"
    app_id = "5f5b940f60a37c2b4012b975"
    updater_instance._dump_model(type, app_id, model)

    folder_path = "models_filesystem/test_models/5f5b940f60a37c2b4012b971"
    assert os.path.exists(folder_path)
    file_path = os.path.join(folder_path, "5f5b940f60a37c2b4012b975.pkl")
    file = open(file_path, "rb")
    output = pickle.load(file)
    assert isinstance(output, Model) 


def test_run():
    pass
