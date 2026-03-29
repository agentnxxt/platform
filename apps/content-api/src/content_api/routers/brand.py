from fastapi import APIRouter
from pydantic import BaseModel

from content_api.memory import brand as brand_memory

router = APIRouter(prefix="/brand", tags=["brand"])


class BrandMemoryRequest(BaseModel):
    brand_name: str
    content: str
    content_type: str = "guidelines"  # guidelines | past_content | voice_sample


@router.post("/memory")
async def add_memory(req: BrandMemoryRequest):
    result = await brand_memory.store(
        brand_name=req.brand_name,
        text=req.content,
        metadata={"type": req.content_type, "brand": req.brand_name},
    )
    return result


@router.get("/memory/{brand_name}")
async def search_memory(brand_name: str, q: str = "brand voice"):
    results = await brand_memory.search(brand_name, q)
    return {"brand_name": brand_name, "results": results}
