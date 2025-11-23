"""Basic tests for PaperTrail core functionality."""

import pytest
from researcher.embeddings import embedding_service
from researcher.llm import llm_service


def test_embedding_service_available():
    """Test that embedding service is available (either litellm or fallback)."""
    assert embedding_service.is_available()
    print(f"✓ Embedding service available: {embedding_service.current_model}")


def test_embedding_generation():
    """Test embedding generation."""
    text = "This is a test paper about machine learning."
    embedding = embedding_service.generate_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)
    print(f"✓ Generated embedding with dimension: {len(embedding)}")


def test_embedding_similarity():
    """Test similarity computation between embeddings."""
    text1 = "Machine learning is a subset of artificial intelligence."
    text2 = "Deep learning is a type of machine learning."
    text3 = "The weather is sunny today."
    
    emb1 = embedding_service.generate_embedding(text1)
    emb2 = embedding_service.generate_embedding(text2)
    emb3 = embedding_service.generate_embedding(text3)
    
    sim_related = embedding_service.compute_similarity(emb1, emb2)
    sim_unrelated = embedding_service.compute_similarity(emb1, emb3)
    
    # Related texts should have higher similarity than unrelated
    assert sim_related > sim_unrelated
    print(f"✓ Similarity test passed: related={sim_related:.3f}, unrelated={sim_unrelated:.3f}")


def test_llm_service_status():
    """Test LLM service status check."""
    status = llm_service.get_status()
    
    assert 'available' in status
    assert 'model' in status
    assert 'backfill_queue_size' in status
    
    print(f"✓ LLM Status: available={status['available']}, model={status['model']}")


def test_llm_graceful_degradation():
    """Test that LLM returns placeholders when unavailable."""
    # This test validates the placeholder system
    result = llm_service.generate_paper_summary(
        "Test Paper",
        "This is a test abstract about machine learning.",
        None
    )
    
    assert 'summary' in result
    assert 'needs_llm_processing' in result
    
    if not llm_service.is_available():
        # If LLM unavailable, should return placeholders
        assert result['summary'] == '<summary>'
        assert result['needs_llm_processing'] is True
        print("✓ LLM graceful degradation working (placeholders returned)")
    else:
        # If LLM available, should return actual content
        assert result['summary'] != '<summary>'
        assert result['needs_llm_processing'] is False
        print("✓ LLM working (actual content returned)")


if __name__ == "__main__":
    print("\nRunning PaperTrail Core Tests...\n")
    
    test_embedding_service_available()
    test_embedding_generation()
    test_embedding_similarity()
    test_llm_service_status()
    test_llm_graceful_degradation()
    
    print("\n✅ All tests passed!")
