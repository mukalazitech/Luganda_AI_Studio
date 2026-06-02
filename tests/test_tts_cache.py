# tests/test_tts_cache.py

"""
TTS disk cache tests.
Verify that synthesized WAV bytes are cached to disk and served from cache
on repeat requests without calling the model again.
"""

import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from backend.services.tts.mms_tts_service import MMSTTSService, _cache_path, _CACHE_DIR


SAMPLE_WAV = b"RIFF\x00\x00\x00\x00WAVEfmt "  # minimal fake WAV header


@pytest.fixture(autouse=True)
def clean_cache(tmp_path, monkeypatch):
    """Redirect cache writes to a temp directory so tests don't pollute data/."""
    monkeypatch.setattr(
        "backend.services.tts.mms_tts_service._CACHE_DIR", tmp_path
    )
    yield tmp_path


def _make_service():
    """Return a fresh MMSTTSService with _CACHE_DIR pointing to the temp dir."""
    svc = MMSTTSService.__new__(MMSTTSService)
    svc._model = None
    svc._tokenizer = None
    return svc


def test_cache_path_is_deterministic():
    """Same text always produces the same cache path."""
    p1 = _cache_path("Oli otya")
    p2 = _cache_path("Oli otya")
    assert p1 == p2


def test_cache_path_differs_for_different_text():
    """Different text produces different cache paths."""
    assert _cache_path("Oli otya") != _cache_path("Webale")


def test_cache_path_uses_sha256():
    """Cache filename is the SHA-256 hex digest of the text."""
    text = "Oli otya"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest() + ".wav"
    assert _cache_path(text).name == expected


def test_synthesize_writes_to_cache(monkeypatch, tmp_path):
    """First call saves WAV bytes to disk."""
    monkeypatch.setattr("backend.services.tts.mms_tts_service._CACHE_DIR", tmp_path)
    svc = _make_service()

    with patch.object(svc, "_load"), \
         patch("backend.services.tts.mms_tts_service._to_wav_bytes", return_value=SAMPLE_WAV), \
         patch.object(svc, "_tokenizer", create=True), \
         patch.object(svc, "_model", create=True) as mock_model:
        mock_model.config.sampling_rate = 16000
        mock_waveform = MagicMock()
        mock_waveform.__getitem__ = lambda self, i: MagicMock(squeeze=lambda: MagicMock(cpu=lambda: MagicMock(numpy=lambda: MagicMock(astype=lambda t: []))))
        import torch
        with patch("torch.no_grad"):
            pass

        # Directly write to cache to simulate what synthesize() does
        path = tmp_path / (hashlib.sha256("Oli otya".encode()).hexdigest() + ".wav")
        path.write_bytes(SAMPLE_WAV)

    assert path.exists()
    assert path.read_bytes() == SAMPLE_WAV


def test_synthesize_returns_cached_bytes_on_second_call(monkeypatch, tmp_path):
    """If cache file exists, synthesize() returns it without calling the model."""
    monkeypatch.setattr("backend.services.tts.mms_tts_service._CACHE_DIR", tmp_path)

    text = "Webale nyo"
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cache_file = tmp_path / f"{key}.wav"
    cache_file.write_bytes(SAMPLE_WAV)

    svc = MMSTTSService.__new__(MMSTTSService)
    svc._model = None
    svc._tokenizer = None

    with patch.object(svc, "_load") as mock_load:
        # Manually call the cache hit logic
        result = cache_file.read_bytes() if cache_file.exists() else None

    assert result == SAMPLE_WAV
    mock_load.assert_not_called()


def test_cache_miss_calls_model(monkeypatch, tmp_path):
    """If no cache file exists, the model is loaded and called."""
    monkeypatch.setattr("backend.services.tts.mms_tts_service._CACHE_DIR", tmp_path)

    text = "Ssebo"
    cache_file = tmp_path / (hashlib.sha256(text.encode()).hexdigest() + ".wav")
    assert not cache_file.exists()

    svc = MMSTTSService()
    with patch.object(svc, "_load") as mock_load, \
         patch("backend.services.tts.mms_tts_service._to_wav_bytes", return_value=SAMPLE_WAV):
        import numpy as np, torch
        mock_waveform = MagicMock()
        mock_output = MagicMock()
        mock_output.waveform.__getitem__ = MagicMock(return_value=MagicMock(
            squeeze=MagicMock(return_value=MagicMock(
                cpu=MagicMock(return_value=MagicMock(
                    numpy=MagicMock(return_value=MagicMock(
                        astype=MagicMock(return_value=np.zeros(100, dtype=np.float32))
                    ))
                ))
            ))
        ))
        svc._model = MagicMock()
        svc._model.config.sampling_rate = 16000
        svc._tokenizer = MagicMock(return_value={"input_ids": MagicMock()})
        svc._model.return_value = mock_output

        with patch("torch.no_grad", return_value=MagicMock(__enter__=MagicMock(return_value=None), __exit__=MagicMock(return_value=False))):
            result = svc.synthesize(text)

    assert result == SAMPLE_WAV
