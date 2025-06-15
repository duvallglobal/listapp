from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_TITLE: str = "Price Intelligence API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_NAME: str = "Price Intelligence API"
    VERSION: str = "1.0.0"

    # Database & Authentication
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_ANON_KEY: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None

    # AI Service API Keys
    GOOGLE_VISION_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    MICROSOFT_VISION_API_KEY: str
    MICROSOFT_VISION_ENDPOINT: str
    OPENAI_API_KEY: Optional[str] = None
    
    # Market Data APIs
    SERPAPI_KEY: Optional[str] = None
    EBAY_APP_ID: str
    
    # Payment Processing
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000", 
        "https://*.replit.dev",
        "https://*.replit.app"
    ]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

    # Cache TTL (seconds)
    ANALYSIS_CACHE_TTL: int = 3600  # 1 hour
    PRICE_CACHE_TTL: int = 1800     # 30 minutes
    CACHE_EXPIRATION_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Supported Marketplaces
    SUPPORTED_MARKETPLACES: List[str] = [
        "ebay",
        "facebook_marketplace", 
        "mercari",
        "poshmark"
    ]
    
    # Marketplace Fee Structures (percentages)
    MARKETPLACE_FEES: dict = {
        "ebay": 0.1325,  # 13.25%
        "facebook_marketplace": 0.05,  # 5%
        "mercari": 0.10,  # 10%
        "poshmark": 0.20,  # 20%
        "amazon": 0.15,  # 15% (average)
        "depop": 0.10,  # 10%
        "vinted": 0.07  # 7%
    }
    
    # AI Service Configuration
    MAX_IMAGE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_FORMATS: List[str] = ["jpg", "jpeg", "png", "heic", "heif", "webp"]
    
    # Analysis Configuration
    DEFAULT_ANALYSIS_TIMEOUT: int = 300  # 5 minutes
    MAX_CONCURRENT_ANALYSES: int = 10
    
    # Subscription Tiers
    SUBSCRIPTION_TIERS: dict = {
        "free_trial": {
            "name": "Free Trial",
            "analysis_limit": 2,
            "price_monthly": 0,
            "features": ["Basic AI analysis", "Price estimates", "Marketplace suggestions"]
        },
        "basic": {
            "name": "Basic",
            "analysis_limit": 20,
            "price_monthly": 9.99,
            "features": ["20 monthly analyses", "Basic AI analysis", "Price estimates", "Marketplace suggestions", "Email support"]
        },
        "pro": {
            "name": "Pro", 
            "analysis_limit": 50,
            "price_monthly": 19.99,
            "features": ["50 monthly analyses", "Advanced AI analysis", "Detailed price breakdowns", "Priority support", "Export analysis data", "Listing optimization tips"]
        },
        "business": {
            "name": "Business",
            "analysis_limit": 100, 
            "price_monthly": 29.99,
            "features": ["100 monthly analyses", "Premium AI models", "Advanced analytics", "Priority support", "Export capabilities", "Bulk analysis"]
        },
        "enterprise": {
            "name": "Enterprise",
            "analysis_limit": -1,  # Unlimited
            "price_monthly": 69.99,
            "features": ["Unlimited analyses", "White-label options", "Advanced features", "Priority support", "Custom integrations"]
        }
    }
    
    # Feature Flags
    ENABLE_GOOGLE_SHOPPING: bool = True
    ENABLE_EBAY_INTEGRATION: bool = True
    ENABLE_MICROSOFT_VISION: bool = True
    ENABLE_GEMINI_PRO: bool = True
    ENABLE_MOCK_DATA: bool = False  # Set to False for production
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Email Configuration (for notifications)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    
    # Monitoring & Analytics
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()

# Validate critical settings
def validate_settings():
    """Validate that critical settings are configured"""
    warnings = []

    if not settings.GOOGLE_GEMINI_API_KEY:
        warnings.append("GOOGLE_GEMINI_API_KEY not set - AI content generation will fail")

    if not settings.SERPAPI_KEY:
        warnings.append("SERPAPI_KEY not set - market research will fail")

    if not settings.GOOGLE_VISION_API_KEY:
        warnings.append("GOOGLE_VISION_API_KEY not set - image analysis may be limited")

    if not settings.MICROSOFT_VISION_API_KEY:
        warnings.append("MICROSOFT_VISION_API_KEY not set - image analysis may be limited")

    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        warnings.append("Supabase not configured - user features will be limited")
        
    if not settings.STRIPE_SECRET_KEY:
        warnings.append("Stripe not configured - payment features will be limited")

    for warning in warnings:
        import logging
        logging.getLogger(__name__).warning(warning)

# Run validation on import
validate_settings()