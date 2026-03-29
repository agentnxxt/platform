"""Orchestrator entrypoint — Temporal worker + FastAPI status server."""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temporalio.client import Client
from temporalio.worker import Worker

from orchestrator.activities import repurpose_content, research_topic, write_content
from orchestrator.workflows import ContentPipeline

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "temporal:7233")
TASK_QUEUE = "content-pipeline"

app = FastAPI(title="Content Orchestrator", version="0.1.0")
_temporal_client: Client | None = None

# In-memory pipeline registry (Temporal is the source of truth)
_pipelines: dict[str, dict] = {}


async def get_client() -> Client:
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = await Client.connect(TEMPORAL_HOST)
    return _temporal_client


class PipelineStartRequest(BaseModel):
    workflow_id: str
    topic: str
    content_type: str = "blog_post"
    tone: str = "professional"
    length: str = "medium"
    target_audience: str | None = None
    brand_context: str = ""
    repurpose_formats: list[str] = []
    model: str | None = None


@app.post("/pipeline/start")
async def start_pipeline(req: PipelineStartRequest):
    client = await get_client()
    handle = await client.start_workflow(
        ContentPipeline.run,
        args=[req.model_dump(exclude={"workflow_id"})],
        id=req.workflow_id,
        task_queue=TASK_QUEUE,
    )
    _pipelines[req.workflow_id] = {
        "workflow_id": req.workflow_id,
        "status": "running",
        "created_at": datetime.utcnow().isoformat(),
    }
    return {"workflow_id": req.workflow_id, "status": "started"}


@app.get("/pipeline/{workflow_id}")
async def get_pipeline(workflow_id: str):
    client = await get_client()
    try:
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        status = str(desc.status).lower()
        result = None
        if status == "workflowexecutionstatus.completed":
            result = await handle.result()
        return {"workflow_id": workflow_id, "status": status, "result": result}
    except Exception as e:
        raise HTTPException(404, str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "content-orchestrator"}


async def run_worker(client: Client):
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ContentPipeline],
        activities=[research_topic, write_content, repurpose_content],
    )
    await worker.run()


async def main():
    client = await Client.connect(TEMPORAL_HOST)
    # Run worker and API server concurrently
    await asyncio.gather(
        run_worker(client),
        asyncio.to_thread(
            uvicorn.run, app, host="0.0.0.0", port=int(os.getenv("ORCHESTRATOR_PORT", "8200"))
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
