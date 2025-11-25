"""Embedding storage and search service."""

import logging
import pickle
from pathlib import Path
from typing import Optional
import numpy as np

from researcher.config import Config
from researcher.services.embedding import get_embedding_service

logger = logging.getLogger("papertrail.embedding_store")


class EmbeddingStore:
    """Store and search embeddings."""

    _instance: Optional["EmbeddingStore"] = None

    def __new__(cls) -> "EmbeddingStore":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize embedding store."""
        if self._initialized:
            return

        self._embeddings: dict[str, np.ndarray] = {}
        self._store_path = Config.EMBEDDINGS_PATH / "embeddings.pkl"
        self._initialized = True
        self._load_embeddings()

    def _load_embeddings(self) -> None:
        """Load embeddings from disk."""
        if self._store_path.exists():
            try:
                with open(self._store_path, "rb") as f:
                    self._embeddings = pickle.load(f)
                logger.info(f"Loaded {len(self._embeddings)} embeddings from disk")
            except Exception as e:
                logger.error(f"Failed to load embeddings: {e}")
                self._embeddings = {}
        else:
            logger.info("No existing embeddings found")

    def _save_embeddings(self) -> None:
        """Save embeddings to disk."""
        try:
            with open(self._store_path, "wb") as f:
                pickle.dump(self._embeddings, f)
            logger.debug(f"Saved {len(self._embeddings)} embeddings to disk")
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")

    def add_embedding(self, paper_id: str, embedding: np.ndarray) -> None:
        """Add an embedding for a paper."""
        logger.debug(f"Adding embedding for paper: {paper_id}")
        self._embeddings[paper_id] = embedding
        self._save_embeddings()

    def get_embedding(self, paper_id: str) -> Optional[np.ndarray]:
        """Get embedding for a paper."""
        return self._embeddings.get(paper_id)

    def has_embedding(self, paper_id: str) -> bool:
        """Check if embedding exists for a paper."""
        return paper_id in self._embeddings

    def remove_embedding(self, paper_id: str) -> bool:
        """Remove embedding for a paper."""
        if paper_id in self._embeddings:
            del self._embeddings[paper_id]
            self._save_embeddings()
            return True
        return False

    def get_all_embeddings(self) -> list[tuple[str, np.ndarray]]:
        """Get all embeddings."""
        return list(self._embeddings.items())

    def search_similar(
        self,
        query: str,
        top_k: int = 10,
        exclude_ids: Optional[set[str]] = None,
    ) -> list[tuple[str, float]]:
        """Search for similar papers by query text."""
        if not self._embeddings:
            return []

        embedding_service = get_embedding_service()
        query_embedding = embedding_service.embed(query)

        embeddings_to_search = [
            (pid, emb)
            for pid, emb in self._embeddings.items()
            if exclude_ids is None or pid not in exclude_ids
        ]

        return embedding_service.find_similar(
            query_embedding,
            embeddings_to_search,
            top_k=top_k,
        )

    def search_similar_to_paper(
        self,
        paper_id: str,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Find papers similar to a given paper."""
        paper_embedding = self._embeddings.get(paper_id)
        if paper_embedding is None:
            return []

        embedding_service = get_embedding_service()
        embeddings_to_search = [
            (pid, emb)
            for pid, emb in self._embeddings.items()
            if pid != paper_id
        ]

        return embedding_service.find_similar(
            paper_embedding,
            embeddings_to_search,
            top_k=top_k,
        )

    def count(self) -> int:
        """Get number of stored embeddings."""
        return len(self._embeddings)


# Singleton instance
def get_embedding_store() -> EmbeddingStore:
    """Get the embedding store instance."""
    return EmbeddingStore()
