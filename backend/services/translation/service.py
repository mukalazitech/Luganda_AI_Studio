# backend/services/translation/service.py

"""
Translation service — Phase 2 (NLLB-200 neural fallback added).

Root cause of 500 error (historical):
- ChromaDB 1.5.5 .get() with include=["metadatas"] returns a dict
  where metadatas can be None if the collection query fails silently.
- The exception was swallowed, causing the function to return None.
- FastAPI then crashed trying to serialize None as a TranslationResponse.

Fixes applied:
- Added safe null checks at every step of the scan
- Added explicit error logging inside _scan_collection so failures surface
- Guaranteed that translate() ALWAYS returns a TranslationResponse object
- Added a top-level safety net at the end of translate() as final fallback
- Simplified ChromaDB .get() call to avoid version compatibility issues
"""

import logging
import re
from typing import Optional

from backend.db.chroma_client import chroma_client
from backend.services.ingestion.embedder import get_embedding_model
from backend.services.translation.nllb_service import nllb_translator
from backend.services.translation.openrouter_service import openrouter_translator
from backend.services.translation.schemas import TranslationRequest, TranslationResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------- #
# Constants
# ---------------------------------------------------------------------- #

COLLECTIONS_TO_SEARCH = ["vocabulary", "sentences", "proverbs"]

# MiniLM cosine distance: 0 = identical, 2 = opposite.
# similarity = 1 - distance
# CHANGED: weak candidates remain visible, but are not authoritative.
SEMANTIC_THRESHOLD = 0.50
SEMANTIC_AUTHORITATIVE_THRESHOLD = 0.80

MATCH_PRIORITY = {
    "partial": 1,
    "normalized": 2,
    "exact": 3,
}


# ---------------------------------------------------------------------- #
# Helpers
# ---------------------------------------------------------------------- #

def _normalize(text: str) -> str:
    """Lowercase, strip whitespace, strip trailing punctuation."""
    return text.strip().lower().rstrip(".,!?;:")


def _get_source_field(direction: str) -> str:
    """Field we search AGAINST — the language the user typed in."""
    return "english" if direction == "en_to_lg" else "luganda"


def _get_target_field(direction: str) -> str:
    """Field we return AS the translation."""
    return "luganda" if direction == "en_to_lg" else "english"


def _tokenize(text: str) -> list[str]:
    """Return normalized word tokens without surrounding punctuation."""
    return re.findall(r"[^\W_]+(?:'[^\W_]+)?", _normalize(text), flags=re.UNICODE)


def _has_compatible_translation_length(
    input_text: str,
    translated_text: str,
) -> bool:
    """Keep one-word lookups from expanding into unrelated sentences."""
    if len(_tokenize(input_text)) != 1:
        return True
    return 0 < len(_tokenize(translated_text)) <= 2


def _source_priority(meta: dict) -> int:
    """Prefer reviewed/curated records when match quality is tied."""
    tier = str(meta.get("tier", "")).strip().lower()
    if tier in {"featured", "curated"} or meta.get("verified") is True:
        return 3

    source_file = str(meta.get("source_file", "")).strip().lower()
    if source_file.endswith(".json") and not source_file.startswith("all_"):
        return 2
    return 0


def _match_result(
    meta: dict,
    target_field: str,
    collection_name: str,
    match_type: str,
    confidence: float,
    input_text: str,
) -> Optional[dict]:
    translation = meta.get(target_field)
    if not translation or not _has_compatible_translation_length(
        input_text,
        str(translation),
    ):
        return None
    return {
        "translated_text": translation,
        "match_type": match_type,
        "confidence": confidence,
        "matched_collection": collection_name,
        "matched_source_file": meta.get("source_file"),
        "trust_tier": "curated" if _source_priority(meta) > 0 else "corpus",
        "_source_priority": _source_priority(meta),
    }


