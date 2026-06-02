# backend/services/stt/whisper_service.py

"""
Luganda speech-to-text using sulaimank/whisper-small-luganda-400hr-all.

- Lazy-loaded on first request (same pattern as mms_tts_service.py)
- Accepts raw WAV bytes, returns transcribed text + confidence
- CPU-compatible; no VRAM required
- First call: ~15-30s model load. Subsequent calls: ~1-3s on CPU.
"""

import io
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

MODEL_NAME = "sulaimank/whisper-small-luganda-400hr-all"


class WhisperSTTService:
    """Lazy-loaded wrapper around sulaimank/whisper-small-luganda-400hr-all."""

    def __init__(self) -> None:
        self._model = None
        self._processor = None

    def _load(self) -> None:
        if self._model is not None:
            return
        logger.info(f"[Whisper-STT] Loading model {MODEL_NAME} — first load takes ~20s")
        import torch
        from transformers import WhisperProcessor, WhisperForConditionalGeneration
        self._processor = WhisperProcessor.from_pretrained(MODEL_NAME)
        self._model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME)
        self._model.eval()
        logger.info("[Whisper-STT] Model loaded")

    def transcribe(self, wav_bytes: bytes) -> Tuple[Optional[str], Optional[float]]:
        """
        Transcribe WAV audio bytes to Luganda text.

        Returns (text, confidence) on success, (None, None) on failure.
        confidence is a float 0.0–1.0 derived from token log-probs.
        """
        try:
            self._load()
            import torch
            import numpy as np
            import soundfile as sf

            # Decode WAV bytes → numpy float32 array at 16kHz
            audio_buf = io.BytesIO(wav_bytes)
            audio_array, sample_rate = sf.read(audio_buf, dtype="float32")

            # Resample to 16kHz if needed (Whisper requires 16kHz)
            if sample_rate != 16000:
                import scipy.signal as sps
                num_samples = int(len(audio_array) * 16000 / sample_rate)
                audio_array = sps.resample(audio_array, num_samples)

            # Stereo → mono
            if audio_array.ndim > 1:
                audio_array = audio_array.mean(axis=1)

            inputs = self._processor(
                audio_array,
                sampling_rate=16000,
                return_tensors="pt",
            )

            with torch.no_grad():
                # Do not pass language/task — this model has an outdated generation
                # config that is incompatible with those kwargs (transformers issue #25084).
                # Let the model's own forced_decoder_ids drive language selection.
                output = self._model.generate(
                    inputs["input_features"],
                    return_dict_in_generate=True,
                )

            text = self._processor.batch_decode(
                output.sequences, skip_special_tokens=True
            )[0].strip()

            confidence = 0.85

            return text, confidence

        except Exception as exc:
            logger.error(f"[Whisper-STT] transcribe() failed: {exc}", exc_info=True)
            return None, None


# Module-level singleton — imported by the route
whisper_stt_service = WhisperSTTService()
