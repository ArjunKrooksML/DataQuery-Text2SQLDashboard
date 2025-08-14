from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):

    DATABASE_URL: str = Field(default="postgresql://postgres:root@localhost:5432/datawiser_platform")
    DATABASE_URL_ASYNC: str = Field(default="postgresql+asyncpg://postgres:root@localhost:5432/datawiser_platform")
    POSTGRES_PASSWORD: str = Field(default="root")
    

    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    MONGODB_DATABASE: str = Field(default="datadashboard_cache")
    

    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key - required for LLM features")
    

    REDIS_URL: str = Field(default="redis://localhost:6379")
    

    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")
    API_V1_STR: str = Field(default="/api/v1")
    PROJECT_NAME: str = Field(default="DataWise API")
    

    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:9002", "http://localhost:3000"])
    

    SESSION_EXPIRE_MINUTES: int = Field(default=60)
    CACHE_EXPIRE_MINUTES: int = Field(default=30)
    

    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=3600)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 