# ---------------------------------------------------------------------- #
# Core: scan a collection and find the best match
# ---------------------------------------------------------------------- #

def _scan_collection(
    collection_name: str,
    source_field: str,
    target_field: str,
    input_text: str,
) -> Optional[dict]:
    """
    Pull all records from a collection and compare in Python.

    This is safe, simple, and avoids ChromaDB filter compatibility issues.
    With 500 records, this runs in milliseconds.

    Match priority:
    1. Exact match       — strip whitespace only, case preserved
    2. Normalized match  — both sides lowercased
    3. Partial match     — input word found inside stored value
                           e.g. "stomach" matches "Stomach / Belly"
    """
    try:
        col = chroma_client.get_collection(name=collection_name)

        # Simple .get() with no filters — just pull everything
        raw = col.get(include=["metadatas"])

        # Safety check — metadatas can be None if collection is empty
        if raw is None:
            logger.warning(f"[{collection_name}] col.get() returned None.")
            return None

        metadatas = raw.get("metadatas")
        if not metadatas:
            logger.warning(f"[{collection_name}] metadatas is empty or None.")
            return None

        logger.debug(
            f"[{collection_name}] Scanning {len(metadatas)} records | "
            f"source_field='{source_field}' | target_field='{target_field}'"
        )

        input_stripped = input_text.strip()
        input_normalized = _normalize(input_text)

        # ---------------------------------------------------------- #
        # Pass A — Exact match (strip only, case preserved)
        # ---------------------------------------------------------- #
        exact_matches = []
        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            stored = meta.get(source_field, "")
            if not stored:
                continue
            if stored.strip() == input_stripped:
                result = _match_result(
                    meta,
                    target_field,
                    collection_name,
                    "exact",
                    1.0,
                    input_text,
                )
                if result:
                    exact_matches.append(result)
        if exact_matches:
            return max(exact_matches, key=lambda item: item["_source_priority"])

        # ---------------------------------------------------------- #
        # Pass B — Normalized match (lowercase both sides)
        # ---------------------------------------------------------- #
        normalized_matches = []
        for meta in metadatas:
            if not isinstance(meta, dict):
                continue
            stored = meta.get(source_field, "")
            if not stored:
                continue
            if _normalize(stored) == input_normalized:
                result = _match_result(
                    meta,
                    target_field,
                    collection_name,
                    "normalized",
                    0.98,
                    input_text,
                )
                if result:
                    normalized_matches.append(result)
        if normalized_matches:
            return max(
                normalized_matches,
                key=lambda item: item["_source_priority"],
            )

        # ---------------------------------------------------------- #
        # Pass C — Partial match
        # "stomach" matches "Stomach / Belly"
        # "foot" matches "Foot"
        # New: "hello world" matches if "hello" OR "world" appears in stored value
        # Only runs if input has at least one word >= 3 characters
        # AND input is 1-2 words only. Sentences (3+ words) skip this
        # pass entirely and fall through to semantic search → NLLB.
        # Without this guard, ANY word in a sentence can false-match
        # a stored entry (e.g. "market" in a sentence hitting transport.json). # CHANGED
        # ---------------------------------------------------------- #
        if len(input_normalized) >= 3 and len(input_normalized.split()) <= 2:  # CHANGED
            input_words = _tokenize(input_text)  # CHANGED
            partial_matches = []
            for meta in metadatas:
                if not isinstance(meta, dict):
                    continue
                stored = meta.get(source_field, "")
                if not stored:
                    continue
                stored_words = _tokenize(stored)  # CHANGED
                exact_word_match = any(
                    word in stored_words for word in input_words
                )
                vocabulary_variant_match = (
                    collection_name == "vocabulary"
                    and len(input_words) == 1
                    and len(input_words[0]) >= 4
                    and any(
                        input_words[0] in stored_word
                        or stored_word in input_words[0]
                        for stored_word in stored_words
                        if len(stored_word) >= 4
                    )
                )
                if exact_word_match or vocabulary_variant_match:
                    result = _match_result(
                        meta,
                        target_field,
                        collection_name,
                        "partial",
                        0.85,
                        input_text,
                    )
                    if result:
                        partial_matches.append(result)
            if partial_matches:
                return max(
                    partial_matches,
                    key=lambda item: item["_source_priority"],
                )

    except Exception as e:
        # Log the full error so we can diagnose future issues
        logger.error(
            f"_scan_collection failed for '{collection_name}': {e}",
            exc_info=True,
        )

    return None


