from datetime import datetime
from bson import ObjectId

import firebase_admin
import pytest

from tests.integration.fixtures import db_instance, fcm_instance
from app.recommender import Recommender as EPR
from app.tasks.checker import Checker
from app.types_classes import EType


@pytest.fixture(scope="module")
def checker_instance(db_instance, fcm_instance):
    checker = Checker("64d154d494895e0b4c1bc081", db_instance, fcm_instance)
    return checker


def test_checker(checker_instance, db_instance):
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    cur_energy = user["current_month_energy"]
    shiftable = [EType.SHIFTABLE.value, EType.PHANTOM.value]
    min = datetime.now().minute
    if min == 0:
        powers = checker_instance._get_powers()
    powers = db_instance.get_doc(
        "Powers",
        {"user": ObjectId("64d154d494895e0b4c1bc081")},
        sort=[("timestamp", -1)],
    )

    checker_instance.run()

    for app in appliances:
        app_id = str(app["_id"])
        if app["is_deleted"]:
            continue

        cur_energy += app["energy"]
        assert app_id in checker_instance.peak_flags
        if EPR.check_peak(datetime.now().hour, app["status"], app["e_type"], shiftable):
            assert not checker_instance.peak_flags[app_id]
        else:
            assert checker_instance.peak_flags[app_id]

        if app_id in powers and app["e_type"] == EType.PHANTOM.value:
            assert app_id in checker_instance.phantom_flags
            model = checker_instance._get_model(app_id, "cluster")
            if EPR.check_phantom(model, powers[app_id], app["status"]):
                assert not checker_instance.phantom_flags[app_id][0]
            else:
                assert checker_instance.phantom_flags[app_id][0]
        if min == 0:
            assert app_id in checker_instance.baseline_flags
            if (
                app["baseline_threshold"] > 0
                and EPR.check_baseline(app_id, app, powers[app_id])
            ):
                assert not checker_instance.baseline_flags[app_id]
            else:
                assert checker_instance.baseline_flags[app_id]

    percentage = EPR.check_goal(cur_energy, user["energy_goal"])
    if percentage:
        assert not checker_instance.goal_flags[percentage]


def test_fcm_cleanup(fcm_instance):
    app = firebase_admin.get_app()
    firebase_admin.delete_app(app)
    del fcm_instance
    assert True
