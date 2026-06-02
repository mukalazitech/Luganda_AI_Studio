# backend/services/tts/mms_tts_service.py

"""
Meta MMS TTS service for Luganda.

Model: facebook/mms-tts-lug
- Luganda-specific voice (real language, not a generic Latin voice)
- CPU-capable, no VRAM required
- ~few hundred MB download
- Lazy-loaded on first request (same pattern as nllb_service.py)

First call: 5–15 s (model loading)
Subsequent: 1–2 s on CPU (instant on cache hit)
"""

import hashlib
import io
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import torch

logger = logging.getLogger(__name__)

MODEL_NAME = "facebook/mms-tts-lug"

# Disk cache: data/tts_cache/<sha256_of_text>.wav
# Keeps WAV files between server restarts so common words are always instant.
_CACHE_DIR = Path(__file__).resolve().parents[4] / "data" / "tts_cache"


def _cache_path(text: str) -> Path:
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return _CACHE_DIR / f"{key}.wav"


class MMSTTSService:
    """Lazy-loaded wrapper around facebook/mms-tts-lug with disk-based WAV cache."""

    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        if self._model is not None:
            return
        logger.info(f"[MMS-TTS] Loading model {MODEL_NAME} — this takes ~10s on first run")
        from transformers import VitsModel, VitsTokenizer
        self._tokenizer = VitsTokenizer.from_pretrained(MODEL_NAME)
        self._model = VitsModel.from_pretrained(MODEL_NAME)
        self._model.eval()
        logger.info("[MMS-TTS] Model loaded")

    def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize Luganda text into WAV bytes.
        Returns cached bytes immediately if this text was synthesized before.
        Returns None if synthesis fails.
        """
        # CHANGED: check disk cache before hitting the model
        path = _cache_path(text)
        if path.exists():
            logger.debug(f"[MMS-TTS] Cache hit: '{text[:40]}'")
            return path.read_bytes()

        try:
            self._load()

            with torch.no_grad():
                inputs = self._tokenizer(text, return_tensors="pt")
                output = self._model(**inputs).waveform

            # output[0] selects first batch item; squeeze removes any remaining singleton dims
            waveform = output[0].squeeze().cpu().numpy().astype(np.float32)
            sample_rate = self._model.config.sampling_rate

            wav_bytes = _to_wav_bytes(waveform, sample_rate)

            # CHANGED: persist to disk cache for future requests
            path.write_bytes(wav_bytes)
            logger.debug(f"[MMS-TTS] Cached: '{text[:40]}' → {path.name}")

            return wav_bytes

        except Exception as e:
            logger.error(f"[MMS-TTS] Synthesis failed: {e}", exc_info=True)
            return None


def _to_wav_bytes(waveform: np.ndarray, sample_rate: int) -> bytes:
    """Convert a float32 numpy waveform array to WAV bytes."""
    import scipy.io.wavfile as wavfile

    # Clip to [-1, 1] before scaling — VITS output can exceed this range
    pcm = np.clip(waveform, -1.0, 1.0)
    pcm = (pcm * 32767).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, pcm)
    return buf.getvalue()


mms_tts_service = MMSTTSService()
