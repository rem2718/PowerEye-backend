from unittest.mock import Mock
import os

from dotenv import load_dotenv
import firebase_admin
import pytest

from app.external_dependencies.fcm import FCM
from app.types_classes import NotifType

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture(scope="module")
def fcm_instance():
    CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    mock_db = Mock()
    token = "ffxuhXsmQNyat_DXn5y_Ix:APA91bFDh9cJisILPz9HoUsXe53y04xwugYS8Ze8zBFko6U5oZLWKqhwfWXvIAX6JziHLyllXFECZuS0T7nk28S2djRsOyLBoCmFcU6iSN2D0l1_aQUhDxTpOWvTHjk6LISM994hfApq"
    mock_db.get_doc.return_value = {
        "notified_devices": [
            {"device_id": "dev1", "fcm_token": token},
            {"device_id": "dev2", "fcm_token": "invalid_token"},
        ]
    }
    return FCM(CRED, mock_db)


@pytest.mark.parametrize(
    ("type", "data", "output"),
    (
        (
            NotifType.CREDS,
            None,
            (
                "Update Your Password",
                "Please update your login information for Meross.",
            ),
        ),
        (
            NotifType.DISCONNECTION,
            {"app_name": "tv"},
            (
                "We can't reach your smart plug!",
                "Your tv is currently disconnected. Check its connection and fix it for better recommendations",
            ),
        ),
        (
            NotifType.GOAL,
            {"percentage": 25},
            (
                "Monthly Energy Goal",
                "You're close to reach 25% of your monthly energy goal.",
            ),
        ),
        (
            NotifType.PEAK,
            {"app_name": "tv"},
            (
                "Peak Usage Alert!",
                "Try to postpone using tv after 5 PM. Click here to turn it off.",
            ),
        ),
        (
            NotifType.PHANTOM,
            {"app_name": "tv"},
            (
                "Phantom Mode Active!",
                "tv is in phantom mode. Click here to turn it off.",
            ),
        ),
        (
            NotifType.BASELINE,
            {"app_name": "tv"},
            (
                "Appliance Energy Consumption Increased!",
                "tv is used more than it should today. Try to use it less.",
            ),
        ),
    ),
)
def test_map_message(fcm_instance, type, data, output):
    assert fcm_instance.map_message(type, data) == output


def test_notify(fcm_instance):
    responses = fcm_instance.notify(
        "64d1638293d44252699aa21e", NotifType.PEAK, {"app_name": "tv"}
    )
    assert "powereye1-e599e" in responses[0]
    assert not responses[1]


def test_fcm_cleanup(fcm_instance):
    app = firebase_admin.get_app()
    firebase_admin.delete_app(app)
    del fcm_instance
    assert True
