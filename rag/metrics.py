"""Retrieval metrics (pure Python, no heavy imports)."""

from typing import Dict, List


def first_relevant_rank(retrieved_sources: List[str], relevant: List[str]) -> int:
    """1-based rank of the first retrieved source that is relevant, or 0 if none."""
    for rank, source in enumerate(retrieved_sources, 1):
        if source in relevant:
            return rank
    return 0


def retrieval_scores(ranks: List[int], k: int) -> Dict[str, float]:
    """hit@k and MRR from first-relevant ranks (0 = miss). Empty input scores 0."""
    if not ranks:
        return {f"hit@{k}": 0.0, "mrr": 0.0}
    hits = sum(1 for r in ranks if 0 < r <= k)
    mrr = sum(1 / r for r in ranks if r > 0)
    return {f"hit@{k}": hits / len(ranks), "mrr": mrr / len(ranks)}
