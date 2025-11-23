"""LLM service with graceful degradation and placeholder system."""

from typing import Optional, List, Dict, Any
import json

from researcher.config import settings
from researcher.logger import setup_logger
from researcher.database import db
from researcher.models import BackfillQueueItem

logger = setup_logger(__name__)


class LLMService:
    """LLM service with placeholder fallback and backfill queue."""
    
    def __init__(self):
        """Initialize LLM service."""
        self.available = False
        self.model = None
        self._test_availability()
    
    def _test_availability(self):
        """Test if LLM is available."""
        if not settings.default_model:
            logger.warning("No DEFAULT_MODEL configured, LLM unavailable")
            return
        
        try:
            import litellm
            logger.info(f"Testing LLM availability with model: {settings.default_model}")
            response = litellm.completion(
                model=settings.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                self.available = True
                self.model = settings.default_model
                logger.info(f"✓ LLM available: {settings.default_model}")
            else:
                logger.warning("LLM test returned invalid response")
        except Exception as e:
            logger.warning(f"LLM unavailable: {e}")
            logger.info("Will use placeholder system for LLM-generated fields")
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.available
    
    def generate_paper_summary(self, title: str, abstract: str, full_text: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive paper summary.
        
        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Optional full paper text
            
        Returns:
            Dictionary with summary fields or placeholders
        """
        if not self.available:
            logger.debug(f"LLM unavailable, returning placeholders for: {title}")
            return {
                "summary": "<summary>",
                "key_contributions": None,
                "methodology": "<methodology>",
                "results": "<results>",
                "keywords": None,
                "needs_llm_processing": True
            }
        
        try:
            logger.info(f"Generating LLM summary for: {title}")
            
            # Construct prompt
            content = f"Title: {title}\n\nAbstract: {abstract}"
            if full_text and len(full_text) < 20000:  # Limit context size
                content += f"\n\nFull Text (excerpt): {full_text[:20000]}"
            
            prompt = f"""Analyze this research paper and provide:
1. A concise summary (2-3 sentences)
2. Key contributions (3-5 bullet points)
3. Methodology overview (1-2 sentences)
4. Main results (1-2 sentences)
5. Keywords (5-7 relevant terms)

Paper:
{content}

Respond in JSON format:
{{
  "summary": "...",
  "key_contributions": ["...", "..."],
  "methodology": "...",
  "results": "...",
  "keywords": ["...", "..."]
}}"""
            
            import litellm
            response = litellm.completion(
                model=settings.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            logger.debug(f"LLM response: {content[:200]}...")
            
            # Parse JSON response
            # Try to extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            result["needs_llm_processing"] = False
            logger.info(f"✓ Generated summary for: {title}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            # Return placeholders on error
            return {
                "summary": "<summary>",
                "key_contributions": None,
                "methodology": "<methodology>",
                "results": "<results>",
                "keywords": None,
                "needs_llm_processing": True
            }
    
    def add_to_backfill_queue(self, paper_id: str, fields: List[str], priority: int = 0):
        """Add paper to backfill queue for later LLM processing.
        
        Args:
            paper_id: Paper ID
            fields: List of fields that need processing
            priority: Priority level (higher = more important)
        """
        item = BackfillQueueItem(
            paper_id=paper_id,
            fields_to_fill=fields,
            priority=priority
        )
        db.insert_backfill_item(item)
        logger.info(f"Added to backfill queue: {paper_id} (fields: {fields})")
    
    def extract_arguments(self, hypothesis: str, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract pro/contra arguments for a hypothesis from papers.
        
        Args:
            hypothesis: Theory/hypothesis to validate
            papers: List of paper dictionaries with title, abstract, full_text
            
        Returns:
            List of arguments with type, summary, relevance
        """
        if not self.available:
            logger.warning("LLM unavailable, cannot extract arguments")
            return []
        
        try:
            logger.info(f"Extracting arguments for hypothesis: {hypothesis}")
            
            arguments = []
            for paper in papers:
                prompt = f"""Given this hypothesis:
"{hypothesis}"

Analyze this research paper and determine if it supports or contradicts the hypothesis.

Paper Title: {paper['title']}
Abstract: {paper['abstract']}

Respond in JSON format:
{{
  "stance": "pro" or "contra" or "neutral",
  "relevance": 0.0 to 1.0,
  "summary": "Brief explanation of how this paper relates to the hypothesis",
  "key_quotes": ["relevant quote 1", "relevant quote 2"]
}}"""
                
                import litellm
                response = litellm.completion(
                    model=settings.default_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                
                # Parse JSON
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                result = json.loads(content)
                
                if result["stance"] != "neutral" and result["relevance"] > 0.3:
                    arguments.append({
                        "paper_id": paper["id"],
                        "paper_title": paper["title"],
                        "argument_type": result["stance"],
                        "relevance_score": result["relevance"],
                        "summary": result["summary"],
                        "key_quotes": result.get("key_quotes", [])
                    })
            
            logger.info(f"✓ Extracted {len(arguments)} arguments")
            return arguments
            
        except Exception as e:
            logger.error(f"Error extracting arguments: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get LLM service status."""
        return {
            "available": self.available,
            "model": self.model,
            "backfill_queue_size": len(db.get_backfill_queue())
        }


# Global LLM service instance
llm_service = LLMService()
