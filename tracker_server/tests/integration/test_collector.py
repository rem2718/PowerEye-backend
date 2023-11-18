from bson import ObjectId
import asyncio
import math
import os

from dotenv import load_dotenv
import firebase_admin
import pytest

from tests.integration.fixtures import db_instance, fcm_instance
from app.plug_controller import PlugController
from app.tasks.collector import Collector
from app.types_classes import PlugType

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture(scope="module")
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@pytest.fixture(scope="module")
def tuya_instance(loop):
    dev1 = os.getenv("TEST_DEV1")
    data = {"dev1": dev1, "type": PlugType.TUYA.value}
    plug_controller = PlugController(loop, data)
    return plug_controller


@pytest.fixture(scope="module")
def meross_instance(loop):
    email = os.getenv("TEST_EMAIL")
    data = {"email": email, "type": PlugType.MEROSS.value}
    plug_controller = PlugController(loop, data)
    return plug_controller


@pytest.fixture(scope="module")
def collector_instance_with_tuya(db_instance, fcm_instance, tuya_instance):
    user_id = "64d154d494895e0b4c1bc081"
    collector = Collector(user_id, db_instance, fcm_instance, tuya_instance)
    return collector


@pytest.fixture(scope="module")
def collector_instance_with_meross(db_instance, fcm_instance, meross_instance):
    user_id = "64d1548894895e0b4c1bc07f"
    collector = Collector(user_id, db_instance, fcm_instance, meross_instance)
    return collector


def test_collector_with_tuya(collector_instance_with_tuya, db_instance, tuya_instance):
    min = collector_instance_with_tuya.min
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    app_infos = {}
    tuya_instance.login()
    for app in appliances:
        on_off, connection, power = tuya_instance.get_info({"id": app["cloud_id"]})
        energy = collector_instance_with_tuya._to_energy(app["energy"], power)
        app_infos[str(app["_id"])] = (on_off, connection, power, energy)

    collector_instance_with_tuya.run()

    doc = db_instance.get_doc(
        "Powers",
        {"user": ObjectId("64d154d494895e0b4c1bc081")},
        sort=[("timestamp", -1)],
    )
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d154d494895e0b4c1bc081")})
    appliances = user["appliances"]
    ts = collector_instance_with_tuya.ts.replace(second=0, microsecond=0) - min
    assert doc["timestamp"].replace(second=0, microsecond=0) == ts
    assert all(
        math.isclose(doc[app_id], power)
        for app_id, (_, _, power, _) in app_infos.items()
    )
    assert all(
        app["connection_status"] == app_infos[str(app["_id"])][1] for app in appliances
    )
    assert all(app["status"] == app_infos[str(app["_id"])][0] for app in appliances)
    assert all(app["energy"] == app_infos[str(app["_id"])][3] for app in appliances)


def test_collector_with_meross(
    collector_instance_with_meross, db_instance, meross_instance
):
    min = collector_instance_with_meross.min
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d1548894895e0b4c1bc07f")})
    appliances = user["appliances"]
    app_map = {}
    for app in appliances:
        app_map[app["cloud_id"]] = (str(app["_id"]), app["energy"])
    app_infos = {}
    meross_instance.login(os.getenv("TEST_PASS"))
    devices = meross_instance.get_devices()
    for dev in devices:
        id, prev = app_map[str(dev.uuid)]
        on_off, connection, power = meross_instance.get_info(dev)
        energy = collector_instance_with_meross._to_energy(prev, power)
        app_infos[id] = (on_off, connection, power, energy)

    collector_instance_with_meross.run()

    meross_instance.loop.run_until_complete(meross_instance.plug._logout())
    doc = db_instance.get_doc(
        "Powers",
        {"user": ObjectId("64d1548894895e0b4c1bc07f")},
        sort=[("timestamp", -1)],
    )
    user = db_instance.get_doc("Users", {"_id": ObjectId("64d1548894895e0b4c1bc07f")})
    appliances = user["appliances"]
    ts = collector_instance_with_meross.ts.replace(second=0, microsecond=0) - min

    assert doc["timestamp"].replace(second=0, microsecond=0) == ts
    assert all(
        int(doc[app_id]) == int(power)
        for app_id, (_, _, power, _) in app_infos.items()
        if doc[app_id] is not None and power is not None
    )
    assert all(
        app["connection_status"] == app_infos[str(app["_id"])][1]
        for app in appliances
        if str(app["_id"]) in app_infos
    )
    assert all(
        app["status"] == app_infos[str(app["_id"])][0]
        for app in appliances
        if str(app["_id"]) in app_infos
    )
    assert all(
        int(app["energy"]) == int(app_infos[str(app["_id"])][3])
        for app in appliances
        if str(app["_id"]) in app_infos
    )


def test_fcm_cleanup(fcm_instance):
    app = firebase_admin.get_app()
    firebase_admin.delete_app(app)
    del fcm_instance
    assert True
