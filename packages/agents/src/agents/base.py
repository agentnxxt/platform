from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel


class LLMClient:
    """Thin async wrapper around Ollama / LiteLLM for agent use."""

    def __init__(
        self,
        ollama_url: str | None = None,
        litellm_url: str | None = None,
        litellm_key: str | None = None,
    ) -> None:
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localllm:11434")
        self.litellm_url = litellm_url or os.getenv("LITELLM_URL", "http://gateway:4000")
        self.litellm_key = litellm_key or os.getenv("LITELLM_MASTER_KEY", "sk-master")

    async def generate(
        self,
        prompt: str,
        model: str = "qwen2.5:7b",
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text, trying LiteLLM first then falling back to Ollama."""
        async with httpx.AsyncClient(timeout=120) as client:
            # Try LiteLLM gateway first
            try:
                messages: list[dict[str, str]] = []
                if system:
                    messages.append({"role": "system", "content": system})
                messages.append({"role": "user", "content": prompt})

                resp = await client.post(
                    f"{self.litellm_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.litellm_key}"},
                    json={
                        "model": f"ollama/{model}",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass

            # Direct Ollama fallback
            resp = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def embed(self, text: str, model: str = "nomic-embed-text") -> list[float]:
        """Generate an embedding vector via Ollama."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.ollama_url}/api/embed",
                json={"model": model, "input": text[:2000]},
            )
            resp.raise_for_status()
            return resp.json()["embeddings"][0]


class AgentResult(BaseModel):
    success: bool
    output: Any = None
    error: str | None = None


class BaseAgent(ABC):
    """Base class for all AutonomyX content agents."""

    name: str = "base"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    @abstractmethod
    async def run(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's primary task."""
        ...
