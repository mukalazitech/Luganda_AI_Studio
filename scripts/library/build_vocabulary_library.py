"""Build the 'All vocabulary' browse tier from the raw dictionary corpus CSV.

Two-step workflow (Phase 2 of plans/2026-07-23-luganda-browse-library-expansion.md):
  1. `--review`  writes datasets/vocabulary/_review/all_vocabulary_review.json for spot-check.
     This file is OUTSIDE datasets/vocabulary/ so the library service never loads it.
  2. `--promote` reads that (possibly hand-edited) review file and writes the live
     datasets/vocabulary/all_vocabulary.json that the service serves under tier="all".

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
SOURCE_CSV = Path(r"D:\projects\Luganda_AI_Studio\data\csv\groupB_dictionary.csv")
CURATED_DIR = WORKTREE_ROOT / "datasets" / "vocabulary"
REVIEW_DIR = WORKTREE_ROOT / "scripts" / "library" / "review"
REVIEW_PATH = REVIEW_DIR / "all_vocabulary_review.json"
PROMOTED_PATH = WORKTREE_ROOT / "datasets" / "vocabulary" / "all_vocabulary.json"

# Category assignment is EXACT English-headword membership, not keyword search.
#
# The earlier keyword approach matched loosely against each entry's Luganda
# *definition* text, so "cold" landed in body_parts (its gloss said "cold in the
# head"), "basket"/"egg" in animals (glosses mentioned "fish"/"locust"), and the
# label words "animal"/"colour" tagged themselves. Patrick's fix (2026-07-23):
# we already KNOW the English words in each category — match the English headword
# against those known words and nothing else. Anything not confidently a member
# falls to `general` rather than polluting a real category.
#
# Each set below is authored from what an English speaker knows belongs in the
# category, and is further seeded at runtime from the english words already in
# the curated datasets/vocabulary/<category>.json files (see _seed_from_curated).
# Members are lowercase, singular-or-plural as they naturally read; the headword
# is normalized the same way before lookup (see normalize_headword).
CATEGORY_WORDS: dict[str, set[str]] = {
    "animals": {
        "dog", "cat", "cow", "bull", "ox", "calf", "goat", "sheep", "lamb", "pig",
        "hog", "boar", "donkey", "horse", "mule", "rabbit", "hare", "rat", "mouse",
        "mole", "bat", "monkey", "ape", "baboon", "chimpanzee", "gorilla", "lion",
        "leopard", "cheetah", "hyena", "jackal", "fox", "wolf", "elephant", "rhino",
        "rhinoceros", "hippopotamus", "hippo", "buffalo", "zebra", "giraffe",
        "antelope", "gazelle", "deer", "impala", "warthog", "squirrel", "porcupine",
        "hedgehog", "mongoose", "crocodile", "lizard", "chameleon", "snake", "python",
        "cobra", "viper", "frog", "toad", "tortoise", "turtle", "fish", "bird",
        "hen", "cock", "rooster", "chicken", "duck", "goose", "turkey", "pigeon",
        "dove", "eagle", "hawk", "owl", "crow", "parrot", "sparrow", "stork",
        "crane", "guinea fowl", "insect", "ant", "bee", "wasp", "fly", "mosquito",
        "butterfly", "moth", "beetle", "grasshopper", "locust", "cricket", "spider",
        "scorpion", "snail", "slug", "worm", "termite", "flea", "louse", "tick",
        "crab", "shrimp", "lobster", "camel",
    },
    "body_parts": {
        "head", "skull", "hair", "face", "forehead", "eye", "eyes", "eyebrow",
        "eyelash", "eyelid", "ear", "ears", "nose", "nostril", "cheek", "cheeks",
        "mouth", "lip", "lips", "tongue", "tooth", "teeth", "gum", "gums", "jaw",
        "chin", "neck", "throat", "shoulder", "shoulders", "arm", "arms", "elbow",
        "wrist", "hand", "hands", "palm", "finger", "fingers", "thumb", "little finger",
        # Bare "nail" deliberately excluded: this corpus's own "nail" row
        # translates to omusumaali (the hardware nail, per its own definition
        # "n., omusumaali; finger n., olwala."), not the anatomical sense.
        # "fingernail"/"toenail" are unambiguous and kept.
        "index finger", "fingernail", "toenail", "chest", "breast", "breasts", "nipple",
        "rib", "ribs", "back", "spine", "waist", "hip", "hips", "belly", "stomach",
        "abdomen", "navel", "buttock", "buttocks", "thigh", "thighs", "knee", "knees",
        "leg", "legs", "calf", "shin", "ankle", "heel", "foot", "feet", "toe", "toes",
        "sole", "skin", "flesh", "bone", "bones", "blood", "muscle", "vein", "nerve",
        "heart", "lung", "lungs", "liver", "kidney", "spleen", "brain", "intestine",
        "intestines", "bladder", "womb",
    },
    "clothing": {
        "clothes", "clothing", "cloth", "garment", "dress", "gown", "skirt", "shirt",
        "blouse", "trousers", "shorts", "coat", "jacket", "sweater", "cardigan",
        "robe", "cloak", "scarf", "veil", "shawl", "hat", "cap", "shoe", "shoes",
        "sandal", "sandals", "boot", "boots", "sock", "socks", "stocking", "glove",
        "gloves", "belt", "tie", "apron", "uniform", "underwear", "pyjamas",
        "handkerchief", "button", "collar", "sleeve", "pocket", "barkcloth",
    },
    "colors": {
        "black", "white", "red", "green", "yellow", "blue", "brown", "grey", "gray",
        "orange", "purple", "pink", "violet", "scarlet", "crimson", "golden",
    },
    "emotions": {
        "happiness", "joy", "gladness", "sadness", "sorrow", "grief", "misery",
        "anger", "rage", "fury", "fear", "terror", "dread", "love", "affection",
        "hatred", "hate", "jealousy", "envy", "shame", "pride", "pity", "compassion",
        "hope", "despair", "worry", "anxiety", "loneliness", "courage", "boredom",
        "disgust", "surprise", "gratitude", "contentment", "excitement", "peace",
    },
    "family": {
        "family", "father", "mother", "parent", "parents", "child", "children",
        "son", "daughter", "brother", "sister", "sibling", "husband", "wife",
        "spouse", "grandfather", "grandmother", "grandchild", "grandson",
        "granddaughter", "uncle", "aunt", "nephew", "niece", "cousin", "in-law",
        "father-in-law", "mother-in-law", "twin", "twins", "orphan", "widow",
        "widower", "ancestor", "relative", "relatives", "clan", "co-wife",
        "stepfather", "stepmother", "stepchild",
    },
    "food_and_drink": {
        "food", "meal", "porridge", "bread", "loaf", "rice", "millet", "sorghum",
        "maize", "cassava", "potato", "sweet potato", "yam", "banana", "plantain",
        "matoke", "bean", "beans", "pea", "peas", "groundnut", "peanut", "meat",
        "beef", "pork", "mutton", "chicken", "fish", "egg", "eggs", "milk", "butter",
        "ghee", "oil", "salt", "sugar", "honey", "pepper", "sauce", "soup", "stew",
        "vegetable", "vegetables", "fruit", "mango", "pineapple", "orange", "lemon",
        "avocado", "sugarcane", "cake", "flour", "water", "drink", "beer", "wine",
        "tea", "coffee", "juice", "relish",
    },
    "health": {
        "illness", "disease", "sickness", "health", "pain", "ache", "headache",
        "fever", "malaria", "cough", "cold", "flu", "wound", "sore", "ulcer",
        "swelling", "boil", "rash", "itch", "injury", "fracture", "medicine",
        "drug", "cure", "remedy", "treatment", "vaccine", "bandage", "hospital",
        "clinic", "doctor", "nurse", "patient", "diarrhoea", "diarrhea", "vomiting",
        "nausea", "dizziness", "cancer", "tuberculosis", "leprosy", "smallpox",
        "measles", "epilepsy", "madness", "blindness", "deafness", "paralysis",
    },
    "numbers": {
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty",
        "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
        "million", "half", "quarter", "dozen", "single", "double", "triple",
        "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth",
        "ninth", "tenth",
    },
    "places": {
        "town", "city", "village", "country", "place", "market", "shop", "home",
        "house", "school", "church", "mosque", "temple", "hospital", "office",
        "farm", "garden", "field", "forest", "bush", "hill", "mountain", "valley",
        "river", "lake", "sea", "ocean", "island", "swamp", "well", "spring",
        "road", "path", "street", "bridge", "border", "region", "district",
        "county", "capital", "palace", "prison", "graveyard", "kingdom", "nation",
        "world", "compound", "courtyard", "kitchen", "bedroom", "toilet", "latrine",
    },
    "time": {
        "time", "morning", "afternoon", "evening", "night", "midnight", "noon",
        "midday", "dawn", "dusk", "day", "today", "tomorrow", "yesterday", "week",
        "month", "year", "season", "hour", "minute", "second", "moment", "century",
        "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
        "january", "february", "march", "april", "may", "june", "july", "august",
        "september", "october", "november", "december", "clock", "watch", "calendar",
    },
    "transport": {
        "car", "vehicle", "lorry", "truck", "bus", "taxi", "van", "motorcycle",
        "bicycle", "bike", "boat", "canoe", "ship", "ferry", "aeroplane", "airplane",
        "plane", "train", "wheel", "engine", "road", "journey", "trip", "voyage",
        "wheelbarrow", "cart", "paddle", "oar", "sail",
    },
}
DEFAULT_CATEGORY = "general"

# Dictionary source-annotation markers that belong to a LUGANDA headword. When
# they appear in the english field the row's columns are swapped/malformed from
# the 2026-07-22 corpus parse (e.g. english="gyabazito (la) red stinkwood",
# luganda="kind of tall forest tree"). Not repairable from this file alone, so
# these rows are dropped. Kept narrow so ordinary English parentheticals like
# "abandoned (deserted)" are NOT matched.
_MALFORMED_ENGLISH = re.compile(
    r"\((?:la|n/n|n|v|vi|vt|adj|adv|int|interj|conj|prep)\)"          # POS/source in parens
    r"|\[(?:Sw|Eng|Ar|Lg|Lat|Stf|Sir|Pers|Fr|Ger|Port|Hind|frag)\b"  # bracketed source lang
    r"|(?<![A-Za-z])ideo\.|\bq\.v\.|\bplur\.",
    re.I,
)

# Cross-reference stubs like "ab plur", "e- plur", "a- pron", "prep" — the
# luganda field is a bare part-of-speech/grammar pointer (to a plural form,
# a pronoun paradigm, etc.), not a real headword, so it is not a usable
# (luganda, english) translation pair.
_GRAMMAR_STUB = re.compile(
    r"^[a-z]{0,4}-?\s*(v|n|plur|pron|num|adv|adj|interj|conj|prep|tr|intr|vi|vt|cf)\.?$",
    re.I,
)

# "vide <word>" ("see also") cross-reference with nothing else — same idea as
# _CF_ONLY but appearing on the luganda side in this corpus.
_VIDE_ONLY = re.compile(r"^vide\s+\S", re.I)

# Closed stoplist of common short English words that are never valid Luganda
# spellings. Some dictionary rows got their luganda/english columns swapped
# during the 2026-07-22 corpus parse (e.g. luganda="on", english="behalf of" —
# the real pair is english="on behalf of", luganda="kubwa"/"kulwa", visible in
# the source line but lost to the swap). Not repairable from this file alone;
# matched as an exact whole-field token set (never a substring) so it cannot
# accidentally reject a real Luganda word.
_ENGLISH_STOPWORDS = {
    "on", "of", "at", "to", "for", "with", "by", "in", "from", "into", "onto",
    "take", "give", "get", "put", "do", "go", "use", "see", "sit", "long",
    "become", "all", "day", "night", "over", "under", "up", "down", "out",
    "off", "away", "each", "other", "than", "then", "also", "only", "still",
    "yet", "ago", "afar",
    # Copulas/auxiliaries — added 2026-07-23 after Patrick spotted a live card
    # "be in" -> "despair": source row was luganda="be in" english="despair"
    # definition="be in, okwesalabya." — the parser took the English phrasal
    # lead-in as the "translation" and dropped the real Luganda word
    # (okwesalabya) that followed. Same shape as "go/aboard", "become/accustomed
    # to", "have/appetite" etc. Broadening this set catches all of them.
    "be", "is", "are", "am", "was", "were", "been", "being", "has", "have",
    "had", "not", "no", "can", "will", "shall", "may", "should", "would",
    "could", "must",
}
_WORD_RE = re.compile(r"[a-z']+")


def _is_swapped_stopword(luganda: str) -> bool:
    words = _WORD_RE.findall(luganda.lower())
    return bool(words) and all(w in _ENGLISH_STOPWORDS for w in words)


# Most swapped-stopword rows are repairable: the real Luganda translation is
# still present in the definition, right after the leaked English prefix
# (e.g. luganda="be in" english="despair" definition="be in, okwesalabya." ->
# real luganda = "okwesalabya"). Extract it instead of just dropping the row.
_CANDIDATE_SHAPE = re.compile(r"^[A-Za-z '\-]+$")


def _repair_swapped_stopword(luganda: str, definition: str) -> str | None:
    match = re.match(rf"^\s*{re.escape(luganda)}\s*,\s*(.+)", definition, re.I)
    if not match:
        return None
    clause = re.split(r"[;.]", match.group(1), maxsplit=1)[0].strip()
    if not clause or not _CANDIDATE_SHAPE.fullmatch(clause):
        return None
    if _is_grammar_stub(clause) or _is_swapped_stopword(clause):
        return None  # still just a POS tag ("adj") or English ("as far as")
    return clause

# A source-corpus entry number leaked into the luganda field, e.g.
# "10 gulp" / "1 playing card" — a parser artifact from the numbered
# dictionary source, not a translation.
_DIGIT_LEADING = re.compile(r"^\d+\s")

# A "cf. <word>" cross-reference with nothing else — the english field is a
# pointer to another headword, not a translation of this one.
_CF_ONLY = re.compile(r"^cf\.\s*\S", re.I)

# Hand-fixed corpus mistranslations (Patrick's 2026-07-23 spot-check): the
# source dictionary sometimes gives the GENERIC word ("ensolo" = "animal")
# as the primary translation for a SPECIFIC headword, with the real specific
# word only present as a "vide" (see-also) cross-reference in the definition,
# e.g. row english="antelope" luganda="ensolo" definition="ensolo; also vide
# ensunu, entalaganya, enjobi, etc." — showing "animal" under a card titled
# "antelope" is wrong even though the category (animals) is correct. Checked:
# this is the ONLY row in the whole corpus where a non-general entry's luganda
# is the bare generic animal word, so a small explicit table (not a general
# heuristic) is the honest fix — "ensunu" is a real corpus word for a specific
# antelope species, taken verbatim from this row's own "vide" list.
_HEADWORD_LUGANDA_OVERRIDES: dict[str, str] = {
    "antelope": "ensunu",
}


def _is_grammar_stub(luganda: str) -> bool:
    return bool(_GRAMMAR_STUB.match(luganda.strip()))


def _is_digit_leading(luganda: str) -> bool:
    return bool(_DIGIT_LEADING.match(luganda.strip()))


def _is_cf_only(english: str) -> bool:
    return bool(_CF_ONLY.match(english.strip()))


def _paren_mismatched(text: str) -> bool:
    """Detect a multi-line dictionary entry whose parenthetical bled across
    two CSV rows during parsing (e.g. luganda="of Parliament)",
    english="also balcony; gallery (e.g."). Genuinely broken, not repairable
    from this file alone — filtered out rather than served mangled.
    """
    return text.count("(") != text.count(")")


def load_source_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.is_file():
        sys.exit(f"Source CSV not found: {SOURCE_CSV}")
    with SOURCE_CSV.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _curated_files() -> list[Path]:
    """Every curated vocabulary JSON EXCEPT our own promoted output — otherwise a
    re-run would treat the previous all_vocabulary.json as curated and dedupe the
    whole corpus away / re-seed categories from stale auto-tags."""
    return [
        p for p in sorted(CURATED_DIR.glob("*.json"))
        if p.name != PROMOTED_PATH.name
    ]


def load_curated_pairs() -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for path in _curated_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            luganda = (entry.get("luganda") or "").strip().lower()
            english = (entry.get("english") or "").strip().lower()
            if luganda and english:
                pairs.add((luganda, english))
    return pairs


def _seed_from_curated() -> None:
    """Add the english words already in each curated datasets/vocabulary/<cat>.json
    into that category's word set, so the "all" tier honours exactly the taxonomy
    the curated "featured" tier already uses (Patrick's "the English you already
    know"). File stem == category name (animals.json -> "animals")."""
    for path in _curated_files():
        category = path.stem
        target = CATEGORY_WORDS.get(category)
        if target is None:
            continue  # any non-category curated file
        data = json.loads(path.read_text(encoding="utf-8"))
        for entry in data.get("entries", []):
            for candidate in normalize_headword(entry.get("english") or ""):
                if candidate:
                    target.add(candidate)


# Category-name / label words that describe a category rather than belong to it
# ("animal" is not an animal, "colour" is not a colour). Never categorised.
_CATEGORY_LABEL_WORDS = {
    "animal", "animals", "colour", "color", "colours", "colors", "body", "number",
    "numbers", "clothing", "clothes", "food", "drink", "place", "places", "time",
    "family", "transport", "emotion", "emotions", "health",
}


def normalize_headword(english: str) -> list[str]:
    """Reduce an english headword to its comparable lexical form(s).

    Dictionary english fields read like "abandoned (deserted)", "car / vehicle",
    "town; city". We take the text before any ';', drop parenthetical glosses,
    split "/" alternatives, strip a leading "to " / "a " / "an " / "the ", and
    lowercase. Returns each candidate so "car / vehicle" can match on either.
    Multi-word phrases are kept intact (so "little finger" can match a set entry
    of the same form) — they simply won't match unless listed verbatim.
    """
    head = english.split(";")[0]
    head = re.sub(r"\([^)]*\)", " ", head)  # drop "(deserted)" style glosses
    candidates = []
    for part in head.split("/"):
        part = part.strip().lower()
        part = re.sub(r"^(to|a|an|the)\s+", "", part)
        part = re.sub(r"[^a-z\s'-]", "", part).strip()
        part = re.sub(r"\s{2,}", " ", part)
        if part:
            candidates.append(part)
    return candidates


def assign_category(english: str) -> str:
    """Assign a category ONLY when the english headword is a known member of that
    category's word set. Matches the headword, never the Luganda definition, and
    never the category's own label word. Everything else -> general."""
    candidates = normalize_headword(english)
    if any(c in _CATEGORY_LABEL_WORDS for c in candidates):
        return DEFAULT_CATEGORY
    for candidate in candidates:
        for category, words in CATEGORY_WORDS.items():
            if candidate in words:
                return category
    return DEFAULT_CATEGORY


def build_entries() -> tuple[list[dict], Counter]:
    rows = load_source_rows()
    curated_pairs = load_curated_pairs()
    _seed_from_curated()

    seen: set[tuple[str, str]] = set()
    entries: list[dict] = []
    dropped: Counter = Counter()
    index = 0
    for row in rows:
        luganda = (row.get("luganda") or "").strip()
        english = (row.get("english") or "").strip()
        override = _HEADWORD_LUGANDA_OVERRIDES.get(english.strip().lower())
        if override:
            luganda = override
        if not luganda or not english:
            dropped["empty_side"] += 1
            continue
        if _is_grammar_stub(luganda):
            dropped["grammar_stub"] += 1
            continue
        if _is_digit_leading(luganda):
            dropped["digit_leading"] += 1
            continue
        if _is_cf_only(english):
            dropped["cf_only"] += 1
            continue
        if _VIDE_ONLY.match(luganda):
            dropped["vide_only"] += 1
            continue
        if _is_swapped_stopword(luganda):
            repaired = _repair_swapped_stopword(luganda, row.get("definition") or "")
            if repaired:
                luganda = repaired
                dropped["repaired_swapped_stopword"] += 1
            else:
                dropped["swapped_stopword"] += 1
                continue
        if _paren_mismatched(english) or _paren_mismatched(luganda):
            dropped["paren_mismatch"] += 1
            continue
        if _MALFORMED_ENGLISH.search(english):
            dropped["malformed_swapped"] += 1
            continue

        key = (luganda.lower(), english.lower())
        if key in curated_pairs:
            dropped["already_curated"] += 1
            continue
        if key in seen:
            dropped["cross_file_dup"] += 1
            continue
        seen.add(key)
        index += 1

        definition = (row.get("definition") or "").strip()
        category = assign_category(english)
        source_id = (row.get("source_id") or "").strip()

        entry = {
            "id": f"vocab_all_{index:04d}",
            "luganda": luganda,
            "english": english,
            "category": category,
            "source_id": source_id,
            "needs_review": False,
        }
        if definition:
            entry["notes"] = definition
        entries.append(entry)

    entries, merged_count = _merge_same_luganda_per_category(entries)
    dropped["merged_duplicate_luganda"] = merged_count
    return entries, dropped


def _merge_same_luganda_per_category(entries: list[dict]) -> tuple[list[dict], int]:
    """Collapse cards that show the SAME Luganda word twice on the same browse
    page (Patrick's report: the emotions page showed two separate "ennaku"
    cards — one glossed "sadness", one "sorrow" — because the source dictionary
    is English-headword-first: one Luganda word legitimately gets many close
    English synonyms, each its own CSV row). Grouping is scoped to
    (category, luganda) rather than luganda alone: merging is only safe when
    the words also ended up on the same themed page — a small number of
    Luganda words are true homographs across unrelated categories (e.g.
    "okuziyiza" spans several senses), and this keeps those separate.

    English glosses are joined with "/" in their first-seen order, deduplicated
    case-insensitively. Definitions are combined the same way. needs_review is
    OR'd across the group; the first non-empty source_id wins; ids are
    renumbered after merging since the entry count changes.
    """
    groups: dict[tuple[str, str], list[dict]] = {}
    order: list[tuple[str, str]] = []
    for entry in entries:
        gkey = (entry["category"], entry["luganda"].strip().lower())
        if gkey not in groups:
            groups[gkey] = []
            order.append(gkey)
        groups[gkey].append(entry)

    merged: list[dict] = []
    merged_count = 0
    for index, gkey in enumerate(order, start=1):
        members = groups[gkey]
        if len(members) == 1:
            entry = members[0]
        else:
            merged_count += len(members) - 1
            seen_english: list[str] = []
            for m in members:
                if m["english"] not in seen_english:
                    seen_english.append(m["english"])
            seen_notes: list[str] = []
            for m in members:
                note = m.get("notes")
                if note and note not in seen_notes:
                    seen_notes.append(note)
            entry = {
                "luganda": members[0]["luganda"],
                "english": " / ".join(seen_english),
                "category": members[0]["category"],
                "source_id": next((m["source_id"] for m in members if m["source_id"]), ""),
                "needs_review": any(m["needs_review"] for m in members),
            }
            if seen_notes:
                entry["notes"] = " / ".join(seen_notes)
        entry["id"] = f"vocab_all_{index:04d}"
        merged.append(entry)

    return merged, merged_count


def write_review(entries: list[dict], dropped: Counter) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "category": "vocabulary",
            "tier": "all",
            "description": "Auto-tagged raw dictionary corpus pending Patrick's spot-check before promotion.",
            "total_entries": len(entries),
        },
        "entries": entries,
    }
    REVIEW_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = Counter(e["category"] for e in entries)
    print(f"Wrote {len(entries)} entries to {REVIEW_PATH}")
    print("\nDropped (not written):")
    for reason, count in dropped.most_common():
        print(f"  {reason:16s} {count:5d}")
    print("\nCategory distribution:")
    for category, count in counts.most_common():
        print(f"  {category:16s} {count:5d}")


def promote() -> None:
    if not REVIEW_PATH.is_file():
        sys.exit(f"Review file not found: {REVIEW_PATH}. Run --review first.")
    data = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    entries = data["entries"]
    for entry in entries:
        entry["tier"] = "all"

    payload = {
        "metadata": {
            "category": "vocabulary",
            "tier": "all",
            "description": "Full raw dictionary corpus (More Translations dictionary source), auto-tagged by category.",
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
        entries, dropped = build_entries()
        write_review(entries, dropped)
    elif args.promote:
        promote()


if __name__ == "__main__":
    main()
