# backend/db/chroma_client.py

import logging
from typing import Optional

import chromadb
from chromadb.errors import NotFoundError

from backend.core.config import settings

logger = logging.getLogger(__name__)


def get_or_create_collection_safe(
    client: chromadb.ClientAPI,
    name: str,
    embedding_function=None,
    metadata: Optional[dict] = None,
):
    """
    Fetch a collection if it already exists, otherwise create it.

    ChromaDB's get_or_create_collection() raises a conflict error when an
    explicit embedding_function is passed for a collection that already
    exists with a *different* persisted embedding function. Existing
    collections in this app were created at different times with different
    embedding functions, so passing one explicitly is unsafe for them.

    This helper sidesteps that: for an existing collection, it fetches it
    with no embedding_function override (ChromaDB resolves the one already
    persisted on the collection). Only brand-new collections get the
    provided embedding_function.
    """
    try:
        return client.get_collection(name)
    except NotFoundError:
        return client.get_or_create_collection(
            name,
            embedding_function=embedding_function,
            metadata=metadata,
        )


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Creates and returns a persistent ChromaDB client.
    Data is stored on disk at the path defined in settings.chroma_dir.
    """
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Connecting to ChromaDB at: {settings.chroma_dir}")

    client = chromadb.PersistentClient(
        path=str(settings.chroma_dir),
    )
    return client


# This line is what gets imported by other files.
chroma_client = get_chroma_client()