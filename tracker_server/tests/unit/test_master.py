from unittest.mock import MagicMock

from apscheduler.schedulers.blocking import BlockingScheduler
import pytest

from app.tasks.master import Master


@pytest.fixture(scope="module")
def mocked_db():
    db = MagicMock()
    return db


@pytest.fixture(scope="module")
def master_instance(mocked_db):
    fcm = MagicMock()
    scheduler = MagicMock(spec=BlockingScheduler)
    master = Master("test_id", mocked_db, fcm, scheduler)
    return master


def test_create_tasks(master_instance):
    id = "123"
    user_data = {"email": "test@example.com", "type": 1}
    count = master_instance.scheduler.add_job.call_count
    master_instance._create_tasks(id, user_data)

    assert master_instance.scheduler.add_job.call_count == count + 3


@pytest.mark.parametrize(
    ("deleted", "job", "add", "remove"),
    (
        (True, True, 0, 3),
        (True, False, 0, 0),
        (False, True, 0, 0),
        (False, False, 3, 0),
    ),
)
def test_run(master_instance, mocked_db, deleted, job, add, remove):
    user = {
        "_id": "user123",
        "email": "test@example.com",
        "cloud_type": 1,
        "is_deleted": deleted,
        "appliances": [{"cloud_id": "device123"}],
    }
    mocked_db.get_docs.return_value = [user]
    master_instance.scheduler.get_job.return_value = job

    add_count = master_instance.scheduler.add_job.call_count
    remove_count = master_instance.scheduler.remove_job.call_count

    master_instance.run()

    assert master_instance.scheduler.add_job.call_count == add_count + add
    assert master_instance.scheduler.remove_job.call_count == remove_count + remove
