from unittest.mock import MagicMock
import asyncio
import os

from dotenv import load_dotenv
import pytest

from scheduler import Scheduler

load_dotenv(os.path.join(".secrets", ".env"))


@pytest.fixture
def scheduler_instance():
    db = MagicMock()
    fcm = MagicMock()
    scheduler = Scheduler(db, fcm)
    scheduler.scheduler = MagicMock()
    return scheduler

def test_scheduler_run(scheduler_instance):
    scheduler_instance.run()
    asyncio.get_event_loop().stop()
    scheduler_instance.scheduler.shutdown()
    scheduler_instance.scheduler.add_job.assert_called()
    scheduler_instance.scheduler.start.assert_called()
