"""
Configuration settings for the PDF Annotation Platform
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support



    """

    # Database Configuration
    database_hostname: str = Field(default="localhost", description="Database host")
    database_port: str = Field(default="5432", description="Database port")
    database_password: str = Field(description="Database password")
    database_name: str = Field(description="Database name")
    database_username: str = Field(description="Database username")

    # Redis Configuration
    redis_hostname: str = Field(default="localhost", description="Redis host")
    redis_port: str = Field(default="6379", description="Redis port")
    redis_password: Optional[str] = Field(default=None, description="Redis password")

    # JWT Security Configuration
    secret_key: str = Field(description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Token expiry in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiry in days"
    )

    # Application Configuration
    app_name: str = Field(
        default="PDF Annotation Platform", description="Application name"
    )
    debug: bool = Field(default=False, description="Debug mode")
    version: str = Field(default="1.0.0", description="API version")

    # CORS Configuration
    backend_cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    class Config:
        """
        Pydantic configuration
        Tells Pydantic to read from .env file
        """

        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """
        Construct database URL from components


        """
        return (
            f"postgresql+asyncpg://{self.database_username}:{self.database_password}"
            f"@{self.database_hostname}:{self.database_port}/{self.database_name}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_hostname}:{self.redis_port}/0"
        return f"redis://{self.redis_hostname}:{self.redis_port}/0"


# Global settings instance
# This replaces hardcoded values throughout the application
settings = Settings()
