"""Cached, deterministic normalization of the curated learner datasets."""

from functools import cache
import json
from typing import Any

from backend.core.config import DATASETS_DIR


def _load_entries(subdir: str) -> list[dict[str, Any]]:
    """Read every curated JSON file in a directory in deterministic order.

    An entry without its own "tier" inherits the file's metadata.tier, defaulting
    to "featured" for files (like the original curated sets) that predate the
    tier concept entirely.
    """
    entries: list[dict[str, Any]] = []
    for path in sorted((DATASETS_DIR / subdir).glob("*.json")):
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
        file_tier = data.get("metadata", {}).get("tier", "featured")
        for entry in data.get("entries", []):
            entry.setdefault("tier", file_tier)
            entries.append(entry)
    return entries


def _selected(entry: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: entry[field] for field in fields if field in entry}


@cache
def proverbs() -> list[dict[str, Any]]:
    normalized = []
    for index, entry in enumerate(_load_entries("proverbs"), start=1):
        item = {
            "id": entry.get("id") or f"proverbs:{index:04d}",
            "tier": entry.get("tier", "featured"),
            **_selected(entry, ("luganda", "english", "meaning", "theme")),
        }
        item.update(_selected(entry, ("symbols", "cultural_note")))
        normalized.append(item)
    return normalized


@cache
def phrases() -> list[dict[str, Any]]:
    normalized = []
    for index, entry in enumerate(_load_entries("sentences"), start=1):
        item = {
            "id": entry.get("id") or f"phrases:{index:04d}",
            **_selected(entry, ("luganda", "english", "topic", "difficulty")),
        }
        item.update(_selected(entry, ("tense", "notes")))
        normalized.append(item)
    return normalized


@cache
def vocabulary() -> list[dict[str, Any]]:
    normalized = []
    for entry in _load_entries("vocabulary"):
        category = entry["category"]
        luganda = entry["luganda"]
        item = {
            "key": f"{category}:{luganda}",
            "tier": entry.get("tier", "featured"),
            "luganda": luganda,
            **_selected(entry, ("english", "category")),
            "part_of_speech": entry.get("part_of_speech"),
            "example_luganda": entry.get("example_sentence_luganda"),
            "example_english": entry.get("example_sentence_english"),
        }
        item.update(
            _selected(
                entry,
                (
                    "subcategory",
                ),
            )
        )
        normalized.append(item)
    return normalized


def _section_items(content: list[Any] | dict[str, Any]) -> list[Any]:
    if isinstance(content, list):
        return content
    if isinstance(content.get("entries"), list):
        return content["entries"]
    if isinstance(content.get("rows"), list):
        return content["rows"]
    return [
        {"label": key.replace("_", " ").title(), "value": value}
        for key, value in content.items()
        if key not in {"description", "important_note"}
    ]


@cache
def grammar_sections() -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    for path in sorted((DATASETS_DIR / "grammar").glob("*.json")):
        with path.open(encoding="utf-8") as source:
            data = json.load(source)
        metadata = data.get("metadata", {})
        file_introduction = data.get("introduction", "")
        content_fields = [
            (field, content)
            for field, content in data.items()
            if field not in {"metadata", "introduction"}
            and content
            and isinstance(content, (list, dict))
        ]
        base_title = path.stem.replace("_", " ").title()
        for field, content in content_fields:
            field_title = field.replace("_", " ").title()
            section = {
                "id": f"{path.stem}:{field}",
                "title": (
                    f"{base_title} — {field_title}"
                    if len(content_fields) > 1
                    else base_title
                ),
                "kind": field,
                "introduction": (
                    content.get("description", file_introduction)
                    if isinstance(content, dict)
                    else file_introduction
                ),
                "items": _section_items(content),
                "verified": metadata.get("verified"),
                "verification_notes": metadata.get("verification_notes"),
                "source_ids": metadata.get("source_ids", []),
            }
            if isinstance(content, dict) and "important_note" in content:
                section["important_note"] = content["important_note"]
            sections.append(section)
    return sections
