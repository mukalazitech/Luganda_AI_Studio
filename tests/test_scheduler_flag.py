from backend.core import config
from backend.main import app


def test_harvest_scheduler_is_disabled_by_default():
    assert config.HARVEST_SCHEDULER_ENABLED is False


def test_disabled_scheduler_does_not_create_task(client):
    assert app.state.harvest_task is None
