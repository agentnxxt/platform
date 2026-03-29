"""Temporal workflows — durable content pipeline."""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from orchestrator.activities import ContentInput, repurpose_content, research_topic, write_content


@workflow.defn
class ContentPipeline:
    """Research → Write → Repurpose — durable, resumable pipeline."""

    @workflow.run
    async def run(self, params: dict) -> dict:
        topic: str = params["topic"]
        content_type: str = params.get("content_type", "blog_post")
        tone: str = params.get("tone", "professional")
        length: str = params.get("length", "medium")
        target_audience: str = params.get("target_audience", "general")
        brand_context: str = params.get("brand_context", "")
        model: str = params.get("model", "qwen2.5:7b")
        repurpose_formats: list[str] = params.get("repurpose_formats", [])

        retry = RetryPolicy(maximum_attempts=3, initial_interval=timedelta(seconds=5))

        # Step 1 — Research
        research = await workflow.execute_activity(
            research_topic,
            args=[topic, model],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry,
        )

        # Step 2 — Write
        content = await workflow.execute_activity(
            write_content,
            ContentInput(
                topic=topic,
                content_type=content_type,
                tone=tone,
                length=length,
                target_audience=target_audience,
                brand_context=brand_context,
                model=model,
            ),
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry,
        )

        # Step 3 — Repurpose (optional)
        repurposed: Optional[dict] = None
        if repurpose_formats:
            repurposed = await workflow.execute_activity(
                repurpose_content,
                args=[content, repurpose_formats],
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry,
            )

        return {
            "topic": topic,
            "research": research,
            "content": content,
            "repurposed": repurposed,
        }
