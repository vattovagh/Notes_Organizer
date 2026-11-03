"""Chroma vector store holding note chunks."""

import os
from typing import Dict, List, Optional

from rag.embeddings import embed

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".chroma")
COLLECTION = "notes"


def _collection(db_dir: str = DB_DIR):
    import chromadb
    client = chromadb.PersistentClient(path=db_dir)
    return client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def add_chunks(source: str, subject: str, chunks: List[str], db_dir: str = DB_DIR) -> int:
    """Upsert chunks for one note. Ids are deterministic, so re-ingesting is idempotent."""
    if not chunks:
        return 0
    _collection(db_dir).upsert(
        ids=[f"{source}::{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embed(chunks),
        metadatas=[{"source": source, "subject": subject, "chunk": i} for i in range(len(chunks))],
    )
    return len(chunks)


def search(question: str, k: int = 4, subject: Optional[str] = None,
           db_dir: str = DB_DIR) -> List[Dict]:
    """Return the top-k chunks as dicts: text, source, subject, chunk, distance."""
    collection = _collection(db_dir)
    if collection.count() == 0:
        return []
    result = collection.query(
        query_embeddings=embed([question]),
        n_results=k,
        where={"subject": subject} if subject else None,
    )
    hits = []
    for text, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        hits.append({"text": text, "distance": dist, **meta})
    return hits
