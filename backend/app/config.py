import json
from typing import List, Union
from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "IntelliRAG API"
    VERSION: str = "0.1.0"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/intellirag"
    VECTOR_DIMENSION: int = 768
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    JWT_SECRET_KEY: str = "changethis-insecure-development-jwt-secret-key-32charsmin"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "storage/uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: Union[List[str], str] = ["pdf", "png", "jpg", "jpeg", "txt", "docx", "csv"]
    
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 50
    MAX_CHUNK_SIZE: int = 1500
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_BATCH_SIZE: int = 32

    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_API_KEY: str = ""
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_OUTPUT_TOKENS: int = 1024
    RAG_MAX_CONTEXT_CHARS: int = 12000
    RAG_DEFAULT_TOP_K: int = 5
    RAG_DEFAULT_SIMILARITY_THRESHOLD: float = 0.25

    NOTIFICATION_EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "notifications@intellirag.ai"
    WEBHOOK_TIMEOUT_SECONDS: int = 5
    NOTIFICATION_MAX_RETRIES: int = 3

    SCHEDULER_ENABLED: bool = True
    REMINDER_CHECK_INTERVAL_SECONDS: int = 60
    NOTIFICATION_RETRY_INTERVAL_SECONDS: int = 300

    @field_validator("CORS_ORIGINS", "ALLOWED_EXTENSIONS", mode="before")
    def assemble_list_fields(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        env = info.data.get("ENVIRONMENT", "development") if info.data else "development"
        if isinstance(env, str) and env.lower() == "production":
            if not v or v == "changethis-insecure-development-jwt-secret-key-32charsmin" or len(v) < 32:
                raise ValueError("In production, JWT_SECRET_KEY must be a secure random secret of at least 32 characters.")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()