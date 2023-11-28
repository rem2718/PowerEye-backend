from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
import pickle

import pandas as pd
import pytest

from app.recommender import Recommender as EPR
from app.tasks.checker import Checker
from app.types_classes import EType


@pytest.fixture(scope="module")
def db_mock():
    db = Mock()

    def mocked_get_doc(collection, query={}, projection={}, sort=None):
        match collection:
            case "Users":
                return {
                    "energy_goal": 15,
                    "current_month_energy": 5,
                    "appliances": [
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b971"),
                            "name": "app1",
                            "is_deleted": False,
                            "e_type": 1,
                            "energy": 1.32,
                            "status": False,
                            "baseline_threshold": 0.2,
                        },
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b972"),
                            "name": "app2",
                            "is_deleted": True,
                            "e_type": 1,
                            "energy": 1.32,
                            "status": False,
                            "baseline_threshold": -1,
                        },
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b973"),
                            "name": "app3",
                            "is_deleted": False,
                            "e_type": 2,
                            "energy": 0,
                            "status": True,
                            "baseline_threshold": -1,
                        },
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b974"),
                            "name": "app4",
                            "is_deleted": False,
                            "e_type": 2,
                            "energy": 0.2,
                            "status": False,
                            "baseline_threshold": 0,
                        },
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b975"),
                            "name": "app5",
                            "is_deleted": False,
                            "e_type": 3,
                            "energy": 0.01,
                            "status": True,
                            "baseline_threshold": 0.2,
                        },
                        {
                            "_id": ObjectId("5f5b940f60a37c2b4012b976"),
                            "name": "app6",
                            "is_deleted": False,
                            "e_type": 3,
                            "energy": 2.25,
                            "status": False,
                            "baseline_threshold": 0.5,
                        },
                    ],
                }
            case "Powers":
                return {
                    "5f5b940f60a37c2b4012b973": 100,
                    "5f5b940f60a37c2b4012b974": 8,
                }

    db.get_doc = MagicMock(side_effect=mocked_get_doc)
    return db


@pytest.fixture(scope="module")
def fcm_mock():
    fcm = Mock()
    fcm.notify = MagicMock()
    return fcm


@pytest.fixture(scope="module")
def checker_instance(db_mock, fcm_mock):
    checker = Checker("64d154bc94895e0b4c1bc080", db_mock, fcm_mock)
    return checker


@pytest.fixture(scope="module")
def apps():
    apps = {
        "5f5b940f60a37c2b4012b971": {
            "name": "app1",
            "e_type": 1,
            "energy": 1.32,
            "status": False,
            "baseline_threshold": 0.2,
        },
        "5f5b940f60a37c2b4012b973": {
            "name": "app3",
            "e_type": 2,
            "energy": 0,
            "status": True,
            "baseline_threshold": -1,
        },
        "5f5b940f60a37c2b4012b974": {
            "name": "app4",
            "e_type": 2,
            "energy": 0.2,
            "status": False,
            "baseline_threshold": 0,
        },
        "5f5b940f60a37c2b4012b975": {
            "name": "app5",
            "e_type": 3,
            "energy": 0.01,
            "status": True,
            "baseline_threshold": 0.2,
        },
        "5f5b940f60a37c2b4012b976": {
            "name": "app6",
            "e_type": 3,
            "energy": 2.25,
            "status": False,
            "baseline_threshold": 0.5,
        },
    }
    return apps


@pytest.fixture(scope="module")
def model():
    file_path = "models_filesystem/cluster_models/64d154bc94895e0b4c1bc080/64d1682993d44252699aa22a.pkl"
    file = open(file_path, "rb")
    model = pickle.load(file)
    file.close()
    return model


def test_run(checker_instance):
    checker_instance.run()
    count = 1 # 1 goal
    if EPR.PEAK_START <= datetime.now().hour < EPR.PEAK_END:
        count += 2  # 2 peak
    elif datetime.now().min == 0:
        count += 2  # 2 baseline

    assert checker_instance.fcm.notify.call_count == count


def test_get_apps(checker_instance, apps):
    user = checker_instance.db.get_doc("Users")
    appliances = user["appliances"]
    res = checker_instance._get_apps(appliances)
    assert res == apps


def test_get_recent_powers(checker_instance, apps):
    expected_res = {
        "5f5b940f60a37c2b4012b973": 100,
        "5f5b940f60a37c2b4012b974": 8,
    }
    res = checker_instance._get_recent_powers(apps)
    assert res == expected_res


