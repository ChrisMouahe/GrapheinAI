"""RetrievalAgent performing semantic vector search over ChartQA RAG index."""

from pathlib import Path
from typing import Any

from src.models.chart import RAGRetrievalResult
from src.utils.embedding_generator import EmbeddingGenerator
from src.utils.rag_pipeline import FAISSRAGPipeline


class RetrievalAgent:
    """Agent for retrieving relevant ChartQA examples using FAISS vector search."""

    def __init__(
        self,
        index_path: Path | str = "models/index.faiss",
        metadata_path: Path | str = "models/metadata.pkl",
        embedding_generator: EmbeddingGenerator | None = None,
    ) -> None:
        self.pipeline = FAISSRAGPipeline(
            index_dir=Path(index_path).parent if index_path else Path("models"),
            embedding_generator=embedding_generator,
        )
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        if self.index_path.exists() and self.metadata_path.exists():
            self.pipeline.load_index(self.index_path, self.metadata_path)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Retrieves top-k most similar ChartQA examples for a query string.

        Args:
            query: Question or search query string.
            top_k: Number of nearest items to retrieve (default: 3).

        Returns:
            List of dictionaries containing retrieved question, chart_type, resolution_formula, answer, and distance.
        """
        return self.pipeline.search(query=query, top_k=top_k)

    def retrieve_schema(self, query: str, top_k: int = 3) -> RAGRetrievalResult:
        """Retrieves top-k results wrapped in Pydantic v2 RAGRetrievalResult schema."""
        results = self.retrieve(query=query, top_k=top_k)
        return RAGRetrievalResult(
            query=query,
            top_k=top_k,
            results=results,
        )

    def reset_index(self) -> None:
        """Flushes in-memory FAISS index context for isolated session execution."""
        if hasattr(self.pipeline, "index") and self.pipeline.index is not None:
            try:
                self.pipeline.index.reset()
            except Exception:
                pass
