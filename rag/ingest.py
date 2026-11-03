"""Ingest note images (via Google Vision OCR) or .txt files into the vector store."""

import os
from typing import List, Tuple

from classify_note import classify_text
from rag.chunking import chunk_text
from rag.store import add_chunks

IMAGE_EXTS = (".jpg", ".jpeg", ".png")
TEXT_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extracted_texts")


def load_text(path: str) -> str:
    """Read a .txt note directly; OCR an image once and cache the text on disk."""
    if path.lower().endswith(".txt"):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()

    stem = os.path.splitext(os.path.basename(path))[0]
    cache_path = os.path.join(TEXT_CACHE_DIR, stem + ".txt")
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return f.read()

    from scan_contents import detect_handwritten_text  # needs Google Vision credentials
    text = detect_handwritten_text(path)
    os.makedirs(TEXT_CACHE_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def ingest_folder(folder: str, max_words: int = 200, overlap: int = 40) -> List[Tuple[str, str, int]]:
    """Ingest every image/.txt note in `folder`. Returns (source, subject, n_chunks) rows."""
    rows = []
    for filename in sorted(os.listdir(folder)):
        if not filename.lower().endswith(IMAGE_EXTS + (".txt",)):
            continue
        source = os.path.splitext(filename)[0]
        try:
            text = load_text(os.path.join(folder, filename))
            if text.strip() == "No text detected":
                text = ""
            subject = classify_text(text)
            n = add_chunks(source, subject, chunk_text(text, max_words, overlap))
            rows.append((source, subject, n))
            print(f"  {filename} -> {subject}, {n} chunks")
        except Exception as e:
            print(f"  {filename} -> Error: {e}")
    return rows
