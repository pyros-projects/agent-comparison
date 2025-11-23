"""Embedding service with litellm primary and sentence-transformers fallback."""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

from researcher.config import settings
from researcher.logger import setup_logger

logger = setup_logger(__name__)


class EmbeddingService:
    """Generate embeddings with automatic fallback."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.litellm_available = False
        self.fallback_model = None
        self.current_model = None
        
        # Try to initialize litellm
        self._try_litellm()
        
        # If litellm fails, use fallback
        if not self.litellm_available:
            self._init_fallback()
    
    def _try_litellm(self):
        """Attempt to initialize litellm embedding."""
        if not settings.default_embedding_model:
            logger.warning("No DEFAULT_EMBEDDING_MODEL configured, skipping litellm")
            return
        
        try:
            import litellm
            # Test litellm with a simple embedding
            logger.info(f"Testing litellm embedding with model: {settings.default_embedding_model}")
            test_response = litellm.embedding(
                model=settings.default_embedding_model,
                input=["test"]
            )
            if test_response and hasattr(test_response, 'data') and len(test_response.data) > 0:
                self.litellm_available = True
                self.current_model = settings.default_embedding_model
                logger.info(f"✓ litellm embedding available: {settings.default_embedding_model}")
            else:
                logger.warning("litellm test returned invalid response")
        except Exception as e:
            logger.warning(f"litellm embedding unavailable: {e}")
            logger.info("Will use sentence-transformers fallback")
    
    def _init_fallback(self):
        """Initialize sentence-transformers fallback model."""
        try:
            logger.info(f"Initializing fallback embedding model: {settings.fallback_embedding_model}")
            self.fallback_model = SentenceTransformer(settings.fallback_embedding_model)
            self.current_model = settings.fallback_embedding_model
            logger.info(f"✓ Fallback embedding model loaded: {settings.fallback_embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load fallback embedding model: {e}")
            raise RuntimeError("No embedding model available") from e
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            if self.litellm_available:
                return self._generate_litellm(text)
            else:
                return self._generate_fallback(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Try fallback if litellm fails
            if self.litellm_available and self.fallback_model is None:
                logger.info("litellm failed, switching to fallback")
                self.litellm_available = False
                self._init_fallback()
                return self._generate_fallback(text)
            raise
    
    def _generate_litellm(self, text: str) -> List[float]:
        """Generate embedding using litellm."""
        import litellm
        logger.debug(f"Generating litellm embedding (length: {len(text)} chars)")
        response = litellm.embedding(
            model=settings.default_embedding_model,
            input=[text]
        )
        embedding = response.data[0]['embedding']
        logger.debug(f"Generated embedding dimension: {len(embedding)}")
        return embedding
    
    def _generate_fallback(self, text: str) -> List[float]:
        """Generate embedding using sentence-transformers."""
        if self.fallback_model is None:
            self._init_fallback()
        
        logger.debug(f"Generating fallback embedding (length: {len(text)} chars)")
        embedding = self.fallback_model.encode(text, convert_to_numpy=True)
        result = embedding.tolist()
        logger.debug(f"Generated embedding dimension: {len(result)}")
        return result
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between -1 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return float(similarity)
    
    def is_available(self) -> bool:
        """Check if embedding service is available."""
        return self.litellm_available or self.fallback_model is not None
    
    def get_model_info(self) -> dict:
        """Get current model information."""
        return {
            "model": self.current_model,
            "using_fallback": not self.litellm_available,
            "available": self.is_available()
        }


# Global embedding service instance
embedding_service = EmbeddingService()
