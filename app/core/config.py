# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import secrets


class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "Email Security System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False  # Set to True for development

    # Redis configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int =  6379
    REDIS_DB: int =  0
    REDIS_PASSWORD: str =None

    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Environment settings
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # production, development, testing
    
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str ="db"
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_SSL_MODE: bool = False
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int 
    EMAIL_TOKEN_EXPIRE_MINUTES: int

    # OTP settings
    VALID_WINDOW: int
    
    # Email settings
    EMAIL_USERNAME: str 
    EMAIL_PASSWORD: str 
    SMTP_SERVER: str 
    SMTP_PORT: int 
    FROM_EMAIL: str 

    #Encryption settings
    ENCRYPTION_KEY: str

    #Paths settings
    GMAIL_CLIENT_SECRET_PATH: str
    GMAIL_REDIRECT_URI: str
    
    # API Documentation settings
    DOCS_URL: Optional[str] = "/api/docs"
    REDOC_URL: Optional[str] = "/api/redoc"
    OPENAPI_URL: Optional[str] = "/api/openapi.json"
    
    # Rate Limiting settings
    RATE_LIMIT_PER_SECOND: int = 10
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    
    @property
    def sync_database_url(self) -> str:
        postgres_url = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if self.DATABASE_SSL_MODE:
            postgres_url += "?sslmode=require"
        return postgres_url

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"

# Create a singleton instance of settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()