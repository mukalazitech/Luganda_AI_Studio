"""Build the 'All proverbs' browse tier from the raw 5000-proverbs corpus CSV.

Two-step workflow (Phase 1 of plans/2026-07-23-luganda-browse-library-expansion.md):
  1. `--review`  writes datasets/proverbs/_review/all_proverbs_review.json for spot-check.
     This file is OUTSIDE datasets/proverbs/ so the library service never loads it.
  2. `--promote` reads that (possibly hand-edited) review file and writes the live
     datasets/proverbs/all_proverbs.json that the service serves under tier="all".

Source CSV (read-only, never modified): the D: repo's corpus-ingestion output.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_CSV = Path(r"D:\projects\Luganda_AI_Studio\data\csv\groupB_proverbs.csv")
DICTIONARY_CSV = Path(r"D:\projects\Luganda_AI_Studio\data\csv\groupB_dictionary.csv")
CURATED_JSON = WORKTREE_ROOT / "datasets" / "proverbs" / "kiganda_proverbs.json"
REVIEW_DIR = WORKTREE_ROOT / "scripts" / "library" / "review"
REVIEW_PATH = REVIEW_DIR / "all_proverbs_review.json"
PROMOTED_PATH = WORKTREE_ROOT / "datasets" / "proverbs" / "all_proverbs.json"

# Order matters: first matching theme wins. Keywords match against the
# lowercased luganda + english + notes text of each proverb.
THEME_KEYWORDS: list[tuple[str, list[str]]] = [
    ("family", ["mother", "father", "child", "children", "husband", "wife", "family",
                "co-wife", "relative", "relatives", "marry", "marrying", "marriage",
                "parent", "son", "daughter", "home", "house", "household"]),
    ("friendship", ["friend", "friendship", "companion", "neighbour", "neighbor",
                    "love each other", "loves"]),
    ("respect", ["respect", "elder", "elders", "honour", "honor", "shame", "humility",
                 "obey", "visitor", "guest", "host", "hospitable", "hospitality",
                 "polite", "manners"]),
    ("leadership", ["king", "chief", "leader", "ruler", "rule", "authority", "power",
                    "kabaka", "govern"]),
    ("wealth", ["rich", "wealth", "money", "poor", "poverty", "wealthy", "riches",
                "property", "cattle", "cow", "cows", "hunger", "food", "eat", "eating",
                "meat", "banana"]),
    ("caution", ["danger", "careful", "warn", "warning", "beware", "trap", "enemy",
                 "fear", "afraid", "thief", "steal", "stolen", "lie", "lies", "deceive",
                 "cheat", "trouble", "quarrel", "fight", "fights", "fighting"]),
    ("patience", ["patience", "patient", "wait", "waiting", "slow", "slowly", "hurry",
                  "rush", "haste"]),
    ("time", ["time", "morning", "night", "day", "today", "tomorrow", "yesterday",
              "season", "early", "late"]),
    ("hardwork", ["work", "labour", "labor", "effort", "toil", "farm", "farming",
                  "harvest", "plant", "planting", "sow", "reap", "lazy", "laziness"]),
    ("wisdom", ["wise", "wisdom", "fool", "foolish", "know", "knows", "knowledge",
                "understand", "learn", "advice", "truth", "secret", "secrets"]),
    ("community", ["people", "many", "together", "everyone", "each other", "society",
                   "community", "gathered", "crowd"]),
    ("character", ["beautiful", "beauty", "ugly", "appearance", "looks", "character",
                   "behaviour", "behavior"]),
]
DEFAULT_THEME = "general"


def load_source_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.is_file():
        sys.exit(f"Source CSV not found: {SOURCE_CSV}")
    with SOURCE_CSV.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_curated_pairs() -> set[tuple[str, str]]:
    data = json.loads(CURATED_JSON.read_text(encoding="utf-8"))
    return {
        (entry["luganda"].strip().lower(), entry["english"].strip().lower())
        for entry in data["entries"]
    }


def assign_theme(luganda: str, english: str, notes: str) -> str:
    haystack = f"{luganda} {english} {notes}".lower()
    for theme, keywords in THEME_KEYWORDS:
        if any(re.search(rf"\b{re.escape(kw)}\b", haystack) for kw in keywords):
            return theme
    return DEFAULT_THEME


_WORD = re.compile(r"[A-Za-z]{3,}")
# A "prose clause" needs at least one lowercase word of 3+ letters. Citation
# fragments (source abbreviations, page/entry numbers, journal names + years)
# are built from capitalized abbreviations and digits and essentially never
# contain a genuine lowercase English word.
_LOWERCASE_WORD = re.compile(r"\b[a-z]{3,}\b")

# Splits on sentence-ending punctuation (. ! ?) while keeping the punctuation
# attached to the clause before it, so the last "real" clause can be found and
# everything after it (source citations, page refs, journal names) discarded.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


# A citation fragment glued onto the end of a kept clause with no sentence break
# of its own — happens when the clause is a quoted saying whose closing "!"/"."
# sits right before the citation, e.g. '"Wie du mir, so ich dir!" Duta 599.' or
# 'Age quod agis!" Munno 1926 p.75.'. Matches from the last quote/exclamation
# onward: an optional short Proper-noun source name, then digits/dots/commas.
_GLUED_CITATION_TAIL = re.compile(
    r'(?<=[!?."\'’])\s+'
    r"(?:[A-Z][A-Za-z.]{0,10}\s*)?"
    r"\d[\d.,\s]*[A-Za-z]?\.?\s*$"
)


def _strip_glued_citation(clause: str) -> str:
    match = _GLUED_CITATION_TAIL.search(clause)
    if match and match.start() > 0:
        return clause[: match.start()].rstrip()
    return clause


def _strip_citation_tail(notes: str) -> str:
    """Cut trailing citation clutter by finding the last clause with real prose.

    This 1950s-dictionary-style source appends citations in wildly inconsistent
    formats after the actual meaning: bare numbers ('24.160.'), abbreviations
    ('M.334, 36.3', 'Duta 1422'), journal refs ('Munno 1921 p.144',
    'Ug.Journ.1936 p.254'), comma-separated lists of any of these, sometimes
    dash-separated, sometimes inside trailing parentheses. Rather than pattern-
    match every citation grammar (tried, kept finding new shapes), split into
    clauses on sentence punctuation and keep everything through the LAST clause
    that contains genuine lowercase prose words, discarding whatever citation
    debris follows it. A second pass then trims a citation fragment glued onto
    the end of that kept clause with no sentence break of its own (e.g. after a
    quoted saying's closing punctuation).
    """
    clauses = _SENTENCE_SPLIT.split(notes.strip())
    last_prose_index = -1
    for i, clause in enumerate(clauses):
        if _LOWERCASE_WORD.search(clause):
            last_prose_index = i
    if last_prose_index == -1:
        return ""
    kept = " ".join(clauses[: last_prose_index + 1]).strip()
    return _strip_glued_citation(kept)


def _looks_like_prose(text: str) -> bool:
    """Reject citation-only junk: needs several real words, mostly lowercase."""
    words = _WORD.findall(text)
    if len(words) < 4:
        return False
    lowercase_words = [w for w in words if w[0].islower()]
    return len(lowercase_words) >= 3


def clean_notes(notes: str) -> str | None:
    """Strip trailing source citations, e.g. 'Rub.C.1044.' / 'M.334, 36.3' / 'Duta 1422, 38.11'.

    Citation formatting in this 1950s-dictionary-style source is too inconsistent
    to regex away perfectly (multi-part academic refs, stray punctuation, notes
    that are pure citation). Rather than risk serving a mangled fragment or a fake
    generic sentence, strip what we can and return None (omit the field entirely)
    when what remains doesn't look like real prose. The frontend must not render
    a fallback placeholder in its place (per Patrick, 2026-07-23 spot-check).
    """
    notes = notes.strip()
    if not notes:
        return None

    stripped = _strip_citation_tail(notes)
    if stripped and len(stripped) < len(notes):
        notes = stripped

    return notes if _looks_like_prose(notes) else None


# Luganda noun-class prefixes for detecting a stray untranslated Luganda word
# left in the English field by the original transcriber, e.g. "(ebigambo) That is..."
# or "Big birds (aganyonyi) that don't fly...". Prefix shape alone is not enough:
# "en-"/"em-"/"e-"/"a-" also start ordinary English words ("empty", "entertainment",
# "escaped", "always"), which caused false-positive deletions in earlier passes
# (Patrick's 2026-07-23 spot-check). The prefix is only a candidate filter; the
# real check is `_is_known_luganda_word` below, which confirms the word actually
# appears as a headword on the Luganda side of this corpus.
_LUGANDA_PREFIX = re.compile(
    r"^(oku|obu|olu|omu|omw|eki|ebi|aka|ama|olw|en|em)[a-z]{3,}$", re.I
)


def _build_luganda_vocab(rows: list[dict[str, str]]) -> set[str]:
    """Every word that appears on the Luganda side of the proverbs corpus, plus
    every headword in the dictionary corpus (9,237 entries), lowercased.

    Using only the proverbs file's own Luganda column missed real Luganda words
    that happen not to appear as standalone tokens there (diminutive/class-prefix
    forms like 'akaswa', 'ebiswa' — real words, just not this file's headword
    shape). The dictionary adds headword coverage without weakening the
    English-word exclusion, since dictionary headwords are Luganda by
    definition.
    """
    vocab: set[str] = set()
    for row in rows:
        for word in re.findall(r"[A-Za-z']+", row.get("luganda") or ""):
            vocab.add(word.lower().strip("'"))
    if DICTIONARY_CSV.is_file():
        with DICTIONARY_CSV.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                for word in re.findall(r"[A-Za-z']+", row.get("luganda") or ""):
                    vocab.add(word.lower().strip("'"))
    return vocab


def _is_stray_luganda_gloss(paren_text: str, luganda_vocab: set[str]) -> bool:
    words = paren_text.strip().split()
    if len(words) != 1:
        return False
    word = re.sub(r"[^A-Za-z']", "", words[0])
    if len(word) < 5 or not _LUGANDA_PREFIX.match(word):
        return False
    # Confirm it's a real corpus word, not an English word that happens to
    # start with a Luganda-shaped prefix (e.g. "empty", "entertainment").
    return word.lower() in luganda_vocab


def clean_english(english: str, luganda_vocab: set[str]) -> tuple[str, bool]:
    """Remove a stray untranslated Luganda word left in parentheses.

    Only touches entries matching the narrow leaked-gloss pattern (prefix shape
    AND confirmed present as real Luganda vocabulary); every other English field
    is returned unchanged. Returns (cleaned_text, was_changed).
    """
    parens = re.findall(r"\(([^)]+)\)", english)
    stray = [p for p in parens if _is_stray_luganda_gloss(p, luganda_vocab)]
    if not stray:
        return english, False

    cleaned = english
    for gloss in stray:
        # Remove "(gloss) " or " (gloss)" including the surrounding parens/space.
        cleaned = re.sub(rf"\(\s*{re.escape(gloss)}\s*\)\s*", "", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    cleaned = cleaned[0].upper() + cleaned[1:] if cleaned else cleaned
    return cleaned, True


def build_entries() -> list[dict]:
    rows = load_source_rows()
    curated_pairs = load_curated_pairs()
    luganda_vocab = _build_luganda_vocab(rows)

    seen: set[tuple[str, str]] = set()
    entries: list[dict] = []
    index = 0
    english_fixed_count = 0
    for row in rows:
        luganda = (row.get("luganda") or "").strip()
        english = (row.get("english") or "").strip()
        if not luganda or not english:
            continue
        key = (luganda.lower(), english.lower())
        if key in curated_pairs or key in seen:
            continue
        seen.add(key)
        index += 1

        english, was_fixed = clean_english(english, luganda_vocab)
        if was_fixed:
            english_fixed_count += 1

        notes = (row.get("notes") or "").strip()
        theme = assign_theme(luganda, english, notes)
        source_id = (row.get("source_id") or "").strip()

        meaning = clean_notes(notes)
        entry = {
            "id": f"prov_all_{index:04d}",
            "luganda": luganda,
            "english": english,
            "theme": theme,
            "source_id": source_id,
            "needs_review": False,
        }
        if meaning is not None:
            entry["meaning"] = meaning
        entries.append(entry)

    print(f"Cleaned stray Luganda gloss out of {english_fixed_count} English fields.")
    return entries


def write_review(entries: list[dict]) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "category": "proverbs",
            "tier": "all",
            "description": "Auto-tagged raw proverbs pending Patrick's spot-check before promotion.",
            "total_entries": len(entries),
        },
        "entries": entries,
    }
    REVIEW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = Counter(e["theme"] for e in entries)
    no_meaning = sum(1 for e in entries if "meaning" not in e)
    print(f"Wrote {len(entries)} entries to {REVIEW_PATH}")
    print(f"Entries with no usable meaning (field omitted): {no_meaning} "
          f"({no_meaning / len(entries) * 100:.1f}%)")
    print("\nTheme distribution:")
    for theme, count in counts.most_common():
        print(f"  {theme:12s} {count:5d}")


def promote() -> None:
    if not REVIEW_PATH.is_file():
        sys.exit(f"Review file not found: {REVIEW_PATH}. Run --review first.")
    data = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    entries = data["entries"]
    for entry in entries:
        entry["tier"] = "all"

    payload = {
        "metadata": {
            "category": "proverbs",
            "tier": "all",
            "description": "Full raw proverb corpus (5000 Proverbs source), auto-tagged by theme.",
            "total_entries": len(entries),
        },
        "entries": entries,
    }
    PROMOTED_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Promoted {len(entries)} entries to {PROMOTED_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--review", action="store_true", help="Build the review file")
    group.add_argument("--promote", action="store_true", help="Promote review file to live dataset")
    args = parser.parse_args()

    if args.review:
        write_review(build_entries())
    elif args.promote:
        promote()


if __name__ == "__main__":
    main()