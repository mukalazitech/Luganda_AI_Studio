# backend/services/ingestion/embedder.py

"""
Embedder
=========

Wraps the sentence-transformers model to generate text embeddings.

Model used:
  paraphrase-multilingual-MiniLM-L12-v2

Why this model?
  - Multilingual: trained on 50+ languages, handles Luganda far better than
    the English-only all-MiniLM-L6-v2 it replaced
  - Same 384-dimensional output — drop-in replacement
  - ~470 MB (vs ~90 MB for the old model) — acceptable for this hardware
  - Runs on CPU (no VRAM required)
  - ChromaDB supports it via SentenceTransformerEmbeddingFunction

IMPORTANT — two public names for the same model loader:

  get_model()            — used by the ingestion pipeline
  get_embedding_model()  — used by translation/service.py (kept for compatibility)

Both return the same loaded SentenceTransformer object.
Do not remove either — both are actively used.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_model_name = "paraphrase-multilingual-MiniLM-L12-v2"

# The model is loaded lazily (only when first needed)
# This avoids slow startup if ingestion isn't being used
_model = None


def get_chroma_embedding_fn():
    """
    Return a ChromaDB-compatible embedding function using the multilingual model.

    Pass this to get_or_create_collection() and query() so ChromaDB uses
    the same model for both ingestion and search — no mismatch possible.

    ChromaDB caches the underlying model internally so it is only loaded
    once per process regardless of how many times this function is called.
    """
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    return SentenceTransformerEmbeddingFunction(model_name=_model_name)


def get_model():
    """
    Load and return the sentence-transformers model.
    Uses lazy loading — model is only downloaded/loaded once.

    First call: downloads ~470MB model (if not cached) and loads it.
    Subsequent calls: returns the already-loaded model instantly.
    """
    global _model

    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "sentence-transformers is not installed.\n"
            "Install it with: pip install sentence-transformers"
        )

    logger.info(f"Loading embedding model: {_model_name}")
    logger.info("(This may take a moment the first time — model will be cached)")

    _model = SentenceTransformer(_model_name)
    logger.info("Embedding model loaded successfully.")
    return _model


def get_embedding_model():
    """
    Alias for get_model().

    This name is used by backend/services/translation/service.py.
    Kept here so that file does not need to be changed.
    """
    return get_model()


def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """
    Generate embeddings for a list of text strings.

    Parameters
    ----------
    texts : list of str
        The texts to embed. Each text becomes one 384-dim vector.
    batch_size : int
        How many texts to embed at once. Default 64 is safe for 16GB RAM.

    Returns
    -------
    list of list of float
        One embedding vector per input text.

    Example
    -------
    >>> vecs = embed_texts(["ssebo", "sir, mister"])
    >>> len(vecs)        # 2 embeddings
    2
    >>> len(vecs[0])     # 384 dimensions
    384
    """
    if not texts:
        return []

    model = get_model()

    logger.info(f"Embedding {len(texts)} texts in batches of {batch_size}...")

    # SentenceTransformer handles batching internally but we can specify it
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
    )

    logger.info(f"Embedding complete. Shape: {embeddings.shape}")

    # Convert numpy arrays to plain Python lists for ChromaDB compatibility
    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """
    Embed a single text string.
    Convenience wrapper around embed_texts.

    Example
    -------
    >>> vec = embed_single("webale nyo")
    >>> len(vec)
    384
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text.")

    results = embed_texts([text])
    return results[0]
