from apscheduler.schedulers.blocking import BlockingScheduler
import firebase_admin
import pytest

from tests.integration.fixtures import db_instance, fcm_instance
from app.tasks.master import Master


@pytest.fixture(scope="module")
def master_instance(db_instance, fcm_instance):
    master = Master("", db_instance, fcm_instance, BlockingScheduler())
    return master


def test_master(master_instance, db_instance):
    users = db_instance.get_docs("Users")
    ids = [
        str(user["_id"])
        for user in users
        if not user["is_deleted"] and len(user["appliances"])
    ]
    job_names = ["collector_", "checker_", "updater_"]

    master_instance.run()

    jobs = master_instance.scheduler.get_jobs()
    job_ids = [job.id for job in jobs]
    for id in ids:
        for name in job_names:
            job_name = name + id
            assert job_name in job_ids


def test_fcm_cleanup(fcm_instance):
    app = firebase_admin.get_app()
    firebase_admin.delete_app(app)
    del fcm_instance
    assert True
