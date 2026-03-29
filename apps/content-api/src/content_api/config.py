from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://localllm:11434"
    qdrant_url: str = "http://qdrant:6333"
    litellm_url: str = "http://gateway:4000"
    litellm_master_key: str = "sk-master"
    api_port: int = 8100
    default_model: str = "qwen2.5:7b"
    fast_model: str = "phi3.5:latest"
    embed_model: str = "nomic-embed-text"
    embed_size: int = 768  # nomic-embed-text output dim

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
