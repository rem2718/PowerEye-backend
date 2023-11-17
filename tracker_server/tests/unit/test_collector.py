from unittest.mock import Mock, MagicMock
from bson import ObjectId
import math

import pytest

from app.tasks.collector import Collector
from app.types_classes import NotifType


@pytest.fixture(scope="module")
def db_mock():
    db = Mock()
    apps = {
        "cloud_password": "mocked_password",
        "appliances": [
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b971"),
                "cloud_id": "cloud_id1",
                "is_deleted": False,
                "energy": 2.1,
                "name": "app1",
            },
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b972"),
                "cloud_id": "cloud_id2",
                "is_deleted": True,
                "energy": 2.1,
                "name": "app2",
            },
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b973"),
                "cloud_id": "cloud_id3",
                "is_deleted": False,
                "energy": 5,
                "name": "app3",
            },
            {
                "_id": ObjectId("5f5b940f60a37c2b4012b974"),
                "cloud_id": "cloud_id4",
                "is_deleted": False,
                "energy": 0,
                "name": "app4",
            },
        ],
    }
    db.get_doc.return_value = apps
    db.insert_doc = MagicMock()
    db.update_appliances = MagicMock()
    return db


@pytest.fixture(scope="module")
def fcm_mock():
    fcm = Mock()
    fcm.notify = MagicMock()
    return fcm


@pytest.fixture(scope="module")
def plug_mock():
    def mocked_get_info(dev):
        match dev["id"]:
            case "cloud_id1":
                return True, False, 0
            case "cloud_id2":
                return False, True, 2
            case "cloud_id3":
                return True, True, 6000

    plug = Mock()
    plug.update_creds = MagicMock()
    plug.get_devices = MagicMock()
    plug.get_id = MagicMock(side_effect=lambda dev: dev["id"])
    plug.get_info = MagicMock(side_effect=mocked_get_info)
    return plug


@pytest.fixture(scope="module")
def collector_instance(db_mock, fcm_mock, plug_mock):
    collector = Collector("5f5b940f60a37c2b4012b932", db_mock, fcm_mock, plug_mock)
    return collector


@pytest.fixture(scope="module")
def app_map():
    app_map = {
        "cloud_id1": {"id": "5f5b940f60a37c2b4012b971", "name": "app1", "energy": 2.1},
        "cloud_id3": {"id": "5f5b940f60a37c2b4012b973", "name": "app3", "energy": 5},
        "cloud_id4": {"id": "5f5b940f60a37c2b4012b974", "name": "app4", "energy": 0},
    }
    return app_map


def test_get_appliances(collector_instance, app_map):
    res = collector_instance._get_appliances()
    expected_res = app_map
    assert res == expected_res


@pytest.mark.parametrize(
    ("prev_energy", "power", "output"),
    ((3, None, 3), (0, 0, 0), (4.1, 0, 4.1), (0.71, 20, 2131 / 3000)),
)
def test_to_energy(collector_instance, prev_energy, power, output):
    res = collector_instance._to_energy(prev_energy, power)
    assert math.isclose(res, output, rel_tol=1e-9, abs_tol=1e-9)


@pytest.mark.parametrize(
    ("connection_status", "count", "flag_before", "flag_after"),
    (
        (False, 1, [False], False),
        (False, 1, [True, False], False),
        (True, 1, [False], True),
        (False, 2, [True, True], False),
    ),
)
def test_check_disconnected(
    collector_instance, connection_status, count, flag_before, flag_after
):
    id = "5f5b940f60a37c2b4012b932"
    name = "name1"
    type = NotifType.DISCONNECTION
    if flag_before[0]:
        collector_instance.flags[id] = flag_before[1]

    collector_instance._check_disconnected(id, name, connection_status)
    if count == 1:
        collector_instance.fcm.notify.assert_called_once_with(
            id, type, {"app_name": name}
        )
    assert collector_instance.flags[id] == flag_after
    assert collector_instance.fcm.notify.call_count == count


def test_notify_disconnected(collector_instance, app_map):
    id = "5f5b940f60a37c2b4012b932"
    type = NotifType.DISCONNECTION

    apps_ids = ["cloud_id1", "cloud_id3", "cloud_id4"]
    collector_instance.flags = {
        "5f5b940f60a37c2b4012b971": True,
        "5f5b940f60a37c2b4012b974": False,
    }

    updates = collector_instance._notify_disconnected(apps_ids, app_map, [])

    collector_instance.fcm.notify.assert_any_call(id, type, {"app_name": "app1"})
    collector_instance.fcm.notify.assert_any_call(id, type, {"app_name": "app3"})
    assert collector_instance.flags == {
        "5f5b940f60a37c2b4012b971": False,
        "5f5b940f60a37c2b4012b973": False,
        "5f5b940f60a37c2b4012b974": False,
    }
    assert updates == [
        ("5f5b940f60a37c2b4012b971", {"connection_status": False}),
        ("5f5b940f60a37c2b4012b973", {"connection_status": False}),
    ]


def test_get_doc_updates(collector_instance, app_map):
    cloud_devices = [{"id": "cloud_id1"}, {"id": "cloud_id2"}, {"id": "cloud_id3"}]
    collector_instance.flags["5f5b940f60a37c2b4012b974"] = True
    doc, updates = collector_instance._get_doc_updates(cloud_devices, app_map)
    expected_doc = {"5f5b940f60a37c2b4012b971": 0, "5f5b940f60a37c2b4012b973": 6000}
    expected_updates = [
        (
            "5f5b940f60a37c2b4012b971",
            {"status": True, "connection_status": False, "energy": 2.1},
        ),
        (
            "5f5b940f60a37c2b4012b973",
            {"status": True, "connection_status": True, "energy": 5.1},
        ),
        (
            "5f5b940f60a37c2b4012b974",
            {"connection_status": False},
        ),
    ]
    assert doc == expected_doc
    assert updates == expected_updates


def test_save_data(collector_instance):
    id = ObjectId("5f5b940f60a37c2b4012b932")
    doc = {}
    updates = []
    collector_instance._save_data(doc, updates)
    assert doc == {
        "user": id,
        "timestamp": collector_instance.ts - collector_instance.min,
    }


def test_run(collector_instance):
    id = "5f5b940f60a37c2b4012b932"
    type = NotifType.CREDS
    collector_instance.cloud.login.return_value = False

    collector_instance.run()
    collector_instance.fcm.notify.assert_any_call(id, type)
    assert collector_instance.notified == True

    collector_instance.run()
    assert collector_instance.notified == True

    collector_instance.cloud.login.return_value = True
    collector_instance.run()
    assert collector_instance.notified == False
