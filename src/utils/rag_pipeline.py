"""FAISS RAG pipeline for indexing and searching ChartQA multimodal metadata."""

import pickle
from pathlib import Path
from typing import Any
import numpy as np

from src.models.exceptions import RAGPipelineError, VectorSearchError
from src.utils.embedding_generator import EmbeddingGenerator

# Optional import of FAISS with numpy L2 fallback
try:
    import faiss

    HAVE_FAISS = True
except ImportError:
    faiss = None
    HAVE_FAISS = False


class NumpyFlatL2Index:
    """Numpy-backed L2 distance index providing identical interface to FAISS IndexFlatL2."""

    def __init__(self, d: int) -> None:
        self.d = d
        self.vectors: list[np.ndarray] = []

    def add(self, x: np.ndarray) -> None:
        x_mat = np.atleast_2d(x).astype(np.float32)
        for row in x_mat:
            self.vectors.append(row)

    def search(self, x: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
        if not self.vectors:
            return np.array([[]]), np.array([[]])

        query = np.atleast_2d(x).astype(np.float32)
        matrix = np.array(self.vectors, dtype=np.float32)

        # L2 distances: ||q - v||^2
        dists_list: list[np.ndarray] = []
        indices_list: list[np.ndarray] = []

        for q in query:
            diffs = matrix - q
            sq_dists = np.sum(diffs ** 2, axis=1)
            top_k_idx = np.argsort(sq_dists)[:k]
            dists_list.append(sq_dists[top_k_idx])
            indices_list.append(top_k_idx)

        return np.array(dists_list), np.array(indices_list)

    @property
    def ntotal(self) -> int:
        return len(self.vectors)


class FAISSRAGPipeline:
    """RAG Indexing pipeline using FAISS IndexFlatL2 and metadata pickle storage."""

    def __init__(
        self,
        index_dir: Path | str = "models",
        embedding_generator: EmbeddingGenerator | None = None,
    ) -> None:
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.embedder = embedding_generator or EmbeddingGenerator()
        self.dimension = self.embedder.get_embedding_dimension()

        self.index: Any | None = None
        self.metadata_store: list[dict[str, Any]] = []

    def build_index(
        self,
        items: list[dict[str, Any]],
    ) -> tuple[Path, Path]:
        """Builds FAISS IndexFlatL2 from items containing 'question', 'chart_type', 'resolution_formula', 'answer'.

        Args:
            items: List of dictionary items.

        Returns:
            Tuple of (index_path, metadata_path).
        """
        if not items:
            raise RAGPipelineError("Cannot build FAISS index with empty item list.")

        questions = [item.get("question", "") for item in items]
        embeddings = self.embedder.encode(questions, convert_to_numpy=True, normalize_embeddings=True)
        embeddings = np.atleast_2d(embeddings).astype(np.float32)

        if HAVE_FAISS and faiss is not None:
            index = faiss.IndexFlatL2(self.dimension)
            index.add(embeddings)
        else:
            index = NumpyFlatL2Index(self.dimension)
            index.add(embeddings)

        self.index = index
        self.metadata_store = items

        return self.save_index()

    def save_index(
        self,
        index_filename: str = "index.faiss",
        metadata_filename: str = "metadata.pkl",
    ) -> tuple[Path, Path]:
        """Saves FAISS index and metadata store to disk."""
        if self.index is None:
            raise RAGPipelineError("No index built to save. Call build_index() first.")

        idx_path = self.index_dir / index_filename
        meta_path = self.index_dir / metadata_filename

        if HAVE_FAISS and faiss is not None and hasattr(faiss, "write_index"):
            faiss.write_index(self.index, str(idx_path))
        else:
            with open(idx_path, "wb") as f:
                pickle.dump(self.index, f)

        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata_store, f)

        return idx_path, meta_path

    def load_index(
        self,
        index_path: Path | str = "models/index.faiss",
        metadata_path: Path | str = "models/metadata.pkl",
    ) -> None:
        """Loads FAISS index and metadata store from disk."""
        idx_p = Path(index_path)
        meta_p = Path(metadata_path)

        if not idx_p.exists() or not meta_p.exists():
            raise RAGPipelineError(f"Index or metadata file not found at: {idx_p}, {meta_p}")

        if HAVE_FAISS and faiss is not None and hasattr(faiss, "read_index"):
            try:
                self.index = faiss.read_index(str(idx_p))
            except Exception:
                with open(idx_p, "rb") as f:
                    self.index = pickle.load(f)
        else:
            with open(idx_p, "rb") as f:
                self.index = pickle.load(f)

        with open(meta_p, "rb") as f:
            self.metadata_store = pickle.load(f)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Searches the vector index for query string and returns top_k nearest items with distance scores."""
        if self.index is None or not self.metadata_store:
            # Try loading default saved index
            default_idx = self.index_dir / "index.faiss"
            default_meta = self.index_dir / "metadata.pkl"
            if default_idx.exists() and default_meta.exists():
                self.load_index(default_idx, default_meta)
            else:
                raise VectorSearchError("FAISS Index is not built or loaded.")

        q_embedding = self.embedder.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        q_embedding = np.atleast_2d(q_embedding).astype(np.float32)

        k_effective = min(top_k, len(self.metadata_store))
        distances, indices = self.index.search(q_embedding, k_effective)

        results: list[dict[str, Any]] = []
        if len(indices) > 0:
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.metadata_store):
                    continue
                item = dict(self.metadata_store[idx])
                item["distance"] = float(dist)
                item["similarity_score"] = float(1.0 / (1.0 + dist))
                results.append(item)

        return results
