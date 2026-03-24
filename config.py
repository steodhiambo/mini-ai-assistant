"""
Configuration module for the Mini AI Assistant.

Centralizes all configuration settings and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)


class Config:
    """Application configuration."""
    
    # API Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    GEMINI_MAX_TOKENS: int = int(os.getenv("GEMINI_MAX_TOKENS", "1024"))
    GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "30"))
    
    # Database Configuration
    DB_FILE: Path = Path(__file__).parent / "assistant.db"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    
    # Web Server Configuration
    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", os.urandom(24).hex())
    
    # Security Configuration
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "False").lower() == "true"
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100 per hour")
    
    # History Configuration
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required configuration.
        
        Returns:
            True if configuration is valid.
        """
        if not cls.GEMINI_API_KEY:
            return False
        return True
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment (development/production)."""
        return "development" if cls.FLASK_DEBUG else "production"


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    FLASK_DEBUG = True
    FLASK_HOST = "127.0.0.1"


class ProductionConfig(Config):
    """Production-specific configuration."""
    FLASK_DEBUG = False
    RATE_LIMIT_ENABLED = True


def get_config() -> Config:
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
