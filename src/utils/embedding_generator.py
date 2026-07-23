"""NLP Embedding Generator using sentence-transformers/all-MiniLM-L6-v2.

Provides local model caching, vector generation, and full typing for ChartQA semantic search.
"""

from pathlib import Path

import numpy as np

from src.models.exceptions import EmbeddingGenerationError

# Optional import of SentenceTransformer with fallback vectorizer for offline resilience
try:
    from sentence_transformers import SentenceTransformer

    HAVE_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None
    HAVE_SENTENCE_TRANSFORMERS = False

from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingGenerator:
    """Generates dense vector embeddings for text queries and ChartQA context metadata."""

    DEFAULT_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_DIMENSION: int = 384

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir: Path | str = "models/cache",
    ) -> None:
        """Initializes EmbeddingGenerator with model name and local cache directory.

        Args:
            model_name: HuggingFace model identifier.
            cache_dir: Local path for caching model weights.
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self._fallback_vectorizer: TfidfVectorizer | None = None
        self._embedding_dim = self.DEFAULT_DIMENSION

        self._init_model()

    def _init_model(self) -> None:
        """Attempts to load SentenceTransformer model from cache/remote, or sets up fallback."""
        if HAVE_SENTENCE_TRANSFORMERS and SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(
                    self.model_name,
                    cache_folder=str(self.cache_dir),
                )
                dim = getattr(self.model, "get_embedding_dimension", None) or getattr(
                    self.model, "get_sentence_embedding_dimension", None
                )
                self._embedding_dim = dim() if callable(dim) else 384
                return
            except Exception:
                pass

        # Fallback vectorizer if sentence-transformers is offline or unavailable
        self._fallback_vectorizer = TfidfVectorizer(max_features=self.DEFAULT_DIMENSION)

    def encode(
        self,
        text: str | list[str],
        convert_to_numpy: bool = True,
        normalize_embeddings: bool = True,
    ) -> np.ndarray:
        """Generates dense vector embeddings for input text or list of texts.

        Args:
            text: A single string or list of text strings.
            convert_to_numpy: If True, returns numpy ndarray.
            normalize_embeddings: If True, L2-normalizes embedding vectors.

        Returns:
            np.ndarray of shape (N, dimension) or (dimension,).

        Raises:
            EmbeddingGenerationError: If input is invalid or encoding fails.
        """
        if not text:
            raise EmbeddingGenerationError("Input text for embedding generation cannot be empty.")

        is_single = isinstance(text, str)
        text_list: list[str] = [text] if is_single else list(text)

        try:
            if self.model is not None:
                embeddings = self.model.encode(
                    text_list,
                    convert_to_numpy=True,
                    normalize_embeddings=normalize_embeddings,
                )
            else:
                embeddings = self._encode_fallback(text_list, normalize_embeddings)

            embeddings = np.asarray(embeddings, dtype=np.float32)

            if is_single and len(embeddings.shape) == 2:
                return embeddings[0]
            return embeddings

        except Exception as e:
            raise EmbeddingGenerationError(f"Failed to generate embeddings: {e}") from e

    def _encode_fallback(self, texts: list[str], normalize: bool) -> np.ndarray:
        """Fallback embedding generator using TF-IDF padded/truncated to 384 dimensions."""
        if self._fallback_vectorizer is None:
            self._fallback_vectorizer = TfidfVectorizer(max_features=self.DEFAULT_DIMENSION)

        # Fit or transform
        try:
            vecs = self._fallback_vectorizer.transform(texts).toarray()
        except Exception:
            vecs = self._fallback_vectorizer.fit_transform(texts).toarray()

        n_samples, n_feats = vecs.shape
        target_dim = self.DEFAULT_DIMENSION

        if n_feats < target_dim:
            padded = np.zeros((n_samples, target_dim), dtype=np.float32)
            padded[:, :n_feats] = vecs
            vecs = padded
        else:
            vecs = vecs[:, :target_dim]

        if normalize:
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vecs = vecs / norms

        return vecs.astype(np.float32)

    def get_embedding_dimension(self) -> int:
        """Returns the dimensionality of generated embedding vectors."""
        return self._embedding_dim
