import os
from pathlib import Path

from backend.core import config


def test_runtime_data_uses_the_fixture_isolation_directory():
    # CHANGED: importing the backend during tests must never open repo/data.
    assert config.DATA_DIR == Path(os.environ["LUGANDA_DATA_DIR"]).resolve()
    assert config.CHROMA_PATH == config.DATA_DIR / "chromadb"
    assert config.PROGRESS_FILE == config.DATA_DIR / "progress" / "progress.json"
    assert config.FEEDBACK_DIR == config.DATA_DIR / "feedback"
    assert config.TRAINING_DIR == config.DATA_DIR / "training"
    assert config.EVENTS_DIR == config.DATA_DIR / "events"
    assert config.AUDIO_REC_DIR == config.DATA_DIR / "audio" / "recordings"
