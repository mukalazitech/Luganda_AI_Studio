import os
import tempfile

import pytest

# CHANGED: never let tests open or mutate the pilot's live runtime data.
_RUNTIME_DATA = tempfile.TemporaryDirectory(
    prefix="luganda-tests-",
    ignore_cleanup_errors=True,
)
os.environ.setdefault("LUGANDA_DATA_DIR", _RUNTIME_DATA.name)
os.environ.setdefault("HARVEST_SCHEDULER_ENABLED", "false")
os.environ.setdefault("CORRECTION_AUTO_INGEST", "false")

from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_openrouter_state():
    """Reset openrouter_service module state between tests."""
    from backend.services.translation import openrouter_service
    yield
    openrouter_service._last_call_at = None
