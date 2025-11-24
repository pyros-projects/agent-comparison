import logging
import os
from typing import List, Optional, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import litellm
from ..models.database import db
from ..models.schemas import Embedding

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating embeddings with litellm and sentence-transformers fallback"""
    
    def __init__(self):
        self.default_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small")
        self.fallback_model = None
        self._setup_fallback()
    
    def _setup_fallback(self):
        """Setup sentence-transformers as fallback"""
        try:
            self.fallback_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence-transformers fallback model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers fallback: {e}")
            self.fallback_model = None
    
    async def generate_embedding(self, text: str, paper_id: str) -> Optional[List[float]]:
        """Generate embedding for text using litellm with fallback to sentence-transformers"""
        
        # Clean and prepare text
        if not text or not text.strip():
            logger.warning(f"Empty text provided for paper {paper_id}")
            return None
        
        text = text.strip()
        if len(text) < 10:
            logger.warning(f"Text too short for paper {paper_id}: {len(text)} chars")
            return None
        
        # Try litellm first
        embedding = await self._try_litellm_embedding(text)
        
        if embedding is None and self.fallback_model is not None:
            # Fallback to sentence-transformers
            logger.info(f"Using sentence-transformers fallback for paper {paper_id}")
            embedding = self._try_sentence_transformers_embedding(text)
        
        if embedding is None:
            logger.error(f"Failed to generate embedding for paper {paper_id}")
            return None
        
        # Store embedding in database
        try:
            embedding_doc = Embedding(
                paper_id=paper_id,
                embedding=embedding,
                model_name=self.default_model if embedding is not None else "sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Remove old embedding if exists
            db.embeddings.remove(db.embeddings.paper_id == paper_id)
            
            # Store new embedding
            db.embeddings.insert(embedding_doc.model_dump())
            logger.info(f"Embedding stored for paper {paper_id}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to store embedding for paper {paper_id}: {e}")
            return None
    
    async def _try_litellm_embedding(self, text: str) -> Optional[List[float]]:
        """Try to generate embedding using litellm"""
        try:
            response = await litellm.aembedding(
                model=self.default_model,
                input=[text]
            )
            
            if response and response.data and len(response.data) > 0:
                embedding = response.data[0].embedding
                logger.debug(f"Generated embedding with litellm, dimensions: {len(embedding)}")
                return embedding
            
        except Exception as e:
            logger.warning(f"litellm embedding failed: {e}")
        
        return None
    
    def _try_sentence_transformers_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding using sentence-transformers fallback"""
        try:
            if self.fallback_model is None:
                return None
            
            embedding = self.fallback_model.encode([text])[0].tolist()
            logger.debug(f"Generated embedding with sentence-transformers, dimensions: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Sentence-transformers embedding failed: {e}")
            return None
    
    def get_embedding(self, paper_id: str) -> Optional[List[float]]:
        """Retrieve embedding for a paper"""
        try:
            result = db.embeddings.get(db.embeddings.paper_id == paper_id)
            if result:
                return result['embedding']
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve embedding for paper {paper_id}: {e}")
            return None
    
    def search_similar(self, query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find most similar papers using cosine similarity"""
        try:
            query_embedding = np.array(query_embedding)
            results = []
            
            # Get all embeddings
            all_embeddings = db.embeddings.all()
            
            for emb in all_embeddings:
                paper_embedding = np.array(emb['embedding'])
                similarity = np.dot(query_embedding, paper_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(paper_embedding)
                )
                
                results.append({
                    'paper_id': emb['paper_id'],
                    'similarity': float(similarity)
                })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []

# Global embedding service instance
embedding_service = EmbeddingService()
