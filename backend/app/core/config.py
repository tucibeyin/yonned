from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Yonned API"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "yonned-bare-metal-production-secret-key-64-bytes"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Database - PostgreSQL 17 Async (Node102 local unix/port)
    DATABASE_URL: str = "postgresql+asyncpg://yonned:yonned_secure_pwd_2026@127.0.0.1:5432/yonned_db"
    DB_ECHO: bool = False
    
    # Cache & PubSub - Redis 7 (Node102)
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    
    # Storage - MinIO Object Storage (Node104 over WireGuard Mesh)
    MINIO_ENDPOINT: str = "10.10.0.4:9000"
    MINIO_ACCESS_KEY: str = "yonned_prod"
    MINIO_SECRET_KEY: str = "yonned_minio_secret"
    MINIO_BUCKET_NAME: str = "yonned-prod-media"
    MINIO_SECURE: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