# ---------------------------------------------------------------------- #
# Semantic match
# ---------------------------------------------------------------------- #

def _try_semantic_match(
    collection_name: str,
    target_field: str,
    input_text: str,
) -> Optional[dict]:
    """
    Use MiniLM embeddings to find the semantically closest record.

    ChromaDB returns cosine distance (lower = more similar).
    similarity = 1 - distance
    We only accept results where similarity >= SEMANTIC_THRESHOLD.
    """
    try:
        model = get_embedding_model()
        embedding = model.encode([input_text])[0].tolist()

        col = chroma_client.get_collection(name=collection_name)

        results = col.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["metadatas", "distances"],
        )

        if not results:
            return None

        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not metadatas or not distances:
            return None

        if len(metadatas[0]) == 0:
            return None

        meta = metadatas[0][0]
        distance = distances[0][0]
        similarity = round(1.0 - distance, 4)

        logger.debug(
            f"[{collection_name}] SEMANTIC: "
            f"distance={distance:.4f} similarity={similarity:.4f} "
            f"threshold={SEMANTIC_THRESHOLD}"
        )

        if similarity >= SEMANTIC_THRESHOLD:
            translation = meta.get(target_field)
            if translation and _has_compatible_translation_length(
                input_text,
                str(translation),
            ):
                return {
                    "translated_text": translation,
                    "match_type": "semantic",
                    "confidence": similarity,
                    "matched_collection": collection_name,
                    "matched_source_file": meta.get("source_file"),
                    "trust_tier": (
                        "curated" if _source_priority(meta) > 0 else "corpus"
                    ),
                }

    except Exception as e:
        logger.error(
            f"_try_semantic_match failed for '{collection_name}': {e}",
            exc_info=True,
        )

    return None


# ---------------------------------------------------------------------- #
# Main translation function
# ---------------------------------------------------------------------- #

