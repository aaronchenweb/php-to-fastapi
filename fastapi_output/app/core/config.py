"""
Core application configuration.
Generated from PHP project analysis.
"""

import os
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, validator, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Project Information
    PROJECT_NAME: str = Field(default="FastAPI Application", env="PROJECT_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    DESCRIPTION: str = Field(default="API converted from PHP", env="DESCRIPTION")
    
    # API Configuration
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    # CORS Configuration
    CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS"
    )
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from environment variable."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Authentication Configuration
    # JWT_SECRET_KEY: str = Field(env="JWT_SECRET_KEY")  # Uncomment if using JWT
    
    # Email Configuration (if needed)
    # SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    # SMTP_PORT: Optional[int] = Field(default=None, env="SMTP_PORT")
    # SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    # SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    # SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Redis Configuration (if needed)
    # REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File Upload Configuration
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Pagination Defaults
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is set."""
        if not v:
            raise ValueError("SECRET_KEY must be set")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# Global settings instance
settings = Settings()