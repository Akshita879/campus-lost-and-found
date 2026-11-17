import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Campus Lost and Found Portal"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:12345@127.0.0.1:3306/campus_lost_and_found"

    # Security
    JWT_SECRET_KEY: str = "default_secret_key_change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Bootstrap campus admin (created on startup if missing)
    ADMIN_EMAIL: str = "admin@campus.edu"
    ADMIN_PASSWORD: str = "AdminPass123"
    ADMIN_NAME: str = "Campus Admin"

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    ALLOWED_IMAGE_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Matching Engine Parameters
    MATCH_MIN_SCORE_THRESHOLD: float = 25.0
    MATCH_MAX_RESULTS: int = 10
    WEIGHT_CATEGORY: float = 30.0
    WEIGHT_ITEM_NAME: float = 30.0
    WEIGHT_DESCRIPTION: float = 20.0
    WEIGHT_LOCATION: float = 10.0
    WEIGHT_DATE: float = 10.0

    @property
    def upload_path(self) -> Path:
        # Vercel serverless only allows writes under /tmp
        if os.getenv("VERCEL") or self.ENVIRONMENT.lower() in {"production", "prod"}:
            path = Path("/tmp") / self.UPLOAD_DIR
        else:
            path = BASE_DIR / self.UPLOAD_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = SettingsConfigDict(
        env_file=(BASE_DIR / ".env", Path(".env")),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
