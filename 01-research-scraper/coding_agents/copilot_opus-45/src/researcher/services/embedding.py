"""Embedding service with litellm and sentence-transformers fallback."""

import logging
import numpy as np
from typing import Optional
import os

from researcher.config import Config

logger = logging.getLogger("papertrail.embedding")


class EmbeddingService:
    """Embedding service with automatic fallback to sentence-transformers."""

    _instance: Optional["EmbeddingService"] = None

    def __new__(cls) -> "EmbeddingService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize embedding service."""
        if self._initialized:
            return

        self._litellm_available = False
        self._sentence_transformer = None
        self._using_fallback = False
        self._initialized = True

        # Try to initialize litellm embeddings
        if Config.has_embedding_config():
            logger.info(
                f"Attempting to use litellm embeddings: {Config.DEFAULT_EMBEDDING_MODEL}"
            )
            self._litellm_available = self._test_litellm_embeddings()

        if not self._litellm_available:
            logger.warning(
                "litellm embeddings unavailable, initializing sentence-transformers fallback"
            )
            self._initialize_sentence_transformer()

    def _test_litellm_embeddings(self) -> bool:
        """Test if litellm embeddings work."""
        try:
            import litellm

            response = litellm.embedding(
                model=Config.DEFAULT_EMBEDDING_MODEL,
                input=["test"],
            )
            if response and response.data:
                logger.info("litellm embeddings working successfully")
                return True
        except Exception as e:
            logger.warning(f"litellm embeddings test failed: {e}")
        return False

    def _initialize_sentence_transformer(self) -> None:
        """Initialize sentence-transformers as fallback."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(
                f"Loading sentence-transformers model: {Config.FALLBACK_EMBEDDING_MODEL}"
            )
            self._sentence_transformer = SentenceTransformer(
                Config.FALLBACK_EMBEDDING_MODEL
            )
            self._using_fallback = True
            logger.info("sentence-transformers fallback initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentence-transformers: {e}")
            raise RuntimeError(
                "Neither litellm nor sentence-transformers available for embeddings"
            )

    @property
    def using_fallback(self) -> bool:
        """Check if using fallback embeddings."""
        return self._using_fallback

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return Config.EMBEDDING_DIMENSION

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        logger.debug(f"Generating embeddings for {len(texts)} texts")

        if self._litellm_available:
            return self._embed_with_litellm(texts)
        else:
            return self._embed_with_sentence_transformer(texts)

    def _embed_with_litellm(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings using litellm."""
        try:
            import litellm

            response = litellm.embedding(
                model=Config.DEFAULT_EMBEDDING_MODEL,
                input=texts,
            )
            embeddings = [
                np.array(item["embedding"], dtype=np.float32)
                for item in response.data
            ]
            logger.debug(f"Generated {len(embeddings)} embeddings with litellm")
            return embeddings
        except Exception as e:
            logger.warning(f"litellm embedding failed, falling back: {e}")
            # Fall back to sentence-transformers
            if not self._sentence_transformer:
                self._initialize_sentence_transformer()
            self._litellm_available = False
            self._using_fallback = True
            return self._embed_with_sentence_transformer(texts)

    def _embed_with_sentence_transformer(self, texts: list[str]) -> list[np.ndarray]:
        """Generate embeddings using sentence-transformers."""
        if not self._sentence_transformer:
            self._initialize_sentence_transformer()

        embeddings = self._sentence_transformer.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        logger.debug(
            f"Generated {len(embeddings)} embeddings with sentence-transformers"
        )
        return [np.array(e, dtype=np.float32) for e in embeddings]

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return float(
            np.dot(embedding1, embedding2)
            / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        )

    def find_similar(
        self,
        query_embedding: np.ndarray,
        embeddings: list[tuple[str, np.ndarray]],
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Find most similar embeddings."""
        if not embeddings:
            return []

        similarities = []
        for paper_id, emb in embeddings:
            sim = self.similarity(query_embedding, emb)
            similarities.append((paper_id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# Singleton instance
def get_embedding_service() -> EmbeddingService:
    """Get the embedding service instance."""
    return EmbeddingService()
