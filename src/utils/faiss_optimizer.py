"""FAISSOptimizer handling fast vector index caching and similarity search."""

import logging
import time
from typing import Any

logger = logging.getLogger("FAISSOptimizer")


class FAISSOptimizer:
    """Optimizer for FAISS vector RAG index queries and embedding caching."""

    def __init__(self) -> None:
        self.embedding_cache: dict[str, list[float]] = {}

    def get_cached_embedding(self, text: str) -> list[float] | None:
        """Retrieves cached vector embedding for query text."""
        return self.embedding_cache.get(text)

    def cache_embedding(self, text: str, embedding: list[float]) -> None:
        """Stores query vector embedding in cache."""
        self.embedding_cache[text] = embedding

    def fast_vector_search(
        self,
        query_vector: list[float],
        index_vectors: list[list[float]],
        top_k: int = 3,
    ) -> tuple[list[int], float]:
        """Performs optimized dot product similarity search.

        Args:
            query_vector: Normalized query embedding.
            index_vectors: List of stored vector embeddings.
            top_k: Top K nearest neighbor matches.

        Returns:
            Tuple of (matched index IDs list, search_latency_sec).
        """
        start_t = time.time()
        scores = []
        for idx, vec in enumerate(index_vectors):
            # Compute dot product
            dot = sum(a * b for a, b in zip(query_vector, vec))
            scores.append((idx, dot))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_ids = [s[0] for s in scores[:top_k]]
        latency = time.time() - start_t
        logger.info(f"FAISSOptimizer: Vector search completed in {latency:.6f}s")
        return top_ids, latency
