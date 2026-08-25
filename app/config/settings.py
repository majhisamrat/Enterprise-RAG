import os
from pathlib import Path
from typing import Optional
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = Field(default="Enterprise RAG Pipeline", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=True, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Security & Auth
    SECRET_KEY: str = Field(default="super-secret-enterprise-rag-key-change-in-production-2026!", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    OTP_EXPIRE_MINUTES: int = Field(default=5, env="OTP_EXPIRE_MINUTES")

    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = Field(default="", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", env="GOOGLE_CLIENT_SECRET")

    # SMTP / Gmail Email Service
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field(default="noreply@enterprise-rag.com", env="SMTP_FROM_EMAIL")

    # Storage Settings
    UPLOAD_DIR: str = Field(default="data/uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=52428800, env="MAX_FILE_SIZE")  # 50 MB
    STORAGE_BACKEND: str = Field(default="local", env="STORAGE_BACKEND")  # 'local', 's3', or 'minio'
    S3_BUCKET_NAME: Optional[str] = Field(default="enterprise-rag-storage", env="S3_BUCKET_NAME")
    S3_REGION: Optional[str] = Field(default="us-east-1", env="S3_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    MINIO_ENDPOINT: Optional[str] = Field(default="http://localhost:9000", env="MINIO_ENDPOINT")
    
    # Structured Data Store (DuckDB)
    DUCKDB_PATH: str = Field(default="data/duckdb", env="DUCKDB_PATH")
    STRUCTURED_MAX_SIZE_MB: int = Field(default=100, env="STRUCTURED_MAX_SIZE_MB")  # Max CSV/XLSX size for structured queries
    STRUCTURED_MAX_ROWS: int = Field(default=1_000_000, env="STRUCTURED_MAX_ROWS")  # Max row count

    # Relational Database (PostgreSQL)
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@postgres:5432/enterprise_rag", env="DATABASE_URL")
    SYNC_DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@postgres:5432/enterprise_rag", env="SYNC_DATABASE_URL")

    # Redis Cache & Broker
    REDIS_URL: str = Field(default="redis://redis:6379/0", env="REDIS_URL")

    # Vector Storage (Chroma DB - Embedded, replaced Qdrant)
    # Note: Chroma DB stores vectors in .chroma/vectors.pkl with KB-based collection isolation
    # Vectors persist across FastAPI and Celery processes via disk storage
    QDRANT_COLLECTION: str = Field(default="enterprise_documents", env="QDRANT_COLLECTION")  # Base collection name for Chroma
    EMBEDDING_DIMENSION: int = Field(default=384, env="EMBEDDING_DIMENSION")
    SEARCH_CONNECT_TIMEOUT_SECONDS: float = Field(default=30.0, env="SEARCH_CONNECT_TIMEOUT_SECONDS")
    
    # Legacy Qdrant config (kept for backward compatibility, not used)
    QDRANT_URL: str = Field(default="http://qdrant:6333", env="QDRANT_URL")
    QDRANT_HOST: str = Field(default="qdrant", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")

    # Search Engine (Elasticsearch)
    ELASTICSEARCH_URL: str = Field(default="http://elasticsearch:9200", env="ELASTICSEARCH_URL")
    ELASTIC_INDEX: str = Field(default="enterprise_documents", env="ELASTIC_INDEX")

    # Embeddings & Reranker Models
    MODEL_NAME: str = Field(default="BAAI/bge-small-en-v1.5", env="MODEL_NAME")
    RERANKER_MODEL_NAME: str = Field(default="BAAI/bge-reranker-large", env="RERANKER_MODEL_NAME")
    ENABLE_RERANKER: bool = Field(default=False, env="ENABLE_RERANKER")
    RERANKER_MAX_CANDIDATES: int = Field(default=6, env="RERANKER_MAX_CANDIDATES")
    MAX_RETRIEVAL_RESULTS: int = Field(default=50, env="MAX_RETRIEVAL_RESULTS")

    # LLM Provider (Groq / Gemini)
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="openai/gpt-oss-20b", env="GROQ_MODEL")
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash", env="GEMINI_MODEL")
    LLM_PROVIDER: str = Field(default="groq", env="LLM_PROVIDER")
    TEMPERATURE: float = Field(default=0.2, env="TEMPERATURE")
    TOP_P: float = Field(default=0.95, env="TOP_P")
    MAX_OUTPUT_TOKENS: int = Field(default=2048, env="MAX_OUTPUT_TOKENS")
    MAX_RETRIES: int = Field(default=3, env="MAX_RETRIES")
    
    # Code Generation LLM (for structured queries/SQL generation)
    LLM_CODEGEN_MODEL_PROVIDER: Optional[str] = Field(default=None, env="LLM_CODEGEN_MODEL_PROVIDER")
    LLM_CODEGEN_MODEL: Optional[str] = Field(default=None, env="LLM_CODEGEN_MODEL")
    LLM_CODEGEN_TEMPERATURE: float = Field(default=0.1, env="LLM_CODEGEN_TEMPERATURE")

    # Knowledge Base Limits
    MAX_KB_PER_USER: int = Field(default=3, env="MAX_KB_PER_USER")  # Max 3 KBs per user
    MAX_UPLOADS_PER_KB: int = Field(default=5, env="MAX_UPLOADS_PER_KB")  # Max 5 files per KB

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
