from datetime import datetime
from bson import ObjectId

import pytest

from tests.integration.fixtures import db_instance
from app.tasks.updater import Updater


@pytest.fixture(scope="module")
def updater_instance(db_instance):
    updater = Updater("64d154d494895e0b4c1bc081", db_instance)
    return updater


def test_updater(updater_instance, db_instance):
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    yesterday_energys = updater_instance._yesterday_energys(appliances)
    new_energy = (
        sum(value for value in yesterday_energys.values())
        + user["current_month_energy"]
    )

    updater_instance.run()

    doc = db_instance.get_doc(
        "Energys",
        {"user": ObjectId("64d154d494895e0b4c1bc081")},
        sort=[("date", -1), ("_id", -1)],
    )
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    assert all(
        doc[app_id] == yesterday_energys[app_id] for app_id in yesterday_energys.keys()
    )
    assert all(app["energy"] == 0 for app in appliances)
    if datetime.now().day == 1:
        assert user["current_month_energy"] == 0
    else:
        assert user["current_month_energy"] == new_energy
