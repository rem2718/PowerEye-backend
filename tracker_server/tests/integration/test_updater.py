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
    powers = updater_instance._yesterday_powers()
    if powers.shape[0] == 0:
        previous_day = updater_instance.date - updater_instance.day
        query = {
            "user": ObjectId("64d154d494895e0b4c1bc081"),
            "timestamp": {
                "$gte": previous_day.replace(hour=0, minute=0, second=0),
                "$lt": previous_day.replace(hour=23, minute=59, second=59),
            },
        }
        powers = db_instance.client["hemsproject"]["Powers"].find(query)
        db_instance.insert_docs("Powers", powers)
        powers = updater_instance._yesterday_powers()
    energys = updater_instance._generate_yesterday_energys(appliances, powers.copy())
    new_energy = (
        sum(abs(value) for value in energys.values()) + user["current_month_energy"]
    )
    
    updater_instance.run()

    doc = db_instance.get_doc(
        "Energys",
        {"user": ObjectId("64d154d494895e0b4c1bc081")},
        sort=[("date", -1), ("_id", -1)],
    )
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    assert all(doc[app_id] == energys[app_id] for app_id in energys.keys())
    assert all(app["energy"] == 0 for app in appliances)
    assert user["current_month_energy"] == new_energy
