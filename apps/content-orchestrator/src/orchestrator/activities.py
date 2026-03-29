"""Temporal activities — each is a single agent step."""
from __future__ import annotations

import os
from dataclasses import dataclass

from temporalio import activity

from agents import LLMClient

_llm = LLMClient(
    ollama_url=os.getenv("OLLAMA_URL", "http://localllm:11434"),
    litellm_url=os.getenv("LITELLM_URL", "http://gateway:4000"),
    litellm_key=os.getenv("LITELLM_MASTER_KEY", "sk-master"),
)

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5:7b")
FAST_MODEL = os.getenv("FAST_MODEL", "phi3.5:latest")


@dataclass
class ContentInput:
    topic: str
    content_type: str = "blog_post"
    tone: str = "professional"
    length: str = "medium"
    target_audience: str = "general"
    brand_context: str = ""
    model: str = DEFAULT_MODEL


@activity.defn
async def research_topic(topic: str, model: str = DEFAULT_MODEL) -> str:
    activity.logger.info("Researching topic: %s", topic)
    return await _llm.generate(
        prompt=f"""Research the topic: "{topic}"

Provide:
1. Key trends and developments
2. Target audience insights
3. Content angles (3-5 unique angles)
4. Keywords and phrases to use
5. Competitor content gaps

Format as structured JSON.""",
        model=model,
        system="You are a content research expert. Return structured JSON.",
    )


@activity.defn
async def write_content(inp: ContentInput) -> str:
    activity.logger.info("Writing %s about: %s", inp.content_type, inp.topic)
    _length = {"short": "200-300 words", "medium": "500-800 words", "long": "1200-2000 words"}
    length_str = _length.get(inp.length, "500-800 words")

    context = f"\n\nBrand Guidelines:\n{inp.brand_context}" if inp.brand_context else ""
    return await _llm.generate(
        prompt=f"""Write a {length_str} {inp.content_type.replace("_", " ")} about: "{inp.topic}"

Tone: {inp.tone}
Target audience: {inp.target_audience}
{context}

Make it engaging, SEO-friendly, and actionable.""",
        model=inp.model,
        system=f"You are an expert content writer. Write in a {inp.tone} tone.",
    )


@activity.defn
async def repurpose_content(content: str, formats: list[str]) -> dict[str, str]:
    activity.logger.info("Repurposing into %d formats", len(formats))
    _prompts = {
        "twitter": "Rewrite as a Twitter/X post (max 280 chars). Include relevant hashtags.",
        "linkedin": "Rewrite as a LinkedIn post (300-500 words). Professional, insightful. Include a hook.",
        "instagram": "Rewrite as an Instagram caption. Engaging, include emojis and hashtags.",
        "email_subject": "Write 3 email subject line variations. Short, compelling, high open-rate.",
        "facebook": "Rewrite as a Facebook post. Conversational, shareable.",
        "newsletter": "Rewrite as a newsletter section (200-300 words). Informative, scannable.",
        "ad_headline": "Write 5 ad headline variations. Short, punchy, action-oriented.",
    }
    results: dict[str, str] = {}
    for fmt in formats:
        instruction = _prompts.get(fmt, f"Rewrite for {fmt}")
        results[fmt] = await _llm.generate(
            prompt=f"{instruction}\n\nOriginal:\n{content[:3000]}",
            model=FAST_MODEL,
            system="You are a content repurposing expert.",
        )
    return results
