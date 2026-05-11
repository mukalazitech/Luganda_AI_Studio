# backend/api/routes/stt.py

import base64
import json
import logging
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.services.stt.whisper_service import whisper_stt_service

logger = logging.getLogger(__name__)
router = APIRouter()


class STTRequest(BaseModel):
    audio: str = Field(..., description="Base64-encoded WAV audio")
    source: str = Field("translate", description="'translate' or 'teach'")


class STTResponse(BaseModel):
    text: str
    confidence: float


@router.post("", response_model=STTResponse)
def speech_to_text(request: STTRequest):
    """
    Transcribe base64-encoded WAV audio to Luganda text.

    Saves the WAV file to data/audio/recordings/ and appends a record
    to data/audio/transcription_log.jsonl for dataset collection.

    Errors: 400 if audio is missing/invalid, 503 if model fails.
    """
    if not request.audio:
        raise HTTPException(status_code=400, detail="audio must not be empty")

    # Decode base64 → WAV bytes
    try:
        wav_bytes = base64.b64decode(request.audio)
    except Exception:
        raise HTTPException(status_code=400, detail="audio is not valid base64")

    if len(wav_bytes) < 44:  # WAV header is 44 bytes minimum
        raise HTTPException(status_code=400, detail="audio payload too small to be valid WAV")

    # Transcribe
    text, confidence = whisper_stt_service.transcribe(wav_bytes)

    if text is None:
        raise HTTPException(status_code=503, detail="Transcription failed. Is the Whisper model installed?")

    # Save recording + log
    rec_id = f"rec_{int(time.time() * 1000)}"
    _save_recording(rec_id, wav_bytes, text, confidence, request.source)

    return STTResponse(text=text, confidence=confidence)


def _save_recording(
    rec_id: str,
    wav_bytes: bytes,
    text: str,
    confidence: float,
    source: str,
) -> None:
    """Save WAV file and append to transcription log. Failures are logged, not raised."""
    try:
        rec_dir: Path = settings.audio_rec_dir
        rec_dir.mkdir(parents=True, exist_ok=True)

        wav_path = rec_dir / f"{rec_id}.wav"
        wav_path.write_bytes(wav_bytes)

        log_file: Path = settings.audio_log_file
        log_file.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "id": rec_id,
            "file": str(wav_path),
            "source": source,
            "transcribed_text": text,
            "confidence": round(confidence, 4),
            "user_confirmed": False,
            "user_correction": None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    except Exception as exc:
        logger.error(f"[STT] Failed to save recording {rec_id}: {exc}", exc_info=True)
