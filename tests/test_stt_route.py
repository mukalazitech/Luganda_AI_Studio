import base64
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Minimal valid WAV header (44 bytes) + 1 second of silence at 16kHz
import struct

def _make_wav_bytes(num_samples: int = 16000) -> bytes:
    """Build a minimal mono 16kHz 16-bit WAV in memory."""
    data = b"\x00\x00" * num_samples
    data_size = len(data)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16, 1, 1, 16000, 32000, 2, 16,
        b"data", data_size,
    )
    return header + data


VALID_B64 = base64.b64encode(_make_wav_bytes()).decode()


def test_stt_returns_200_with_valid_audio():
    with patch(
        "backend.api.routes.stt.whisper_stt_service.transcribe",
        return_value=("Oli otya", 0.91),
    ):
        with patch("backend.api.routes.stt._save_recording"):
            response = client.post(
                "/api/v1/stt",
                json={"audio": VALID_B64, "source": "translate"},
            )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Oli otya"
    assert data["confidence"] == 0.91


def test_stt_returns_400_for_empty_audio():
    response = client.post("/api/v1/stt", json={"audio": "", "source": "translate"})
    assert response.status_code == 400


def test_stt_returns_400_for_invalid_base64():
    response = client.post("/api/v1/stt", json={"audio": "not-valid-base64!!!", "source": "translate"})
    assert response.status_code == 400


def test_stt_returns_400_for_too_small_payload():
    tiny = base64.b64encode(b"too small").decode()
    response = client.post("/api/v1/stt", json={"audio": tiny, "source": "translate"})
    assert response.status_code == 400


def test_stt_returns_503_when_transcription_fails():
    with patch(
        "backend.api.routes.stt.whisper_stt_service.transcribe",
        return_value=(None, None),
    ):
        response = client.post(
            "/api/v1/stt",
            json={"audio": VALID_B64, "source": "translate"},
        )
    assert response.status_code == 503


def test_stt_saves_recording_on_success(tmp_path):
    rec_dir = tmp_path / "recordings"
    log_file = tmp_path / "transcription_log.jsonl"

    with patch(
        "backend.api.routes.stt.whisper_stt_service.transcribe",
        return_value=("Webale", 0.85),
    ):
        with patch("backend.api.routes.stt.settings") as mock_settings:
            mock_settings.audio_rec_dir = rec_dir
            mock_settings.audio_log_file = log_file
            response = client.post(
                "/api/v1/stt",
                json={"audio": VALID_B64, "source": "teach"},
            )

    assert response.status_code == 200
    wav_files = list(rec_dir.glob("*.wav"))
    assert len(wav_files) == 1
    records = [json.loads(l) for l in log_file.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["transcribed_text"] == "Webale"
    assert records[0]["source"] == "teach"
    assert records[0]["user_confirmed"] is False
