from backend.services.ingestion.embedder import get_chroma_embedding_fn


def test_get_chroma_embedding_fn_returns_correct_type():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    fn = get_chroma_embedding_fn()
    assert isinstance(fn, SentenceTransformerEmbeddingFunction)


def test_get_chroma_embedding_fn_uses_multilingual_model():
    fn = get_chroma_embedding_fn()
    # chromadb exposes model_name (not _model_name) on SentenceTransformerEmbeddingFunction
    assert fn.model_name == "paraphrase-multilingual-MiniLM-L12-v2"


def test_model_name_constant_is_updated():
    import backend.services.ingestion.embedder as emb
    assert emb._model_name == "paraphrase-multilingual-MiniLM-L12-v2"
