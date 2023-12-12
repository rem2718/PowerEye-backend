import pytest
import os

from dotenv import load_dotenv

from app.external_dependencies.mongo import Mongo
from app.external_dependencies.fcm import FCM

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture(scope="session")
def db_instance():
    URL = os.getenv("DB_URL")
    database = "test"
    db = Mongo(URL, database)
    return db


@pytest.fixture(scope="package", autouse=True)
def fcm_instance(db_instance):
    CRED = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    fcm = FCM(CRED, db_instance)
    return fcm

