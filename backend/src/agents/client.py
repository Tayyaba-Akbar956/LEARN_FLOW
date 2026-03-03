"""OpenAI Agent SDK client configuration for Groq API."""
import os
from typing import Optional
from openai import OpenAI


class AgentClient:
    """
    OpenAI Agent SDK client configured for Groq API.

    Provides a configured client for all AI tutor agents to use,
    ensuring consistent API usage and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "llama-3.1-70b-versatile"
    ):
        """
        Initialize AgentClient with Groq API configuration.

        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            base_url: Groq API base URL (defaults to https://api.groq.com/openai/v1)
            model: Default model to use for completions
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or "https://api.groq.com/openai/v1"
        self.model = model

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        # Initialize OpenAI client with Groq configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def get_client(self) -> OpenAI:
        """
        Get the configured OpenAI client.

        Returns:
            Configured OpenAI client instance
        """
        return self.client

    async def create_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ):
        """
        Create a chat completion using Groq API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API

        Returns:
            Completion response from Groq API
        """
        return self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )

    async def create_streaming_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Create a streaming chat completion using Groq API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance model)
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API

        Yields:
            Completion chunks from Groq API
        """
        stream = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        for chunk in stream:
            yield chunk


# Global client instance
_client_instance: Optional[AgentClient] = None


def get_agent_client() -> AgentClient:
    """
    Get or create the global AgentClient instance.

    Returns:
        Configured AgentClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = AgentClient()
    return _client_instance


def reset_agent_client() -> None:
    """Reset the global AgentClient instance (useful for testing)."""
    global _client_instance
    _client_instance = None
