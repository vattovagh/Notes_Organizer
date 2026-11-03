"""Local sentence-embedding wrapper (no API key needed)."""

from typing import List

DEFAULT_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_model_cache = {}


def embed(texts: List[str], model_name: str = DEFAULT_EMBED_MODEL) -> List[List[float]]:
    """Return L2-normalized embeddings, so cosine similarity equals dot product."""
    if model_name not in _model_cache:
        from sentence_transformers import SentenceTransformer  # heavy import, load lazily
        _model_cache[model_name] = SentenceTransformer(model_name)
    vectors = _model_cache[model_name].encode(texts, normalize_embeddings=True)
    return vectors.tolist()
