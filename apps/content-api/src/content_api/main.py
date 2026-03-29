from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from content_api.config import settings
from content_api.routers import agents, brand, workflows

app = FastAPI(title="AutonomyX Content API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(brand.router)
app.include_router(workflows.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "content-api"}


@app.get("/models")
async def list_models():
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(f"{settings.ollama_url}/api/tags")
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
    return {"models": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)
