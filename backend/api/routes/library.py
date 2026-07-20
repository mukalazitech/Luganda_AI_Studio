"""GET-only learner library routes backed by curated JSON files."""

from fastapi import APIRouter, HTTPException

from backend.services.library import service


router = APIRouter()


@router.get("/grammar")
def get_grammar(count_only: bool = False):
    sections = service.grammar_sections()
    response = {"collection": "grammar", "count": len(sections)}
    if not count_only:
        response["sections"] = sections
    return response


@router.get("/{collection}")
def get_collection(collection: str, count_only: bool = False):
    loaders = {
        "proverbs": service.proverbs,
        "phrases": service.phrases,
        "vocabulary": service.vocabulary,
    }
    loader = loaders.get(collection)
    if loader is None:
        raise HTTPException(status_code=404, detail="Library collection not found")

    entries = loader()
    response = {"collection": collection, "count": len(entries)}
    if not count_only:
        response["entries"] = entries
    return response
