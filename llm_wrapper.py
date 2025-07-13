import requests
import json
import os
from typing import Optional, List, Dict, Any
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import LLMResult, Generation
import logging

logger = logging.getLogger(__name__)

class E2ENetworksLLM(LLM):
    """
    Custom LangChain LLM wrapper for E2E Networks hosted LLM endpoints.
    
    This wrapper allows you to use E2E Networks LLM deployments with LangChain
    by providing a standardized interface for making API calls.
    """
    
    endpoint_url: str
    api_key: str
    model_name: str = "e2e-llm"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    timeout: int = 30
    
    def __init__(l
        self,
        endpoint_url: str = None,
        api_key: str = None,
        model_name: str = "e2e-llm",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        timeout: int = 30,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.endpoint_url = endpoint_url or os.getenv("E2E_ENDPOINT_URL")
        self.api_key = api_key or os.getenv("E2E_API_KEY")
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.timeout = timeout
        
        if not self.endpoint_url:
            raise ValueError("E2E endpoint URL must be provided via parameter or E2E_ENDPOINT_URL environment variable")
        if not self.api_key:
            raise ValueError("API key must be provided via parameter or E2E_API_KEY environment variable")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of LLM type."""
        return "e2e_networks_llm"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the E2E Networks LLM endpoint with the given prompt.
        
        Args:
            prompt: The input text prompt
            stop: List of stop sequences
            run_manager: Callback manager for LLM run
            **kwargs: Additional keyword arguments
            
        Returns:
            Generated text response from the LLM
        """
        headers = self._get_headers()
        payload = self._build_payload(prompt, stop, **kwargs)
        
        try:
            logger.info(f"Making request to E2E LLM endpoint: {self.endpoint_url}")
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract text from different possible response formats
            generated_text = self._extract_generated_text(result)
            
            logger.info("Successfully received response from E2E LLM")
            return generated_text
            
        except requests.exceptions.Timeout:
            error_msg = f"Request to E2E LLM timed out after {self.timeout} seconds"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    def _build_payload(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Build the request payload."""
        payload = {
            "prompt": prompt,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", self.top_p),
            "model": self.model_name
        }
        
        if stop:
            payload["stop"] = stop
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in payload and key not in ["temperature", "max_tokens", "top_p"]:
                payload[key] = value
                
        return payload
    
    def _extract_generated_text(self, result: Dict[str, Any]) -> str:
        """
        Extract generated text from API response.
        Handles different response formats that E2E endpoints might return.
        """
        # Common response field names to check
        text_fields = [
            "response", "text", "generated_text", "output", 
            "completion", "answer", "result"
        ]
        
        # Check for choices array (OpenAI-style format)
        if "choices" in result and isinstance(result["choices"], list) and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "text" in choice:
                return choice["text"]
            elif "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        
        # Check for direct text fields
        for field in text_fields:
            if field in result:
                return str(result[field])
        
        # If no recognized format, return the entire result as string
        logger.warning(f"Unrecognized response format: {result}")
        return str(result)
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of input prompts
            stop: List of stop sequences
            run_manager: Callback manager for LLM run
            **kwargs: Additional keyword arguments
            
        Returns:
            LLMResult containing generated responses
        """
        generations = []
        
        for prompt in prompts:
            response = self._call(prompt, stop, run_manager, **kwargs)
            generations.append([Generation(text=response)])
        
        return LLMResult(generations=generations)

# Convenience function to create E2E LLM instance
def create_e2e_llm(
    endpoint_url: str = None,
    api_key: str = None,
    **kwargs
) -> E2ENetworksLLM:
    """
    Create an E2E Networks LLM instance with the given parameters.
    
    Args:
        endpoint_url: E2E Networks LLM endpoint URL
        api_key: API key for authentication
        **kwargs: Additional parameters for the LLM
        
    Returns:
        Configured E2ENetworksLLM instance
    """
    return E2ENetworksLLM(
        endpoint_url=endpoint_url,
        api_key=api_key,
        **kwargs
    )