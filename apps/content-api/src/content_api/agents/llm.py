"""Shared LLM client instance for content-api."""
from agents import LLMClient
from content_api.config import settings

llm = LLMClient(
    ollama_url=settings.ollama_url,
    litellm_url=settings.litellm_url,
    litellm_key=settings.litellm_master_key,
)
