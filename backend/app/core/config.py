from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    # App
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://alfabank_user:alfabank_password@postgres:5432/alfabank_db")
    
    # Redis
    REDIS_URL: str = Field(default="redis://redis:6379")
    
    # JWT
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production-12345")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=24)
    
    # Paths
    MODEL_PATH: str = Field(default="/app/models")
    DATA_PATH: str = Field(default="/app/data")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# CORS - это КОНСТАНТА, не конфиг!
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

settings = Settings()
