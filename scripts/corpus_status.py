"""
corpus_status.py — Phase 0 baseline + growth tracker for Luganda AI.

Prints a clean snapshot of how much data actually exists:
  - Audio recordings (file count + total duration in minutes/hours, read from WAV headers)
  - Transcriptions (total + how many a human has confirmed/corrected)
  - Training pairs, correction pairs, feedback entries
  - Source dataset rows (vocabulary / sentences / grammar / proverbs)
  - ChromaDB size on disk

Pure standard library — no installs needed. Run it any time to see if the
corpus is actually growing.

Usage:
    python scripts/corpus_status.py
    python scripts/corpus_status.py --json    # machine-readable, for the morning briefing
"""

from __future__ import annotations

import contextlib
import json
import sys
import wave
from pathlib import Path

# Project root = parent of this script's folder (scripts/ -> project root)
ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def count_jsonl_lines(path: Path) -> int:
    """Count non-empty lines in a .jsonl file. 0 if missing."""
    if not path.exists():
        return 0
    n = 0
    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


def wav_duration_seconds(path: Path) -> float:
    """Duration of a WAV file in seconds, read from its header. 0 on failure."""
    try:
        with contextlib.closing(wave.open(str(path), "rb")) as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate:
                return frames / float(rate)
    except Exception:
        pass
    return 0.0


def dir_size_mb(path: Path) -> float:
    """Total size of a directory in MB."""
    if not path.exists():
        return 0.0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            with contextlib.suppress(OSError):
                total += p.stat().st_size
    return total / (1024 * 1024)


def count_dataset_rows(folder: Path) -> tuple[int, int]:
    """
    Return (file_count, approx_row_count) for a dataset source folder.
    Handles JSON (list or dict) and JSONL files.
    """
    if not folder.exists():
        return 0, 0
    files = [p for p in folder.rglob("*") if p.suffix.lower() in {".json", ".jsonl"}]
    rows = 0
    for p in files:
        try:
            if p.suffix.lower() == ".jsonl":
                rows += count_jsonl_lines(p)
            else:
                data = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(data, list):
                    rows += len(data)
                elif isinstance(data, dict):
                    # common shapes: {"items": [...]} / {"pairs": [...]} / flat dict
                    listy = next(
                        (v for v in data.values() if isinstance(v, list)), None
                    )
                    rows += len(listy) if listy is not None else len(data)
        except Exception:
            continue
    return len(files), rows


# --------------------------------------------------------------------------- #
# collect
# --------------------------------------------------------------------------- #
def collect() -> dict:
    audio_dir = ROOT / "data" / "audio" / "recordings"
    wavs = list(audio_dir.glob("*.wav")) if audio_dir.exists() else []
    total_secs = sum(wav_duration_seconds(p) for p in wavs)

    # transcription log: total + human-confirmed/corrected
    tlog = ROOT / "data" / "audio" / "transcription_log.jsonl"
    transcribed = confirmed = 0
    if tlog.exists():
        with tlog.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                transcribed += 1
                try:
                    rec = json.loads(line)
                    if rec.get("user_confirmed") or rec.get("user_correction"):
                        confirmed += 1
                except Exception:
                    pass

    datasets = {}
    for name in ("vocabulary", "sentences", "grammar", "proverbs"):
        f, r = count_dataset_rows(ROOT / "datasets" / name)
        datasets[name] = {"files": f, "rows": r}

    return {
        "audio": {
            "files": len(wavs),
            "minutes": round(total_secs / 60, 1),
            "hours": round(total_secs / 3600, 2),
        },
        "transcriptions": {"total": transcribed, "human_confirmed": confirmed},
        "training_pairs": count_jsonl_lines(
            ROOT / "data" / "training" / "training_pairs.jsonl"
        ),
        "correction_pairs": count_jsonl_lines(
            ROOT / "data" / "training" / "corrections.jsonl"
        ),
        "feedback_entries": count_jsonl_lines(
            ROOT / "data" / "feedback" / "feedback_log.jsonl"
        ),
        "source_datasets": datasets,
        "chromadb_mb": round(dir_size_mb(ROOT / "data" / "chromadb"), 1),
        "knowledge_pdfs": len(
            list((ROOT / "knowledge_base" / "pdfs").glob("*.pdf"))
        ),
    }


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def bar(value: int, target: int, width: int = 24) -> str:
    """Tiny text progress bar toward a target."""
    if target <= 0:
        return ""
    filled = min(width, int(width * value / target))
    return "[" + "#" * filled + "-" * (width - filled) + f"] {value}/{target}"


def render(stats: dict) -> str:
    a = stats["audio"]
    t = stats["transcriptions"]
    lines = [
        "=" * 56,
        "  LUGANDA AI — CORPUS STATUS",
        "=" * 56,
        "",
        "AUDIO",
        f"  recordings        : {a['files']} files",
        f"  total duration    : {a['minutes']} min  ({a['hours']} hrs)",
        f"  toward 20 hrs     : {bar(int(a['minutes']), 20 * 60)}",
        "",
        "TRANSCRIPTION",
        f"  transcribed       : {t['total']}",
        f"  human-confirmed   : {t['human_confirmed']}",
        "",
        "TRAINING DATA",
        f"  training pairs    : {stats['training_pairs']}",
        f"  correction pairs  : {stats['correction_pairs']}",
        f"  toward 500 (LoRA) : {bar(stats['correction_pairs'], 500)}",
        f"  feedback entries  : {stats['feedback_entries']}",
        "",
        "SOURCE DATASETS (rows)",
    ]
    for name, d in stats["source_datasets"].items():
        lines.append(f"  {name:<16}: {d['rows']} rows  ({d['files']} files)")
    lines += [
        "",
        "OTHER",
        f"  chromadb size     : {stats['chromadb_mb']} MB",
        f"  knowledge PDFs    : {stats['knowledge_pdfs']}",
        "",
        "=" * 56,
    ]
    return "\n".join(lines)


def briefing_line(stats: dict) -> str:
    """One-line corpus summary for Hermes morning briefing."""
    a = stats["audio"]
    pairs = stats["correction_pairs"]
    needed = max(0, 500 - pairs)
    total_text = sum(d["rows"] for d in stats["source_datasets"].values())
    return (
        f"Luganda AI corpus: {pairs} training pairs (need {needed} more for LoRA), "
        f"{a['files']} audio files ({a['hours']} hrs), "
        f"{total_text} source dataset rows, ChromaDB {stats['chromadb_mb']} MB."
    )


def main() -> None:
    stats = collect()
    if "--json" in sys.argv:
        print(json.dumps(stats, indent=2))
    elif "--briefing" in sys.argv:
        print(briefing_line(stats))
    else:
        print(render(stats))


if __name__ == "__main__":
    main()
