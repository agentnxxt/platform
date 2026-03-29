"""Temporal workflow triggers — kick off async content pipelines."""
from __future__ import annotations

import os
import uuid
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/workflow", tags=["workflows"])

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "temporal:7233")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://content-orchestrator:8200")


class PipelineRequest(BaseModel):
    topic: str
    content_type: str = "blog_post"
    brand_name: Optional[str] = None
    tone: str = "professional"
    length: str = "medium"
    target_audience: Optional[str] = None
    repurpose_formats: list[str] = []
    model: Optional[str] = None


@router.post("/pipeline")
async def start_pipeline(req: PipelineRequest):
    """Start a full research → write → repurpose pipeline via the orchestrator."""
    workflow_id = f"content-{uuid.uuid4().hex[:8]}"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(
                f"{ORCHESTRATOR_URL}/pipeline/start",
                json={"workflow_id": workflow_id, **req.model_dump()},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(503, "Orchestrator unavailable — run content-orchestrator service")


@router.get("/pipeline/{workflow_id}")
async def get_pipeline(workflow_id: str):
    """Poll pipeline status from the orchestrator."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{ORCHESTRATOR_URL}/pipeline/{workflow_id}")
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(503, "Orchestrator unavailable")
