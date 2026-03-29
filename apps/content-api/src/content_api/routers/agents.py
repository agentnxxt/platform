from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from content_api.agents.llm import llm
from content_api.config import settings
from content_api.memory import brand as brand_memory

router = APIRouter(prefix="/agent", tags=["agents"])


class ContentRequest(BaseModel):
    topic: str
    content_type: str = "blog_post"
    brand_name: Optional[str] = None
    tone: str = "professional"
    length: str = "medium"
    target_audience: Optional[str] = None
    model: Optional[str] = None


class ResearchRequest(BaseModel):
    topic: str
    depth: str = "standard"
    model: Optional[str] = None


class RepurposeRequest(BaseModel):
    content: str
    target_formats: list[str] = ["twitter", "linkedin", "instagram"]
    brand_name: Optional[str] = None
    model: Optional[str] = None


_LENGTH = {"short": "200-300 words", "medium": "500-800 words", "long": "1200-2000 words"}

_TYPE_PROMPT = {
    "blog_post": "Write a {length} blog post",
    "social_post": "Write a social media post (280 chars for Twitter, longer for LinkedIn)",
    "email": "Write a marketing email ({length})",
    "ad_copy": "Write compelling ad copy (headline + body + CTA)",
}

_REPURPOSE_PROMPT = {
    "twitter": "Rewrite as a Twitter/X post (max 280 chars). Include relevant hashtags.",
    "linkedin": "Rewrite as a LinkedIn post (300-500 words). Professional, insightful. Include a hook.",
    "instagram": "Rewrite as an Instagram caption. Engaging, include emojis and hashtags.",
    "email_subject": "Write 3 email subject line variations. Short, compelling, high open-rate.",
    "facebook": "Rewrite as a Facebook post. Conversational, shareable.",
    "newsletter": "Rewrite as a newsletter section (200-300 words). Informative, scannable.",
    "ad_headline": "Write 5 ad headline variations. Short, punchy, action-oriented.",
}


@router.post("/research")
async def research(req: ResearchRequest):
    model = req.model or settings.default_model
    result = await llm.generate(
        prompt=f"""Research the topic: "{req.topic}"

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
    return {"topic": req.topic, "research": result, "model": model}


@router.post("/write")
async def write(req: ContentRequest):
    model = req.model or settings.default_model
    brand_context = ""
    if req.brand_name:
        memories = await brand_memory.search(req.brand_name, req.topic)
        if memories:
            brand_context = "\n\nBrand Guidelines & Context:\n" + "\n".join(memories)

    length_str = _LENGTH.get(req.length, "500-800 words")
    type_str = _TYPE_PROMPT.get(req.content_type, "Write content").format(length=length_str)

    result = await llm.generate(
        prompt=f"""{type_str} about: "{req.topic}"

Tone: {req.tone}
Target audience: {req.target_audience or "general"}
{brand_context}

Make it engaging, SEO-friendly, and actionable.""",
        model=model,
        system=f"You are an expert content writer. Write in a {req.tone} tone.",
    )
    return {"topic": req.topic, "content_type": req.content_type, "content": result, "model": model}


@router.post("/repurpose")
async def repurpose(req: RepurposeRequest):
    model = req.model or settings.fast_model
    results: dict[str, str] = {}
    for fmt in req.target_formats:
        instruction = _REPURPOSE_PROMPT.get(fmt, f"Rewrite for {fmt}")
        results[fmt] = await llm.generate(
            prompt=f"{instruction}\n\nOriginal content:\n{req.content[:3000]}",
            model=model,
            system="You are a content repurposing expert.",
        )
    return {"formats": results}
