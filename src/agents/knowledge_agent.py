"""
Medical Knowledge Agent - Provides medical context and guidelines.
"""
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.models.prompt_templates import PromptTemplates
from src.utils.logger import logger


class MedicalKnowledgeAgent(BaseAgent):
    """Agent responsible for providing medical knowledge and context."""
    
    def __init__(self):
        super().__init__(name="Medical Knowledge Agent")
        self._knowledge_cache: Dict[str, str] = {}
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide medical knowledge based on query.
        
        Args:
            input_data: Dict with 'query' and optional 'context'
            
        Returns:
            Dict with 'knowledge_response' and 'confidence'
        """
        query = input_data.get("query", "")
        context = input_data.get("context", "")
        
        logger.info(f"{self.name} processing query: {query[:50]}...")
        
        # Check cache
        cache_key = f"{query}:{context}"
        if cache_key in self._knowledge_cache:
            logger.debug(f"{self.name} using cached response")
            return {
                "knowledge_response": self._knowledge_cache[cache_key],
                "confidence": "high",
                "cached": True
            }
        
        # Generate knowledge response
        prompt = PromptTemplates.format_medical_knowledge(query, context)
        response = self._generate(prompt, temperature=0.4, max_length=1024)
        
        # Cache the response
        self._knowledge_cache[cache_key] = response
        
        logger.info(f"{self.name} provided knowledge response")
        
        return {
            "knowledge_response": response,
            "confidence": "medium",
            "cached": False
        }
    
    def get_triage_protocol(self, symptoms: str) -> str:
        """Get triage protocol for specific symptoms."""
        query = f"What is the appropriate triage protocol for a patient with: {symptoms}"
        result = self.process({"query": query})
        return result["knowledge_response"]
    
    def get_clinical_guideline(self, condition: str) -> str:
        """Get clinical guidelines for a condition."""
        query = f"What are the clinical guidelines for assessing and managing: {condition}"
        result = self.process({"query": query})
        return result["knowledge_response"]
    
    def clear_cache(self) -> None:
        """Clear the knowledge cache."""
        self._knowledge_cache.clear()
        logger.info(f"{self.name} cache cleared")


__all__ = ["MedicalKnowledgeAgent"]
