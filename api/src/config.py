from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    
    # API Keys
    OPENAI_API_KEY: str
    GOOGLE_VISION_API_KEY: Optional[str] = None
    AZURE_VISION_API_KEY: Optional[str] = None
    
    # eBay API
    EBAY_APP_ID: Optional[str] = None
    EBAY_CERT_ID: Optional[str] = None
    EBAY_DEV_ID: Optional[str] = None
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: Optional[str] = None
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    ANALYSIS_CACHE_TTL: int = 86400  # 24 hours
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # AI Model settings
    DEFAULT_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
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
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validation
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")

if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase configuration is required")

# Log configuration (without sensitive data)
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Redis URL: {settings.REDIS_URL}")
print(f"Supported marketplaces: {settings.SUPPORTED_MARKETPLACES}")
print(f"Cache TTL: {settings.CACHE_TTL}s")
