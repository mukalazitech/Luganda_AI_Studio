#!/usr/bin/env python3
"""Transcribe Luganda field audio with indonesian-nlp/wav2vec2-luganda."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import librosa
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


MODEL_ID = "indonesian-nlp/wav2vec2-luganda"
SAMPLE_RATE = 16000
CHUNK_SECONDS = 30
CHUNK_SAMPLES = SAMPLE_RATE * CHUNK_SECONDS
BATCH_SIZE = 4


def mmss(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


def available_output_paths(out_dir: Path, clip_id: str) -> tuple[Path, Path]:
    suffix = ""
    version = 1
    while True:
        md_path = out_dir / f"{clip_id}_raw_wav2vec2{suffix}.md"
        json_path = out_dir / f"{clip_id}_raw_wav2vec2{suffix}.json"
        if not md_path.exists() and not json_path.exists():
            return md_path, json_path
        version += 1
        suffix = f"_v{version}"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", delete=False, dir=str(path.parent)
    ) as handle:
        handle.write(text)
        temp_name = handle.name
    Path(temp_name).rename(path)


def chunk_audio(samples) -> list[tuple[int, float, float, object]]:
    chunks = []
    total_samples = len(samples)
    for index, start_sample in enumerate(range(0, total_samples, CHUNK_SAMPLES)):
        end_sample = min(start_sample + CHUNK_SAMPLES, total_samples)
        if end_sample <= start_sample:
            continue
        chunks.append(
            (
                index,
                start_sample / SAMPLE_RATE,
                end_sample / SAMPLE_RATE,
                samples[start_sample:end_sample],
            )
        )
    return chunks


def transcribe_chunks(chunks, processor, model, device: torch.device) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[offset : offset + BATCH_SIZE]
        audio_arrays = [item[3] for item in batch]
        inputs = processor(
            audio_arrays,
            sampling_rate=SAMPLE_RATE,
            return_tensors="pt",
            padding=True,
        )
        input_values = inputs.input_values.to(device)
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        texts = processor.batch_decode(predicted_ids)
        for (chunk_index, start, end, _audio), text in zip(batch, texts):
            rows.append(
                {
                    "chunk_index": chunk_index,
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "text": " ".join(str(text).split()),
                }
            )
    return rows


def markdown_output(clip_id: str, rows: list[dict[str, object]]) -> str:
    run_date = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    lines = [
        f"# {clip_id} raw wav2vec2 transcript",
        "",
        f"- clip: {clip_id}",
        "- engine: wav2vec2-luganda",
        f"- model: {MODEL_ID}",
        f"- run_date: {run_date}",
        f"- chunk_size_seconds: {CHUNK_SECONDS}",
        "",
    ]
    for row in rows:
        lines.append(f"[@{mmss(float(row['start']))}] {row['text']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio_file", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--clip-id", required=True)
    args = parser.parse_args()

    audio_file = args.audio_file.resolve()
    out_dir = args.out.resolve()
    if not audio_file.exists():
        parser.error(f"audio file not found: {audio_file}")

    samples, _sample_rate = librosa.load(str(audio_file), sr=SAMPLE_RATE, mono=True)
    chunks = chunk_audio(samples)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
    model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID).to(device)
    model.eval()

    rows = transcribe_chunks(chunks, processor, model, device)
    md_path, json_path = available_output_paths(out_dir, args.clip_id)
    atomic_write(md_path, markdown_output(args.clip_id, rows))
    atomic_write(json_path, json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print(f"device={device}")
    print(f"chunks={len(rows)}")
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