def test_get_powers(checker_instance, db_mock):
    powers = [
        {
            "5f5b940f60a37c2b4012b973": 100,
            "5f5b940f60a37c2b4012b974": 8,
            "timestamp": datetime(2023, 1, 1, 1, 1, 1, 1),
        },
        {
            "5f5b940f60a37c2b4012b973": 10,
            "5f5b940f60a37c2b4012b974": 80,
            "timestamp": datetime(2023, 1, 1, 1, 2, 1, 1),
        },
    ]
    db_mock.get_docs = MagicMock(return_value=powers)
    res = checker_instance._get_powers()
    expected_res = [
        {
            "5f5b940f60a37c2b4012b973": 100,
            "5f5b940f60a37c2b4012b974": 8,
            "timestamp": datetime(2023, 1, 1, 1, 1),
        },
        {
            "5f5b940f60a37c2b4012b973": 10,
            "5f5b940f60a37c2b4012b974": 80,
            "timestamp": datetime(2023, 1, 1, 1, 2),
        },
    ]
    expected_res = pd.DataFrame(expected_res)
    expected_res["timestamp"] = pd.to_datetime(expected_res["timestamp"])
    expected_res = expected_res.set_index("timestamp")
    assert res.equals(expected_res)


@pytest.mark.parametrize(
    ("cur_time", "goal", "peak", "baseline"),
    (
        (datetime(2023, 2, 3, 4, 2), False, False, False),
        (datetime(2023, 2, 3, 0, 0), False, True, True),
        (datetime(2023, 2, 3, 4, 0), False, False, False),
        (datetime(2023, 2, 3, 0, 2), False, False, False),
        (datetime(2023, 2, 1, 0, 0), True, True, True),
        (datetime(2023, 2, 1, 2, 0), False, False, False),
        (datetime(2023, 2, 1, 2, 6), False, False, False),
        (datetime(2023, 2, 1, 0, 4), False, False, False),
    ),
)
def test_reset_flags(checker_instance, cur_time, goal, peak, baseline):
    checker_instance.goal_flags = {
        25: False,
        50: False,
        75: False,
        100: False,
        125: False,
        150: True,
        175: True,
        200: True,
    }
    checker_instance.peak_flags = {
        "5f5b940f60a37c2b4012b976": True,
        "5f5b940f60a37c2b4012b974": False,
    }
    checker_instance.baseline_flags = {
        "5f5b940f60a37c2b4012b976": True,
        "5f5b940f60a37c2b4012b974": False,
    }

    checker_instance._reset_flags(cur_time)
    if goal:
        assert checker_instance.goal_flags == {
            25: True,
            50: True,
            75: True,
            100: True,
            125: True,
            150: True,
            175: True,
            200: True,
        }
    else:
        assert checker_instance.goal_flags != {
            25: True,
            50: True,
            75: True,
            100: True,
            125: True,
            150: True,
            175: True,
            200: True,
        }
    if peak:
        assert checker_instance.peak_flags == {}
    else:
        assert len(checker_instance.peak_flags) > 0
    if baseline:
        assert checker_instance.baseline_flags == {}
    else:
        assert len(checker_instance.baseline_flags) > 0


@pytest.mark.parametrize(
    ("time", "output"),
    (
        (datetime.now(), False),
        (datetime.now() + timedelta(minutes=30), False),
        (datetime.now() - timedelta(hours=1, minutes=1), True),
    ),
)
def test_is_hour_elapsed(checker_instance, time, output):
    app_id = "mocked_id"
    checker_instance.phantom_flags[app_id] = [True, time]
    res = checker_instance._is_hour_elapsed(app_id)
    assert res == output


def test_get_model(checker_instance, model):
    res = checker_instance._get_model("64d1682993d44252699aa22a", "cluster")
    assert pickle.dumps(res) == pickle.dumps(model)

    res = checker_instance._get_model("64d1682993d44252699aa32a", "cluster")
    assert res == False

    res = checker_instance._get_model("64d1682993d44252699aa22a", "cluter")
    assert res == False


@pytest.mark.parametrize(
    ("flag_before", "goal", "percentage", "flag_after", "notified"),
    (
        (True, 1, 25, False, True),
        (True, -1, 25, True, False),
        (True, 1, 0, True, False),
        (True, -1, 0, True, False),
        (False, 1, 25, False, False),
        (False, -1, 25, False, False),
        (False, 1, 0, False, False),
        (False, -1, 0, False, False),
    ),
)
def test_notify_goal(
    checker_instance, flag_before, goal, percentage, flag_after, notified, monkeypatch
):
    user = {"energy_goal": goal, "current_month_energy": 0}
    checker_instance.goal_flags[25] = flag_before
    monkeypatch.setattr(EPR, "check_goal", MagicMock(return_value=percentage))
    count = checker_instance.fcm.notify.call_count

    checker_instance._notify_goal(user, 0)

    assert checker_instance.goal_flags[25] == flag_after
    if notified:
        assert checker_instance.fcm.notify.call_count == count + 1
    else:
        assert checker_instance.fcm.notify.call_count == count


