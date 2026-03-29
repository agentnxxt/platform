"""Qdrant-backed brand memory for RAG."""
from __future__ import annotations

import uuid

import httpx

from content_api.config import settings


async def store(brand_name: str, text: str, metadata: dict) -> dict:
    collection = _collection(brand_name)
    async with httpx.AsyncClient(timeout=30) as client:
        # Ensure collection exists
        await client.put(
            f"{settings.qdrant_url}/collections/{collection}",
            json={"vectors": {"size": settings.embed_size, "distance": "Cosine"}},
        )
        embedding = await _embed(client, text)
        point_id = str(uuid.uuid4())
        await client.put(
            f"{settings.qdrant_url}/collections/{collection}/points",
            json={"points": [{"id": point_id, "vector": embedding, "payload": {"text": text, **metadata}}]},
        )
    return {"status": "stored", "id": point_id}


async def search(brand_name: str, query: str, limit: int = 3) -> list[str]:
    collection = _collection(brand_name)
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            embedding = await _embed(client, query)
            resp = await client.post(
                f"{settings.qdrant_url}/collections/{collection}/points/search",
                json={"vector": embedding, "limit": limit, "with_payload": True},
            )
            if resp.status_code == 200:
                return [hit["payload"]["text"] for hit in resp.json().get("result", [])]
        except Exception:
            pass
    return []


async def _embed(client: httpx.AsyncClient, text: str) -> list[float]:
    resp = await client.post(
        f"{settings.ollama_url}/api/embed",
        json={"model": settings.embed_model, "input": text[:2000]},
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


def _collection(brand_name: str) -> str:
    return brand_name.lower().replace(" ", "_")
