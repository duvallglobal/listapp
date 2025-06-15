from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    google_vision_api_key: str
    ebay_app_id: str

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # n8n
    n8n_user: Optional[str] = None
    n8n_password: Optional[str] = None

    # Environment
    environment: str = "development"
    debug: bool = True

    # Cache settings
    cache_ttl: int = 3600  # 1 hour default
    ANALYSIS_CACHE_TTL: int = 86400  # 24 hours

    # AI settings
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.2
    max_analysis_retries: int = 3
    MAX_TOKENS: int = 2000

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Vision API settings
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_IMAGE_FORMATS: list = ["jpeg", "jpg", "png", "webp"]

    # Marketplace settings
    SUPPORTED_MARKETPLACES: list = [
        "ebay", "amazon", "facebook_marketplace",
        "poshmark", "mercari", "depop", "vinted"
    ]

    # Fee structures (as percentages)
    MARKETPLACE_FEES: dict = {
        "ebay": 0.1325,  # 13.25%
        "amazon": 0.15,   # 15%
        "facebook_marketplace": 0.05,  # 5%
        "poshmark": 0.20,  # 20%
        "mercari": 0.1275,  # 12.75%
        "depop": 0.10,     # 10%
        "vinted": 0.05     # 5%
    }

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# Validation
if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY is required")

if not settings.supabase_url or not settings.supabase_service_key:
    raise ValueError("Supabase configuration is required")

# Log configuration (without sensitive data)
print(f"Environment: {settings.environment}")
print(f"Redis URL: {settings.redis_url}")
print(f"Supported marketplaces: {settings.SUPPORTED_MARKETPLACES}")
print(f"Cache TTL: {settings.cache_ttl}s")