@pytest.mark.parametrize(
    ("flag_before", "peak", "flag_after", "notified"),
    (
        (True, True, False, True),
        (True, False, True, False),
        (False, True, False, False),
        (False, False, False, False),
    ),
)
def test_notify_peak(
    checker_instance, flag_before, peak, flag_after, notified, monkeypatch
):
    app_id = "mocked_id"
    app = {"status": True, "e_type": EType.SHIFTABLE, "name": "mocked_name"}

    checker_instance.peak_flags[app_id] = flag_before
    monkeypatch.setattr(EPR, "check_peak", MagicMock(return_value=peak))
    count = checker_instance.fcm.notify.call_count

    checker_instance._notify_peak(app_id, app)

    assert checker_instance.peak_flags[app_id] == flag_after
    if notified:
        assert checker_instance.fcm.notify.call_count == count + 1
    else:
        assert checker_instance.fcm.notify.call_count == count


@pytest.mark.parametrize(
    ("flag_before", "is_hour_elapsed", "phantom", "flag_after", "notified"),
    (
        (True, True, True, False, True),
        (True, False, True, False, True),
        (True, True, False, True, False),
        (True, False, False, True, False),
        (False, True, True, False, True),
        (False, False, True, False, False),
        (False, True, False, True, False),
        (False, False, False, False, False),
    ),
)
def test_notify_phantom(
    checker_instance,
    model,
    flag_before,
    is_hour_elapsed,
    phantom,
    flag_after,
    notified,
    monkeypatch,
):
    app_id = "mocked_id"
    app = {"status": True, "name": "mocked_name"}
    checker_instance._get_model = MagicMock(return_value=model)
    checker_instance.phantom_flags[app_id] = [flag_before, datetime.now()]
    checker_instance._is_hour_elapsed = MagicMock(return_value=is_hour_elapsed)
    monkeypatch.setattr(EPR, "check_phantom", MagicMock(return_value=phantom))
    count = checker_instance.fcm.notify.call_count

    checker_instance._notify_phantom(app_id, app, 0)

    assert checker_instance.phantom_flags[app_id][0] == flag_after
    if notified:
        assert checker_instance.fcm.notify.call_count == count + 1
    else:
        assert checker_instance.fcm.notify.call_count == count


@pytest.mark.parametrize(
    ("flag_before", "threshold", "baseline", "flag_after", "notified"),
    (
        (True, 1, True, False, True),
        (True, -1, True, True, False),
        (True, 1, False, True, False),
        (True, -1, False, True, False),
        (False, 1, True, False, False),
        (False, -1, True, False, False),
        (False, 1, False, False, False),
        (False, -1, False, False, False),
    ),
)
def test_notify_baseline(
    checker_instance,
    flag_before,
    threshold,
    baseline,
    flag_after,
    notified,
    monkeypatch,
):
    data = [
        {
            "5f5b940f60a37c2b4012b973": 100,
            "5f5b940f60a37c2b4012b974": 8,
            "timestamp": datetime(2023, 1, 1, 1, 1, 1, 1),
        },
        {
            "5f5b940f60a37c2b4012b973": 10,
            "5f5b940f60a37c2b4012b974": 80,
            "timestamp": datetime(2023, 1, 1, 1, 2, 1, 1),
        },
    ]
    db_mock.get_docs = MagicMock(return_value=data)
    powers = checker_instance._get_powers()
    app_id = "5f5b940f60a37c2b4012b973"
    app = {"energy": 0, "baseline_threshold": threshold, "name": "mocked_name"}
    checker_instance.baseline_flags[app_id] = flag_before
    monkeypatch.setattr(EPR, "check_baseline", MagicMock(return_value=baseline))
    count = checker_instance.fcm.notify.call_count

    checker_instance._notify_baseline(app_id, app, powers[app_id])

    assert checker_instance.baseline_flags[app_id] == flag_after
    if notified:
        assert checker_instance.fcm.notify.call_count == count + 1
    else:
        assert checker_instance.fcm.notify.call_count == count
