from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class MarketplacePlatform(str, Enum):
    EBAY = "ebay"
    FACEBOOK_MARKETPLACE = "facebook_marketplace"
    MERCARI = "mercari"
    POSHMARK = "poshmark"
    AMAZON = "amazon"
    DEPOP = "depop"
    VINTED = "vinted"
    ETSY = "etsy"
    CRAIGSLIST = "craigslist"
    OFFERUP = "offerup"

class RecommendationConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class PricingStrategy(str, Enum):
    COMPETITIVE = "competitive"
    PREMIUM = "premium"
    QUICK_SALE = "quick_sale"
    MARKET_AVERAGE = "market_average"

class MarketplaceRecommendation(BaseModel):
    platform: MarketplacePlatform
    rank: int = Field(..., ge=1)
    suitability_score: float = Field(..., ge=0, le=1)
    confidence: RecommendationConfidence

    # Pricing information
    recommended_price: float = Field(..., gt=0)
    price_range: Dict[str, float]  # {"min": 0, "max": 0}
    pricing_strategy: PricingStrategy

    # Financial breakdown
    platform_fees: float
    payment_processing_fees: float
    shipping_cost_estimate: float
    net_profit: float
    profit_margin_percentage: float

    # Timing and market data
    estimated_sale_time_days: Optional[int] = None
    demand_level: str  # "high", "medium", "low"
    competition_level: str  # "high", "medium", "low"

    # Platform-specific insights
    reasoning: str
    key_advantages: List[str] = Field(default_factory=list)
    potential_challenges: List[str] = Field(default_factory=list)
    optimization_tips: List[str] = Field(default_factory=list)

    # Similar product data
    similar_product_count: int
    average_similar_price: Optional[float] = None
    price_trend: Optional[str] = None  # "increasing", "stable", "decreasing"

class ListingOptimization(BaseModel):
    title: str = Field(..., max_length=80)
    description: str
    key_selling_points: List[str] = Field(default_factory=list)
    suggested_tags: List[str] = Field(default_factory=list)
    condition_description: str

    # SEO optimization
    search_keywords: List[str] = Field(default_factory=list)
    category_suggestions: List[str] = Field(default_factory=list)

    # Photography recommendations
    photo_tips: List[str] = Field(default_factory=list)
    required_photo_angles: List[str] = Field(default_factory=list)

    # Shipping and handling
    shipping_recommendations: List[str] = Field(default_factory=list)
    packaging_tips: List[str] = Field(default_factory=list)

class MarketAnalysis(BaseModel):
    category: str
    subcategory: Optional[str] = None
    brand_popularity: Optional[float] = Field(None, ge=0, le=1)
    seasonal_trends: Dict[str, Any] = Field(default_factory=dict)
    demand_indicators: Dict[str, Any] = Field(default_factory=dict)

    # Competitive analysis
    competitor_count: int
    average_competitor_price: float
    price_distribution: Dict[str, int] = Field(default_factory=dict)
    market_saturation: str  # "low", "medium", "high"

    # Market insights
    best_selling_months: List[str] = Field(default_factory=list)
    target_demographics: List[str] = Field(default_factory=list)
    trending_keywords: List[str] = Field(default_factory=list)

class RecommendationReport(BaseModel):
    analysis_id: str
    product_name: str
    condition: str
    estimated_value: float
    confidence_score: float = Field(..., ge=0, le=1)

    # Recommendations
    marketplace_recommendations: List[MarketplaceRecommendation]
    listing_optimization: ListingOptimization
    market_analysis: MarketAnalysis

    # Summary insights
    top_recommendation: MarketplaceRecommendation
    quick_sale_option: Optional[MarketplaceRecommendation] = None
    maximum_profit_option: Optional[MarketplaceRecommendation] = None

    # Metadata
    generated_at: datetime
    data_sources: List[str] = Field(default_factory=list)
    analysis_version: str = "1.0"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PriceAlert(BaseModel):
    id: str
    user_id: str
    product_keywords: str
    target_price: float
    current_market_price: Optional[float] = None
    price_change_threshold: float = 0.1  # 10% change
    platforms_to_monitor: List[MarketplacePlatform]
    is_active: bool = True
    created_at: datetime
    last_checked: Optional[datetime] = None
    triggered_count: int = 0