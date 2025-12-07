"""
LLM Client Interface for AI Assistant

Supports multiple providers: OpenAI, Anthropic, and local models.
"""

import os
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import httpx
import json


class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer from LLM"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI GPT client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                raise Exception(f"OpenAI API error: {str(e)}")


class AnthropicClient(LLMClient):
    """Anthropic Claude client"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    async def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using Anthropic API"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
            except httpx.HTTPError as e:
                raise Exception(f"Anthropic API error: {str(e)}")


class LocalLLMClient(LLMClient):
    """Local LLM client (e.g., Ollama, LM Studio)"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
    
    async def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using local LLM"""
        endpoint = f"{self.base_url}/api/generate"
        
        # Combine system and user prompts for local models
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except httpx.HTTPError as e:
                raise Exception(f"Local LLM error: {str(e)}")


class MockLLMClient(LLMClient):
    """Mock client for testing without API keys"""
    
    async def generate_answer(self, system_prompt: str, user_prompt: str) -> str:
        """Generate mock answer"""
        return (
            "**Mock AI Assistant Response**\n\n"
            "This is a mock response. To use the real AI assistant, "
            "please configure LLM_PROVIDER and LLM_API_KEY in your environment.\n\n"
            "Based on the provided data, here's what I can tell you:\n"
            "- The query was processed successfully\n"
            "- Data was retrieved from the database\n"
            "- A real LLM would provide detailed insights here\n\n"
            "Configure your LLM provider to get real answers."
        )


def create_llm_client(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> LLMClient:
    """
    Factory function to create appropriate LLM client
    
    Args:
        provider: "openai", "anthropic", "local", or "mock"
        api_key: API key for cloud providers
        model: Model name (optional, uses defaults)
    
    Returns:
        Configured LLMClient instance
    """
    # Get from environment if not provided
    provider = provider or os.getenv("LLM_PROVIDER", "mock")
    api_key = api_key or os.getenv("LLM_API_KEY")
    model = model or os.getenv("LLM_MODEL")
    
    provider = provider.lower()
    
    if provider == "openai":
        if not api_key:
            raise ValueError("OpenAI requires LLM_API_KEY")
        return OpenAIClient(api_key, model or "gpt-4o")
    
    elif provider == "anthropic":
        if not api_key:
            raise ValueError("Anthropic requires LLM_API_KEY")
        return AnthropicClient(api_key, model or "claude-3-5-sonnet-20241022")
    
    elif provider == "local":
        base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        return LocalLLMClient(base_url, model or "llama2")
    
    elif provider == "mock":
        return MockLLMClient()
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported: openai, anthropic, local, mock"
        )


# Convenience function for quick testing
async def test_llm_connection() -> Dict[str, Any]:
    """Test LLM configuration"""
    try:
        client = create_llm_client()
        provider = os.getenv("LLM_PROVIDER", "mock")
        
        answer = await client.generate_answer(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say 'Hello, I'm working!' if you can respond."
        )
        
        return {
            "status": "success",
            "provider": provider,
            "model": os.getenv("LLM_MODEL", "default"),
            "response": answer[:100] + "..." if len(answer) > 100 else answer
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "provider": os.getenv("LLM_PROVIDER", "not set")
        }
