import os

from dotenv import load_dotenv
import pytest

from app.external_dependencies.tuya_module import Tuya

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture(scope="module")
def tuya_instance():
    dev1 = os.getenv("TEST_DEV1")
    tuya = Tuya({"dev1": dev1})
    return tuya


@pytest.fixture(scope="module")
def dev(tuya_instance):
    tuya_instance.login()
    dev = tuya_instance.get_devices()[0]
    return dev


def test_update_creds(tuya_instance):
    pass


def login(tuya_instance):
    res = tuya_instance.login()
    assert res


def test_get_devices(tuya_instance):
    tuya_instance.login()
    res = tuya_instance.get_devices()
    assert len(res) > 0
    assert isinstance(res, list)


def test_get_id(tuya_instance, dev):
    res = tuya_instance.get_id(dev)
    assert isinstance(res, str)


def test_get_info(tuya_instance, dev):
    on_off, connection_status, power = tuya_instance.get_info(dev)
    assert isinstance(on_off, bool)
    assert isinstance(connection_status, bool)
    assert isinstance(power, float)
    assert power >= 0
