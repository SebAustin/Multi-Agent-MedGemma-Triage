"""
Base agent class for all triage agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.medgemma_client import MedGemmaClient, get_client
from src.utils.logger import logger


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        name: str,
        client: Optional[MedGemmaClient] = None
    ):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
            client: MedGemma client instance (uses global if None)
        """
        self.name = name
        self.client = client or get_client()
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return results.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Processing results
        """
        pass
    
    def _generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response using MedGemma.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            response = self.client.generate(prompt, **kwargs)
            logger.debug(f"{self.name} generated response: {response[:100]}...")
            return response
        except Exception as e:
            logger.error(f"{self.name} generation failed: {e}")
            raise
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


__all__ = ["BaseAgent"]
