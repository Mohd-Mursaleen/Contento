"""Configuration management for the Content Creation Pipeline."""

import os
from typing import Dict, Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    app_name: str = "Content Creation Pipeline"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # AI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 3600  # 1 hour
    
    # Content Generation Settings
    max_content_length: int = 5000
    default_quality_threshold: float = 0.7
    
    # Optional fields that might be in .env but not used
    database_url: str = ""
    redis_url: str = ""
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"  # Ignore extra fields in .env
    }


# Global settings instance
settings = Settings()


def get_agent_config() -> Dict[str, Any]:
    """Get configuration for AI agents."""
    return {
        "openai_api_key": settings.openai_api_key,
        "model": settings.openai_model,
        "max_tokens": 4000,
        "temperature": 0.7,
        "timeout": 60
    }