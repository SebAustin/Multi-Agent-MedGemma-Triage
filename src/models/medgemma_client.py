"""
MedGemma model client for loading and interacting with the model.
"""
from typing import Optional, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from huggingface_hub import login
from tenacity import retry, stop_after_attempt, wait_exponential
from config import ModelConfig
from src.utils.logger import logger


class MedGemmaClient:
    """Client for interacting with MedGemma models."""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        token: Optional[str] = None,
        device: Optional[str] = None
    ):
        """
        Initialize the MedGemma client.
        
        Args:
            model_name: Name of the MedGemma model to load
            token: Hugging Face API token
            device: Device to run inference on ('cuda' or 'cpu')
        """
        self.model_name = model_name or ModelConfig.MODEL_NAME
        self.device = device or ModelConfig.get_device()
        self.token = token or ModelConfig.HF_TOKEN
        
        self.tokenizer = None
        self.model = None
        self._is_loaded = False
        
        logger.info(f"Initializing MedGemmaClient with model: {self.model_name}")
        logger.info(f"Device: {self.device}")
    
    def load_model(self) -> None:
        """Load the MedGemma model and tokenizer."""
        if self._is_loaded:
            logger.info("Model already loaded")
            return
        
        try:
            # Login to Hugging Face if token provided
            if self.token:
                logger.info("Logging in to Hugging Face...")
                login(token=self.token)
            
            logger.info(f"Loading tokenizer from {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=ModelConfig.MODEL_CACHE_DIR,
                token=self.token
            )
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info(f"Loading model from {self.model_name}...")
            model_kwargs = {
                "cache_dir": ModelConfig.MODEL_CACHE_DIR,
                "token": self.token,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "low_cpu_mem_usage": True
            }
            
            # Add quantization if configured
            if ModelConfig.LOAD_IN_8BIT:
                model_kwargs["load_in_8bit"] = True
            elif ModelConfig.LOAD_IN_4BIT:
                model_kwargs["load_in_4bit"] = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            # Move to device if not quantized
            if not (ModelConfig.LOAD_IN_8BIT or ModelConfig.LOAD_IN_4BIT):
                self.model = self.model.to(self.device)
            
            self.model.eval()
            self._is_loaded = True
            
            logger.success(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the MedGemma model.
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if not self._is_loaded:
            self.load_model()
        
        # Set default parameters
        max_length = max_length or ModelConfig.MAX_LENGTH
        max_new_tokens = max_new_tokens or ModelConfig.MAX_NEW_TOKENS
        temperature = temperature or ModelConfig.TEMPERATURE
        top_p = top_p or ModelConfig.TOP_P
        top_k = top_k or ModelConfig.TOP_K
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length
            ).to(self.device)
            
            # Create generation config
            generation_config = GenerationConfig(
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    generation_config=generation_config
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Remove the input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def chat(
        self,
        messages: list[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Chat-style interaction with the model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        # Format messages into a prompt
        prompt = self._format_chat_prompt(messages)
        return self.generate(prompt, **kwargs)
    
    def _format_chat_prompt(self, messages: list[Dict[str, str]]) -> str:
        """
        Format chat messages into a single prompt.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"<system>\n{content}\n</system>\n")
            elif role == "user":
                prompt_parts.append(f"<user>\n{content}\n</user>\n")
            elif role == "assistant":
                prompt_parts.append(f"<assistant>\n{content}\n</assistant>\n")
        
        prompt_parts.append("<assistant>\n")
        return "".join(prompt_parts)
    
    def get_embedding(self, text: str) -> torch.Tensor:
        """
        Get embeddings for input text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding tensor
        """
        if not self._is_loaded:
            self.load_model()
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # Use the last hidden state's mean as embedding
            embeddings = outputs.hidden_states[-1].mean(dim=1)
        
        return embeddings
    
    def unload_model(self) -> None:
        """Unload the model from memory."""
        if self._is_loaded:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache() if self.device == "cuda" else None
            self._is_loaded = False
            logger.info("Model unloaded")
    
    def __enter__(self):
        """Context manager entry."""
        self.load_model()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.unload_model()


# Singleton instance
_client: Optional[MedGemmaClient] = None


def get_client() -> MedGemmaClient:
    """Get or create the global MedGemma client instance."""
    global _client
    if _client is None:
        _client = MedGemmaClient()
        _client.load_model()
    return _client


__all__ = ["MedGemmaClient", "get_client"]
