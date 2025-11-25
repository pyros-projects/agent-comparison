"""LLM service with graceful degradation and placeholder support."""

import logging
from typing import Optional

from researcher.config import Config

logger = logging.getLogger("papertrail.llm")


class LLMService:
    """LLM service with graceful degradation."""

    _instance: Optional["LLMService"] = None

    def __new__(cls) -> "LLMService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize LLM service."""
        if self._initialized:
            return

        self._available = False
        self._initialized = True

        if Config.has_llm_config():
            logger.info(f"Attempting to use LLM: {Config.DEFAULT_MODEL}")
            self._available = self._test_llm()
        else:
            logger.warning("No LLM configured (DEFAULT_MODEL not set)")

    def _test_llm(self) -> bool:
        """Test if LLM is available."""
        try:
            import litellm

            response = litellm.completion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=10,
            )
            if response and response.choices:
                logger.info("LLM is available and working")
                return True
        except Exception as e:
            logger.warning(f"LLM test failed: {e}")
        return False

    @property
    def available(self) -> bool:
        """Check if LLM is available."""
        return self._available

    def refresh_availability(self) -> bool:
        """Re-check LLM availability."""
        if Config.has_llm_config():
            self._available = self._test_llm()
        return self._available

    async def generate_summary(self, paper_title: str, abstract: str, full_text: str = "") -> str:
        """Generate a summary for a paper."""
        if not self._available:
            logger.info(f"LLM unavailable, returning placeholder for summary")
            return Config.PLACEHOLDER_SUMMARY

        try:
            import litellm

            content_to_summarize = abstract
            if full_text:
                # Use first 8000 chars of full text
                content_to_summarize = full_text[:8000]

            prompt = f"""Analyze this research paper and provide a structured summary:

Title: {paper_title}

Content:
{content_to_summarize}

Please provide a summary covering:
1. **Key Contributions**: Main novel contributions of this paper
2. **Methodology**: Research methods and approach used
3. **Results**: Main findings and results
4. **Answered Questions**: What research questions does this paper answer?
5. **Future Research**: Possible directions for further research

Be concise but comprehensive."""

            response = await litellm.acompletion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            
            if response and response.choices:
                summary = response.choices[0].message.content
                logger.info(f"Generated summary for: {paper_title[:50]}...")
                return summary
            
            return Config.PLACEHOLDER_SUMMARY
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            self._available = False
            return Config.PLACEHOLDER_SUMMARY

    async def extract_keywords(
        self, 
        paper_title: str, 
        abstract: str,
        existing_keywords: list[str] = None,
    ) -> list[str]:
        """Extract keywords from a paper, normalizing against existing keywords."""
        if not self._available:
            logger.info(f"LLM unavailable, returning placeholder for keywords")
            return [Config.PLACEHOLDER_KEYWORDS]

        try:
            import litellm

            # Build existing keywords context
            existing_context = ""
            if existing_keywords:
                existing_context = f"""
IMPORTANT: The following keywords already exist in our database. 
If any of your extracted keywords match these semantically (e.g., "LLM" matches "Large Language Model"), 
USE THE EXISTING KEYWORD instead of creating a new variation.

Existing keywords: {', '.join(existing_keywords[:100])}
"""

            prompt = f"""Extract 5-10 relevant keywords/key phrases from this research paper.
{existing_context}
Return only the keywords as a comma-separated list, nothing else.
Prefer shorter, canonical forms (e.g., "LLM" over "Large Language Models").

Title: {paper_title}

Abstract:
{abstract}"""

            response = await litellm.acompletion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            
            if response and response.choices:
                keywords_text = response.choices[0].message.content
                keywords = [k.strip() for k in keywords_text.split(",")]
                keywords = [k for k in keywords if k and not k.startswith("<")]
                logger.info(f"Extracted {len(keywords)} keywords for: {paper_title[:50]}...")
                return keywords
            
            return [Config.PLACEHOLDER_KEYWORDS]
        except Exception as e:
            logger.error(f"Failed to extract keywords: {e}")
            self._available = False
            return [Config.PLACEHOLDER_KEYWORDS]

    async def extract_questions_and_theories(
        self,
        paper_title: str,
        abstract: str,
        full_text: str = "",
    ) -> dict:
        """Extract questions answered and theories supported by a paper."""
        if not self._available:
            logger.info(f"LLM unavailable, returning placeholders for questions/theories")
            return {
                "questions_answered": [Config.PLACEHOLDER_ANALYSIS],
                "theories_supported": [Config.PLACEHOLDER_ANALYSIS],
            }

        try:
            import litellm
            import json

            content = abstract
            if full_text:
                content = full_text[:6000]

            prompt = f"""Analyze this research paper and extract:

1. **Questions Answered**: What specific research questions does this paper answer? List 3-5 questions.
2. **Theories Supported**: What theoretical positions, hypotheses, or claims does this paper support? List 2-4 theories.

Title: {paper_title}

Content:
{content}

Respond in JSON format:
{{
    "questions_answered": [
        "How can X be improved using Y?",
        "What is the relationship between A and B?"
    ],
    "theories_supported": [
        "Scaling improves model performance",
        "Attention mechanisms are sufficient for sequence modeling"
    ]
}}

Be specific and concise. Each question/theory should be a complete, standalone statement."""

            response = await litellm.acompletion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
            )
            
            if response and response.choices:
                result_text = response.choices[0].message.content
                
                try:
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text)
                    logger.info(f"Extracted {len(result.get('questions_answered', []))} questions, {len(result.get('theories_supported', []))} theories")
                    return {
                        "questions_answered": result.get("questions_answered", []),
                        "theories_supported": result.get("theories_supported", []),
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse questions/theories JSON")
                    return {
                        "questions_answered": [Config.PLACEHOLDER_ANALYSIS],
                        "theories_supported": [Config.PLACEHOLDER_ANALYSIS],
                    }
            
            return {
                "questions_answered": [Config.PLACEHOLDER_ANALYSIS],
                "theories_supported": [Config.PLACEHOLDER_ANALYSIS],
            }
        except Exception as e:
            logger.error(f"Failed to extract questions/theories: {e}")
            self._available = False
            return {
                "questions_answered": [Config.PLACEHOLDER_ANALYSIS],
                "theories_supported": [Config.PLACEHOLDER_ANALYSIS],
            }

    async def analyze_theory(
        self,
        theory: str,
        papers: list[dict],
    ) -> dict:
        """Analyze papers for/against a theory."""
        if not self._available:
            logger.warning("LLM unavailable, cannot perform theory analysis")
            return {
                "error": "LLM unavailable - Theory mode requires an active LLM connection",
                "pro_arguments": [],
                "contra_arguments": [],
                "analysis_summary": "",
            }

        try:
            import litellm

            # Build context from papers
            papers_context = ""
            for i, paper in enumerate(papers[:20], 1):  # Limit to 20 papers
                papers_context += f"""
Paper {i}: {paper.get('title', 'Unknown')}
arXiv ID: {paper.get('arxiv_id', 'Unknown')}
Abstract: {paper.get('abstract', '')[:500]}
---
"""

            prompt = f"""Analyze the following research papers in relation to this theory/hypothesis:

THEORY: {theory}

PAPERS:
{papers_context}

For each relevant paper, determine:
1. Does it SUPPORT (pro) or CONTRADICT (contra) the theory?
2. What is the relevance score (0.0 to 1.0)?
3. Provide a brief summary of how it relates to the theory
4. Include any key quotes or findings that support your analysis

Please respond in the following JSON format:
{{
    "pro_arguments": [
        {{
            "paper_index": 1,
            "relevance_score": 0.9,
            "summary": "This paper supports the theory because...",
            "key_quotes": ["Quote 1", "Quote 2"]
        }}
    ],
    "contra_arguments": [
        {{
            "paper_index": 2,
            "relevance_score": 0.8,
            "summary": "This paper contradicts the theory because...",
            "key_quotes": ["Quote 1"]
        }}
    ],
    "analysis_summary": "Overall analysis of how the evidence relates to the theory..."
}}

Only include papers that are actually relevant to the theory. Be thorough and objective."""

            response = await litellm.acompletion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
            )
            
            if response and response.choices:
                import json
                result_text = response.choices[0].message.content
                
                # Try to parse JSON from response
                try:
                    # Handle potential markdown code blocks
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text)
                    
                    # Enrich with paper data
                    for arg in result.get("pro_arguments", []):
                        idx = arg.get("paper_index", 1) - 1
                        if 0 <= idx < len(papers):
                            arg["paper_id"] = papers[idx].get("id", "")
                            arg["paper_title"] = papers[idx].get("title", "")
                    
                    for arg in result.get("contra_arguments", []):
                        idx = arg.get("paper_index", 1) - 1
                        if 0 <= idx < len(papers):
                            arg["paper_id"] = papers[idx].get("id", "")
                            arg["paper_title"] = papers[idx].get("title", "")
                    
                    logger.info(f"Theory analysis complete: {len(result.get('pro_arguments', []))} pro, {len(result.get('contra_arguments', []))} contra")
                    return result
                except json.JSONDecodeError:
                    logger.warning("Failed to parse theory analysis JSON")
                    return {
                        "error": "Failed to parse analysis results",
                        "raw_response": result_text,
                        "pro_arguments": [],
                        "contra_arguments": [],
                        "analysis_summary": "",
                    }
            
            return {
                "error": "No response from LLM",
                "pro_arguments": [],
                "contra_arguments": [],
                "analysis_summary": "",
            }
        except Exception as e:
            logger.error(f"Theory analysis failed: {e}")
            self._available = False
            return {
                "error": f"Analysis failed: {str(e)}",
                "pro_arguments": [],
                "contra_arguments": [],
                "analysis_summary": "",
            }

    async def extract_relationships(
        self,
        paper: dict,
        existing_papers: list[dict],
    ) -> list[dict]:
        """Extract relationships between a paper and existing papers."""
        if not self._available:
            logger.debug("LLM unavailable, skipping relationship extraction")
            return []

        try:
            import litellm
            import json

            # Build context
            existing_context = ""
            for i, p in enumerate(existing_papers[:30], 1):
                existing_context += f"""
{i}. {p.get('title', 'Unknown')} (ID: {p.get('id', '')})
Authors: {', '.join(p.get('authors', [])[:3])}
Category: {p.get('primary_category', '')}
---
"""

            prompt = f"""Analyze relationships between this new paper and existing papers in our database.

NEW PAPER:
Title: {paper.get('title', '')}
Authors: {', '.join(paper.get('authors', []))}
Abstract: {paper.get('abstract', '')[:500]}
Category: {paper.get('primary_category', '')}

EXISTING PAPERS:
{existing_context}

Identify relationships such as:
- Shared authors (author)
- Topic overlap (topic)
- Potential citations (citation)
- Similar methodology (similar)

Respond in JSON format:
{{
    "relationships": [
        {{
            "paper_index": 1,
            "type": "topic",
            "weight": 0.8,
            "reason": "Both papers discuss..."
        }}
    ]
}}

Only include meaningful relationships with weight >= 0.5."""

            response = await litellm.acompletion(
                model=Config.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )
            
            if response and response.choices:
                result_text = response.choices[0].message.content
                
                try:
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text)
                    relationships = []
                    
                    for rel in result.get("relationships", []):
                        idx = rel.get("paper_index", 1) - 1
                        if 0 <= idx < len(existing_papers):
                            relationships.append({
                                "source_id": paper.get("id", ""),
                                "target_id": existing_papers[idx].get("id", ""),
                                "relationship_type": rel.get("type", "similar"),
                                "weight": rel.get("weight", 0.5),
                                "metadata": {"reason": rel.get("reason", "")},
                            })
                    
                    logger.info(f"Extracted {len(relationships)} relationships")
                    return relationships
                except json.JSONDecodeError:
                    logger.warning("Failed to parse relationships JSON")
                    return []
            
            return []
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return []


# Singleton instance
def get_llm_service() -> LLMService:
    """Get the LLM service instance."""
    return LLMService()
