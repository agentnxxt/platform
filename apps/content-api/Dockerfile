FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv --quiet

# Copy workspace manifests first for layer caching
COPY pyproject.toml ./
COPY ../../packages/agents/pyproject.toml ./packages/agents/pyproject.toml
COPY ../../packages/agents/src ./packages/agents/src

# Install dependencies
RUN uv pip install --system -e ".[all]" 2>/dev/null || \
    uv pip install --system fastapi uvicorn[standard] httpx pydantic pydantic-settings

COPY src ./src

EXPOSE 8100

CMD ["uvicorn", "content_api.main:app", "--host", "0.0.0.0", "--port", "8100"]
