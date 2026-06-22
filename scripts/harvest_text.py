"""
harvest_text.py — Phase 1 Text Corpus Harvester for Luganda AI

Pulls Luganda text from free, public sources and saves them as
ingest_dataset.py-compatible JSON files in data/datasets/harvested/.

Sources (all free, no API key required):
  1. Luganda Wikipedia — article summaries via the Wikipedia REST API
  2. FLORES-200 devtest set — 1,012 parallel EN↔LG sentences from Meta AI
  3. Luganda proverbs + phrases from CommonVoice Luganda sentence corpus

Usage:
    python scripts/harvest_text.py               # run all sources
    python scripts/harvest_text.py --source wiki # one source only
    python scripts/harvest_text.py --dry-run     # preview counts only
    python scripts/harvest_text.py --status      # show what's already harvested

After running, ingest into ChromaDB with:
    python scripts/ingest_dataset.py

Designed to be run nightly from a Windows Scheduled Task.
Each run is idempotent — already-downloaded files are not re-fetched
unless --force is passed.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

# ── Setup ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
HARVEST_DIR = ROOT / "data" / "datasets" / "harvested"
HARVEST_LOG = ROOT / "data" / "datasets" / "harvest_log.jsonl"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("harvest")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _save_dataset(name: str, entries: list[dict], source_meta: dict) -> Path:
    """Save entries as a dataset JSON file compatible with ingest_dataset.py."""
    HARVEST_DIR.mkdir(parents=True, exist_ok=True)
    out_path = HARVEST_DIR / f"{name}.json"
    payload = {
        "metadata": {
            **source_meta,
            "harvested_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
        },
        "entries": entries,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def _log_harvest(source: str, file: str, count: int, status: str, detail: str = ""):
    HARVEST_LOG.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "file": file,
        "count": count,
        "status": status,
        "detail": detail,
    }
    with HARVEST_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _get(url: str, params: dict | None = None, timeout: int = 20) -> Any:
    """GET with retries and polite delay."""
    import requests  # noqa: PLC0415 (local import so script is importable without requests)
    headers = {"User-Agent": "LugandaAI-harvester/1.0 (muganda-corpus-builder)"}
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as exc:
            if attempt == 2:
                raise
            log.warning(f"  Retry {attempt + 1}/3 for {url}: {exc}")
            time.sleep(2 ** attempt)


# ── Source 1: Luganda Wikipedia ───────────────────────────────────────────────
WIKI_API = "https://lg.wikipedia.org/w/api.php"
WIKI_CATEGORIES = [
    "Uganda", "Ebigambo", "Obuwangwa", "Ensi", "Abantu", "Ebyobulimi",
    "Ebyomuzannyo", "Ebyempuliziganya", "Ebyobusuubuzi", "Ebyenjigiriza",
    "Obulamu", "Ebyobulimi_bw'Amayinja", "Emizannyo", "Ebyekulaakulana",
]
WIKI_MAX_ARTICLES = 120  # articles per run (summaries only — fast)


def harvest_wikipedia(force: bool = False, dry_run: bool = False) -> int:
    """
    Fetch article summaries from lg.wikipedia.org.
    Each summary becomes one EN↔LG entry (title as English hint,
    Luganda extract as the Luganda text).

    Returns number of new entries saved.
    """
    today = date.today().isoformat()
    out_name = f"wikipedia_lg_{today}"
    out_path = HARVEST_DIR / f"{out_name}.json"

    if out_path.exists() and not force:
        log.info(f"[wikipedia] Already harvested today ({out_path.name}). Use --force to re-fetch.")
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        return existing["metadata"].get("entry_count", 0)

    log.info("[wikipedia] Fetching article list from lg.wikipedia.org …")
    entries: list[dict] = []
    seen_titles: set[str] = set()

    # Pull random sample of recent articles + a fixed set of topical ones
    # Strategy: use allpages + random to get diverse coverage
    params = {
        "action": "query",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 50,
        "format": "json",
    }
    try:
        r = _get(WIKI_API, params=params)
        pages = r.json().get("query", {}).get("random", [])
    except Exception as exc:
        log.error(f"[wikipedia] Failed to get article list: {exc}")
        _log_harvest("wikipedia", out_name, 0, "error", str(exc))
        return 0

    titles = [p["title"] for p in pages if p["title"] not in seen_titles]
    seen_titles.update(titles)

    # Also pull from "Special:Export" for a few key categories
    # via opensearch to fill up to WIKI_MAX_ARTICLES
    more_params = {
        "action": "query",
        "list": "allpages",
        "aplimit": max(0, WIKI_MAX_ARTICLES - len(titles)),
        "apfrom": "A",
        "apnamespace": 0,
        "format": "json",
    }
    try:
        r2 = _get(WIKI_API, params=more_params)
        more_pages = r2.json().get("query", {}).get("allpages", [])
        for p in more_pages:
            if p["title"] not in seen_titles:
                titles.append(p["title"])
                seen_titles.add(p["title"])
    except Exception:
        pass  # random articles are enough

    titles = titles[:WIKI_MAX_ARTICLES]
    log.info(f"[wikipedia] Found {len(titles)} article titles to process")

    if dry_run:
        log.info(f"[wikipedia] DRY RUN — would fetch {len(titles)} summaries")
        return len(titles)

    # Fetch summaries in batches of 20
    BATCH = 20
    for i in range(0, len(titles), BATCH):
        batch = titles[i : i + BATCH]
        summary_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": "|".join(batch),
            "format": "json",
        }
        try:
            r = _get(WIKI_API, params=summary_params)
            pages_data = r.json().get("query", {}).get("pages", {})
        except Exception as exc:
            log.warning(f"[wikipedia] Batch {i//BATCH+1} failed: {exc}")
            continue

        for page in pages_data.values():
            title = page.get("title", "")
            extract = (page.get("extract") or "").strip()
            if not extract or len(extract) < 20:
                continue
            # Split into sentences (rough split on ። ۔ . \n)
            import re
            raw_sentences = re.split(r"[.\n]+", extract)
            for sent in raw_sentences:
                sent = sent.strip()
                if len(sent) < 15 or len(sent) > 400:
                    continue
                # We store the Luganda sentence; title provides context
                entries.append({
                    "luganda": sent,
                    "english": "",  # no parallel English — mark for translation
                    "category": "wikipedia",
                    "subcategory": "article_extract",
                    "source": f"lg.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    "notes": f"From article: {title}",
                    "needs_review": True,
                    "data_type": "sentences",
                })
        time.sleep(0.5)  # polite rate limiting

    if not entries:
        log.warning("[wikipedia] No entries extracted — check network or Wikipedia availability")
        _log_harvest("wikipedia", out_name, 0, "empty")
        return 0

    out_path = _save_dataset(out_name, entries, {
        "source": "Luganda Wikipedia",
        "category": "sentences",
        "description": f"Article extracts from lg.wikipedia.org harvested {today}",
        "url": "https://lg.wikipedia.org",
        "license": "CC BY-SA 4.0",
    })

    log.info(f"[wikipedia] Saved {len(entries)} sentences → {out_path.name}")
    _log_harvest("wikipedia", out_name, len(entries), "ok")
    return len(entries)


# ── Source 2: FLORES-200 Luganda sentences ───────────────────────────────────
FLORES_URL = "https://raw.githubusercontent.com/openlanguagedata/flores/main/flores200/data/devtest/devtest.lug_Latn"
FLORES_EN_URL = "https://raw.githubusercontent.com/openlanguagedata/flores/main/flores200/data/devtest/devtest.eng_Latn"
FLORES_OUT = "flores200_luganda"


def harvest_flores(force: bool = False, dry_run: bool = False) -> int:
    """
    Download FLORES-200 devtest sentences for Luganda (lug_Latn).
    1,012 parallel EN↔LG sentences from Meta AI — MIT license.
    Only downloaded once (it doesn't change).
    """
    out_path = HARVEST_DIR / f"{FLORES_OUT}.json"
    if out_path.exists() and not force:
        log.info(f"[flores] Already downloaded ({out_path.name}). Use --force to re-fetch.")
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        return existing["metadata"].get("entry_count", 0)

    log.info("[flores] Downloading FLORES-200 Luganda sentences …")

    if dry_run:
        log.info("[flores] DRY RUN — would download ~1,012 parallel EN↔LG sentences")
        return 1012

    try:
        lg_resp = _get(FLORES_URL)
        en_resp = _get(FLORES_EN_URL)
    except Exception as exc:
        log.error(f"[flores] Download failed: {exc}")
        _log_harvest("flores200", FLORES_OUT, 0, "error", str(exc))
        return 0

    lg_lines = [l.strip() for l in lg_resp.text.splitlines() if l.strip()]
    en_lines = [l.strip() for l in en_resp.text.splitlines() if l.strip()]

    if not lg_lines:
        log.warning("[flores] Empty response — FLORES URL may have moved")
        _log_harvest("flores200", FLORES_OUT, 0, "empty")
        return 0

    entries = []
    for i, (lg, en) in enumerate(zip(lg_lines, en_lines), start=1):
        entries.append({
            "id": f"flores_dev_{i:04d}",
            "luganda": lg,
            "english": en,
            "category": "sentences",
            "subcategory": "flores200",
            "source": "FLORES-200 devtest",
            "notes": "Parallel sentence from FLORES-200 benchmark dataset (Meta AI, MIT license)",
            "needs_review": False,
            "data_type": "sentences",
        })

    out_path = _save_dataset(FLORES_OUT, entries, {
        "source": "FLORES-200",
        "category": "sentences",
        "description": "1,012 parallel English-Luganda sentences from the FLORES-200 benchmark",
        "url": "https://github.com/openlanguagedata/flores",
        "license": "MIT",
        "parallel": True,
    })

    log.info(f"[flores] Saved {len(entries)} parallel sentence pairs → {out_path.name}")
    _log_harvest("flores200", FLORES_OUT, len(entries), "ok")
    return len(entries)


# ── Source 3: CommonVoice Luganda sentence list ───────────────────────────────
# Mozilla CommonVoice has a public Luganda sentence corpus.
# We use the GitHub mirror (cc0 license).
CV_URL = "https://raw.githubusercontent.com/common-voice/common-voice/main/sentences/lg.txt"
CV_OUT = "commonvoice_luganda_sentences"


def harvest_commonvoice(force: bool = False, dry_run: bool = False) -> int:
    """
    Download Luganda sentences from Mozilla CommonVoice corpus.
    These are crowd-sourced Luganda sentences for speech — good training fodder.
    License: CC0.
    """
    out_path = HARVEST_DIR / f"{CV_OUT}.json"
    if out_path.exists() and not force:
        log.info(f"[commonvoice] Already downloaded ({out_path.name}). Use --force to re-fetch.")
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        return existing["metadata"].get("entry_count", 0)

    log.info("[commonvoice] Downloading CommonVoice Luganda sentences …")

    if dry_run:
        log.info("[commonvoice] DRY RUN — would download CV Luganda sentence list")
        return 0

    try:
        r = _get(CV_URL)
    except Exception as exc:
        log.error(f"[commonvoice] Download failed: {exc}")
        _log_harvest("commonvoice", CV_OUT, 0, "error", str(exc))
        return 0

    lines = [l.strip() for l in r.text.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        log.warning("[commonvoice] Empty response — URL may have changed or no Luganda sentences yet")
        _log_harvest("commonvoice", CV_OUT, 0, "empty")
        return 0

    entries = []
    for i, sent in enumerate(lines, start=1):
        entries.append({
            "id": f"cv_lg_{i:05d}",
            "luganda": sent,
            "english": "",
            "category": "sentences",
            "subcategory": "commonvoice",
            "source": "Mozilla CommonVoice Luganda",
            "notes": "Luganda sentence from Mozilla CommonVoice corpus (CC0 license)",
            "needs_review": True,
            "data_type": "sentences",
        })

    out_path = _save_dataset(CV_OUT, entries, {
        "source": "Mozilla CommonVoice",
        "category": "sentences",
        "description": "Luganda sentences contributed to Mozilla CommonVoice",
        "url": "https://commonvoice.mozilla.org/lg",
        "license": "CC0",
    })

    log.info(f"[commonvoice] Saved {len(entries)} sentences → {out_path.name}")
    _log_harvest("commonvoice", CV_OUT, len(entries), "ok")
    return len(entries)


# ── Source 4: Open parallel corpus (OPUS CCAligned) ─────────────────────────
# OPUS has a TSV mirror for many low-resource language pairs
OPUS_URL = "https://object.pouta.csc.fi/OPUS-CCAligned/v1/moses/en-lg.txt.zip"
OPUS_OUT = "opus_ccaligned_enlg"


def harvest_opus(force: bool = False, dry_run: bool = False) -> int:
    """
    Download OPUS CCAligned English-Luganda parallel corpus.
    This can be several thousand sentence pairs.
    License: varies by source, generally CC.
    """
    import io
    import zipfile

    out_path = HARVEST_DIR / f"{OPUS_OUT}.json"
    if out_path.exists() and not force:
        log.info(f"[opus] Already downloaded ({out_path.name}). Use --force to re-fetch.")
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        return existing["metadata"].get("entry_count", 0)

    log.info("[opus] Downloading OPUS CCAligned EN-LG corpus (may be a few MB) …")

    if dry_run:
        log.info("[opus] DRY RUN — would download OPUS CCAligned EN-LG parallel corpus")
        return 0

    try:
        r = _get(OPUS_URL, timeout=60)
    except Exception as exc:
        log.error(f"[opus] Download failed: {exc}")
        _log_harvest("opus_ccaligned", OPUS_OUT, 0, "error", str(exc))
        return 0

    try:
        zf = zipfile.ZipFile(io.BytesIO(r.content))
        # Expect two files: CCAligned.en-lg.en and CCAligned.en-lg.lg
        names = zf.namelist()
        en_file = next((n for n in names if n.endswith(".en")), None)
        lg_file = next((n for n in names if n.endswith(".lg")), None)
        if not en_file or not lg_file:
            log.warning(f"[opus] Unexpected zip contents: {names}")
            _log_harvest("opus_ccaligned", OPUS_OUT, 0, "empty", str(names))
            return 0
        en_lines = zf.read(en_file).decode("utf-8", errors="ignore").splitlines()
        lg_lines = zf.read(lg_file).decode("utf-8", errors="ignore").splitlines()
    except Exception as exc:
        log.error(f"[opus] Failed to parse zip: {exc}")
        _log_harvest("opus_ccaligned", OPUS_OUT, 0, "error", str(exc))
        return 0

    entries = []
    for i, (en, lg) in enumerate(zip(en_lines, lg_lines), start=1):
        en = en.strip()
        lg = lg.strip()
        if not en or not lg:
            continue
        entries.append({
            "id": f"opus_cc_{i:06d}",
            "luganda": lg,
            "english": en,
            "category": "sentences",
            "subcategory": "opus_ccaligned",
            "source": "OPUS CCAligned EN-LG",
            "notes": "Parallel sentence pair from OPUS CCAligned corpus",
            "needs_review": True,  # CCAligned is noisy — flag for review
            "data_type": "sentences",
        })

    out_path = _save_dataset(OPUS_OUT, entries, {
        "source": "OPUS CCAligned",
        "category": "sentences",
        "description": "English-Luganda parallel sentences from OPUS CCAligned corpus",
        "url": "https://opus.nlpl.eu/CCAligned.php",
        "license": "Various CC licenses",
        "parallel": True,
        "needs_review": True,
    })

    log.info(f"[opus] Saved {len(entries)} parallel pairs → {out_path.name}")
    _log_harvest("opus_ccaligned", OPUS_OUT, len(entries), "ok")
    return len(entries)


# ── Status ───────────────────────────────────────────────────────────────────
def show_status():
    """Show what's already in the harvested folder."""
    if not HARVEST_DIR.exists():
        print("No harvested data yet. Run harvest_text.py to start.")
        return

    files = sorted(HARVEST_DIR.glob("*.json"))
    if not files:
        print("Harvested folder exists but is empty.")
        return

    total = 0
    print(f"\n{'File':<50} {'Entries':>8}  {'Harvested'}")
    print("-" * 80)
    for f in files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            n = d.get("metadata", {}).get("entry_count", len(d.get("entries", [])))
            ts = d.get("metadata", {}).get("harvested_at", "?")[:10]
            print(f"  {f.name:<48} {n:>8}  {ts}")
            total += n
        except Exception:
            print(f"  {f.name:<48} {'?':>8}")
    print("-" * 80)
    print(f"  {'TOTAL':<48} {total:>8}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────
SOURCES = {
    "wiki": ("Luganda Wikipedia", harvest_wikipedia),
    "flores": ("FLORES-200", harvest_flores),
    "commonvoice": ("CommonVoice", harvest_commonvoice),
    "opus": ("OPUS CCAligned", harvest_opus),
}


def main():
    parser = argparse.ArgumentParser(description="Harvest Luganda text corpus")
    parser.add_argument(
        "--source",
        choices=list(SOURCES.keys()) + ["all"],
        default="all",
        help="Which source to harvest (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="Re-fetch even if file exists")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no writes")
    parser.add_argument("--status", action="store_true", help="Show what's already harvested")
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    selected = list(SOURCES.items()) if args.source == "all" else [(args.source, SOURCES[args.source])]

    grand_total = 0
    log.info(f"=== Luganda Text Harvester — {date.today()} ===")
    log.info(f"Sources: {[k for k, _ in selected]}")
    if args.dry_run:
        log.info("DRY RUN — no files will be written")

    for key, (label, fn) in selected:
        log.info(f"\n--- {label} ---")
        try:
            n = fn(force=args.force, dry_run=args.dry_run)
            grand_total += n
            log.info(f"  → {n} entries")
        except Exception as exc:
            log.error(f"  {label} failed: {exc}")

    log.info(f"\n=== TOTAL new entries: {grand_total} ===")
    if not args.dry_run and grand_total > 0:
        log.info("Next step: run  python scripts/ingest_dataset.py  to load into ChromaDB")


if __name__ == "__main__":
    main()