def translate(request: TranslationRequest) -> TranslationResponse:
    """
    Main entry point. ALWAYS returns a TranslationResponse — never None.

    Pass order:
    1. Scan-based match across all collections (exact → normalized → partial)
    2. Semantic match across all collections (best score wins)
    3. OpenRouter API (primary neural fallback, skipped if OPENROUTER_API_KEY not set)
    4. NLLB-200 local (fallback when OpenRouter disabled or failed)
    5. Not found — only if all neural options fail
    """
    input_text = request.text.strip()
    direction = request.direction
    source_field = _get_source_field(direction)
    target_field = _get_target_field(direction)

    logger.info(
        f"Translate | '{input_text}' | {direction} | "
        f"{source_field} → {target_field}"
    )

    # ------------------------------------------------------------------ #
    # Pass 1 — Scan-based match
    # ------------------------------------------------------------------ #
    scan_matches = []
    for collection in COLLECTIONS_TO_SEARCH:
        result = _scan_collection(
            collection_name=collection,
            source_field=source_field,
            target_field=target_field,
            input_text=input_text,
        )
        if result:
            scan_matches.append(result)

    if scan_matches:
        result = max(
            scan_matches,
            key=lambda item: (
                MATCH_PRIORITY[item["match_type"]],
                item.get("_source_priority", 0),
            ),
        )
        logger.info(
            f"Match [{result['match_type']}] in "
            f"'{result['matched_collection']}' → "
            f"'{result['translated_text']}'"
        )
        public_result = {
            key: value
            for key, value in result.items()
            if not key.startswith("_")
        }
        return TranslationResponse(
            input_text=input_text,
            direction=direction,
            status="success",
            message=f"{result['match_type'].capitalize()} match found.",
            **public_result,
        )

    # ------------------------------------------------------------------ #
    # Pass 2 — Semantic match
    # ------------------------------------------------------------------ #
    best_semantic: Optional[dict] = None

    for collection in COLLECTIONS_TO_SEARCH:
        result = _try_semantic_match(
            collection_name=collection,
            target_field=target_field,
            input_text=input_text,
        )
        if result:
            if (
                best_semantic is None
                or result["confidence"] > best_semantic["confidence"]
            ):
                best_semantic = result

    if best_semantic:
        is_authoritative = (
            best_semantic["confidence"] >= SEMANTIC_AUTHORITATIVE_THRESHOLD
        )
        logger.info(
            f"Semantic match in '{best_semantic['matched_collection']}' | "
            f"confidence={best_semantic['confidence']} | "
            f"→ '{best_semantic['translated_text']}'"
        )
        return TranslationResponse(
            input_text=input_text,
            direction=direction,
            status="success" if is_authoritative else "possible_match",
            message=(
                "Semantic match found."
                if is_authoritative
                else "Possible semantic match. Please confirm before relying on it."
            ),
            **best_semantic,
        )

    # ------------------------------------------------------------------ #
    # Pass 3 — OpenRouter API (primary neural fallback)
    # Skipped silently if OPENROUTER_API_KEY is not set.
    # Falls through to NLLB-200 on timeout, HTTP error, or empty response.
    # ------------------------------------------------------------------ #
    if openrouter_translator.is_enabled():
        logger.info(f"[Pass 3] Attempting OpenRouter translation for '{input_text}'")
        api_text = openrouter_translator.translate(input_text, direction)
        if api_text and _has_compatible_translation_length(input_text, api_text):
            logger.info(f"[OpenRouter] '{input_text}' → '{api_text}'")
            return TranslationResponse(
                input_text=input_text,
                direction=direction,
                translated_text=api_text,
                match_type="neural_api",
                confidence=0.75,
                matched_collection="openrouter",
                matched_source_file=None,
                trust_tier="ai_generated",
                status="success",
                message="AI-generated translation via OpenRouter. May need review.",
            )

    # ------------------------------------------------------------------ #
    # Pass 4 — Neural fallback (NLLB-200 local)
    # Only reached when OpenRouter is disabled or failed.
    # ------------------------------------------------------------------ #
    logger.info(f"[Pass 4] Attempting NLLB-200 translation for '{input_text}'")

    neural_text = nllb_translator.translate(input_text, direction)

    if neural_text and _has_compatible_translation_length(
        input_text,
        neural_text,
    ):
        logger.info(f"[NLLB] '{input_text}' → '{neural_text}'")
        return TranslationResponse(
            input_text=input_text,
            direction=direction,
            translated_text=neural_text,
            match_type="neural_local",
            confidence=0.70,
            matched_collection="nllb-200-local",
            matched_source_file=None,
            trust_tier="ai_generated",
            status="success",
            message="AI-generated translation (local model). May need review.",
        )

    # ------------------------------------------------------------------ #
    # Pass 5 — Nothing found
    # ------------------------------------------------------------------ #
    logger.info(f"No match for '{input_text}' | direction={direction}")

    return TranslationResponse(
        input_text=input_text,
        direction=direction,
        translated_text="",
        match_type="not_found",
        confidence=0.0,
        matched_collection=None,
        matched_source_file=None,
        trust_tier=None,
        status="not_found",
        message=(
            "We don't know this word yet — but you can teach us! "
            "Try a simpler word or phrase, or type the correct translation "
            "below and we'll add it to the dictionary for everyone."
        ),
    )
