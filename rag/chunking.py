"""Split note text into overlapping word-based chunks for embedding."""

import re
from typing import List


def chunk_text(text: str, max_words: int = 200, overlap: int = 40) -> List[str]:
    """
    Split text into chunks of at most `max_words` words, each sharing `overlap`
    words with the previous chunk. Whitespace is collapsed; empty text gives [].
    """
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if not 0 <= overlap < max_words:
        raise ValueError("overlap must be >= 0 and < max_words")

    words = re.sub(r"\s+", " ", text).strip().split(" ")
    if words == [""]:
        return []

    step = max_words - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + max_words]))
        if start + max_words >= len(words):
            break
    return chunks
