"""Tests for embedding service."""

import pytest
import numpy as np

from researcher.services.embedding import EmbeddingService


class TestEmbeddingService:
    """Test cases for EmbeddingService."""

    def test_fallback_embedding(self):
        """Test that fallback embedding works when litellm is not configured."""
        service = EmbeddingService()
        
        # Should use fallback since litellm is not configured
        embedding = service.embed("This is a test sentence.")
        
        assert embedding is not None
        assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
        assert isinstance(embedding, np.ndarray)

    def test_embedding_dimension(self):
        """Test embedding dimension."""
        service = EmbeddingService()
        
        embedding = service.embed("Test sentence for dimension check.")
        
        # Sentence transformers all-MiniLM-L6-v2 has dimension 384
        assert len(embedding) == service.dimension

    def test_similar_texts_have_similar_embeddings(self):
        """Test that similar texts produce similar embeddings."""
        service = EmbeddingService()
        
        text1 = "Machine learning is a subset of artificial intelligence."
        text2 = "AI includes machine learning as one of its branches."
        text3 = "The weather today is sunny and warm."
        
        emb1 = service.embed(text1)
        emb2 = service.embed(text2)
        emb3 = service.embed(text3)
        
        sim_1_2 = service.similarity(emb1, emb2)
        sim_1_3 = service.similarity(emb1, emb3)
        
        # Similar texts should have higher similarity
        assert sim_1_2 > sim_1_3, f"sim(1,2)={sim_1_2:.3f} should be > sim(1,3)={sim_1_3:.3f}"

    def test_similarity_computation(self):
        """Test similarity computation."""
        service = EmbeddingService()
        
        # Identical vectors should have similarity 1.0
        vec = np.array([1.0, 0.0, 0.0])
        sim = service.similarity(vec, vec)
        assert abs(sim - 1.0) < 0.001
        
        # Orthogonal vectors should have similarity 0.0
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        sim = service.similarity(vec1, vec2)
        assert abs(sim) < 0.001

    def test_empty_text_handling(self):
        """Test handling of empty text."""
        service = EmbeddingService()
        
        # Empty string should still return an embedding
        embedding = service.embed("")
        assert embedding is not None
        assert len(embedding) > 0

    def test_batch_embedding(self):
        """Test batch embedding functionality."""
        service = EmbeddingService()
        
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence.",
        ]
        
        embeddings = service.embed_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(e) == 384 for e in embeddings)

    def test_fallback_status(self):
        """Test fallback status reporting."""
        service = EmbeddingService()
        
        # Without litellm configured, should use fallback
        assert service.using_fallback
