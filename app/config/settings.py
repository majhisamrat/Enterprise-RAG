import os
from pathlib import Path
from typing import Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Enterprise RAG Pipeline"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Security & Auth
    SECRET_KEY: str = "super-secret-enterprise-rag-key-change-in-production-2026!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 5

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")

    # SMTP / Gmail Email Service
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@enterprise-rag.com"

    # Storage Settings
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE: int = 52428800  # 50 MB
    STORAGE_BACKEND: str = "local"  # 'local', 's3', or 'minio'
    S3_BUCKET_NAME: Optional[str] = "enterprise-rag-storage"
    S3_REGION: Optional[str] = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    MINIO_ENDPOINT: Optional[str] = "http://localhost:9000"

    # Relational Database (PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/enterprise_rag"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/enterprise_rag"

    # Redis Cache & Broker
    REDIS_URL: str = "redis://redis:6379/0"

    # Vector Storage (Qdrant)
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "enterprise_documents"
    EMBEDDING_DIMENSION: int = 384
    SEARCH_CONNECT_TIMEOUT_SECONDS: float = 30

    # Search Engine (Elasticsearch)
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    ELASTIC_INDEX: str = "enterprise_documents"

    # Embeddings & Reranker Models
    MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    RERANKER_MODEL_NAME: str = "BAAI/bge-reranker-large"
    ENABLE_RERANKER: bool = False
    RERANKER_MAX_CANDIDATES: int = 6
    MAX_RETRIEVAL_RESULTS: int = 5

    # LLM Provider (Groq / Gemini)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "qwen/qwen3.6-27b"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    LLM_PROVIDER: str = "groq"
    TEMPERATURE: float = 0.2
    TOP_P: float = 0.95
    MAX_OUTPUT_TOKENS: int = 2048
    MAX_RETRIES: int = 3

    # Mem0 Long-Term Memory (Optional)
    MEM0_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> object:
        """Accept common deployment labels used by existing environment files."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev"}:
                return True
        return value


settings = Settings()
