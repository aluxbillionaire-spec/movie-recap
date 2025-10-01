"""
Application Configuration

Centralized configuration management using Pydantic Settings.
Supports environment variables and configuration files.
"""

from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Basic app settings
    DEBUG: bool = False
    TESTING: bool = False
    APP_NAME: str = "Movie Recap Pipeline"
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/movierecap"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_ECHO: bool = False
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 20
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_MIN_LENGTH: int = 8
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 12 * 1024 * 1024 * 1024  # 12GB
    MAX_VIDEO_DURATION: int = 10 * 3600  # 10 hours in seconds
    MAX_SCRIPT_SIZE: int = 1024 * 1024 * 1024  # 1GB
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"]
    ALLOWED_SCRIPT_EXTENSIONS: List[str] = [".txt", ".doc", ".docx", ".pdf"]
    
    # Google Drive settings
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = "credentials/google-drive-credentials.json"
    GOOGLE_DRIVE_ROOT_FOLDER: str = "movie-recap-pipeline"
    
    # Google Colab settings
    COLAB_WEBHOOK_URL: str = "https://your-colab-webhook.com/webhook"
    COLAB_WEBHOOK_SECRET: str = "colab-webhook-secret"
    
    # Processing limits
    MAX_OUTPUT_DURATION: int = 5 * 3600  # 5 hours in seconds
    SCENE_DETECTION_THRESHOLD: float = 0.4
    ALIGNMENT_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    
    # Monitoring settings
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8001
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: Optional[str] = None
    
    # External service URLs
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook"
    N8N_API_URL: str = "http://localhost:5678/api/v1"
    N8N_API_KEY: Optional[str] = None
    
    # Email settings (for notifications)
    EMAIL_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@movierecap.com"
    
    # S3/Cloud storage (backup)
    S3_BUCKET: Optional[str] = None
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    
    # Machine Learning settings
    ML_MODEL_CACHE_SIZE: int = 3  # Number of models to keep in memory
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"
    
    # Feature flags
    ENABLE_UPSCALING: bool = True
    ENABLE_WATERMARK_DETECTION: bool = True
    ENABLE_CONTENT_MODERATION: bool = True
    ENABLE_METRICS: bool = True
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def validate_origins(cls, v):
        if not v:
            return ["*"]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Development/Testing overrides
if settings.DEBUG:
    settings.DATABASE_ECHO = True
    settings.LOG_LEVEL = "DEBUG"

if settings.TESTING:
    settings.DATABASE_URL = settings.DATABASE_URL.replace("/movierecap", "/movierecap_test")
    settings.REDIS_URL = settings.REDIS_URL.replace("/0", "/15")  # Use different Redis DB for tests