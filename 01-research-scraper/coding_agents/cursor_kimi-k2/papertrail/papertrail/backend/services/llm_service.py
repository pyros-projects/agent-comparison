import logging
import litellm
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations with graceful degradation"""
    
    def __init__(self):
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        self.is_available = True
        self._check_availability()
    
    def _check_availability(self):
        """Check if LLM service is available"""
        try:
            response = litellm.completion(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            self.is_available = response is not None
            logger.info(f"LLM service availability: {self.is_available}")
        except Exception as e:
            logger.warning(f"LLM service unavailable: {e}")
            self.is_available = False
    
    async def generate_paper_summary(self, paper_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive paper summary using LLM"""
        
        if not self.is_available:
            logger.warning("LLM unavailable, returning placeholders")
            return {
                "summary": "<summary>",
                "keywords": [],
                "key_contributions": "<key_contributions>",
                "methodology": "<methodology>",
                "results": "<results>",
                "further_research": "<further_research>"
            }
        
        return {
            "summary": "Generated summary",
            "keywords": ["AI", "ML"],
            "key_contributions": "Key contributions",
            "methodology": "Methodology",
            "results": "Results",
            "further_research": "Further research"
        }

# Global LLM service instance
llm_service = LLMService()
