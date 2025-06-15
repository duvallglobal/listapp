
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Configuration
    APP_NAME: str = "Price Intelligence API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Keys - Vision Services
    GOOGLE_VISION_API_KEY: str
    GOOGLE_GEMINI_API_KEY: str
    MICROSOFT_VISION_API_KEY: str
    MICROSOFT_VISION_ENDPOINT: str
    OPENAI_API_KEY: Optional[str] = None
    
    # API Keys - Marketplace Services  
    GOOGLE_SHOPPING_API_KEY: str
    EBAY_APP_ID: str
    
    # Database & Authentication
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_ANON_KEY: str
    DATABASE_URL: Optional[str] = None
    
    # Cache & Session
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    
    # Payment Processing
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    
    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000", 
        "https://*.replit.dev",
        "https://*.replit.app"
    ]
    
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
    CACHE_EXPIRATION_HOURS: int = 24
    
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
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Dependency function for FastAPI
def get_settings() -> Settings:
    return settings


# Validation functions
def validate_api_keys():
    """Validate that required API keys are present"""
    required_keys = [
        "GOOGLE_VISION_API_KEY",
        "GOOGLE_GEMINI_API_KEY", 
        "MICROSOFT_VISION_API_KEY",
        "GOOGLE_SHOPPING_API_KEY",
        "EBAY_APP_ID",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not getattr(settings, key, None):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")


def get_marketplace_fee(platform: str) -> float:
    """Get fee percentage for a marketplace platform"""
    return settings.MARKETPLACE_FEES.get(platform.lower(), 0.10)  # Default 10%


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature flag is enabled"""
    feature_map = {
        "google_shopping": settings.ENABLE_GOOGLE_SHOPPING,
        "ebay": settings.ENABLE_EBAY_INTEGRATION,
        "microsoft_vision": settings.ENABLE_MICROSOFT_VISION,
        "gemini_pro": settings.ENABLE_GEMINI_PRO,
        "mock_data": settings.ENABLE_MOCK_DATA
    }
    return feature_map.get(feature.lower(), False)


def get_subscription_tier(tier_name: str) -> dict:
    """Get subscription tier configuration"""
    return settings.SUBSCRIPTION_TIERS.get(tier_name.lower(), settings.SUBSCRIPTION_TIERS["free_trial"])


# Initialize validation on import
try:
    validate_api_keys()
except ValueError as e:
    print(f"Configuration Warning: {e}")
    print("Some features may not work without proper API keys configured.")
