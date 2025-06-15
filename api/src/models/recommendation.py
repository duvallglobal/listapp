from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RecommendationType(str, Enum):
    PLATFORM = "platform"
    PRICING = "pricing"
    LISTING = "listing"
    TIMING = "timing"
    PHOTOGRAPHY = "photography"

class RecommendationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PlatformFeatures(BaseModel):
    auction_format: bool = False
    fixed_price: bool = True
    best_offer: bool = False
    local_pickup: bool = False
    international_shipping: bool = False
    promoted_listings: bool = False
    store_subscription: bool = False
    bulk_listing_tools: bool = False
    mobile_app_quality: str = "good"  # poor, fair, good, excellent
    seller_protection: str = "standard"  # basic, standard, premium

class FeeStructure(BaseModel):
    listing_fee: float = 0.0
    final_value_fee_percentage: float
    final_value_fee_cap: Optional[float] = None
    payment_processing_fee: float = 0.0
    additional_fees: Dict[str, float] = Field(default_factory=dict)
    total_fee_estimate: float
    
    @validator('total_fee_estimate')
    def calculate_total_fee(cls, v, values):
        # This would be calculated based on item price
        return v

class AudienceInsights(BaseModel):
    primary_demographics: Dict[str, Any] = Field(default_factory=dict)
    buying_behavior: Dict[str, Any] = Field(default_factory=dict)
    price_sensitivity: str = "medium"  # low, medium, high
    brand_preference: str = "mixed"  # brand_focused, value_focused, mixed
    category_popularity: float = Field(ge=0.0, le=10.0)
    seasonal_trends: Dict[str, float] = Field(default_factory=dict)

class PlatformRecommendation(BaseModel):
    platform_name: str
    overall_score: float = Field(ge=0.0, le=10.0)
    
    # Detailed scoring
    audience_match_score: float = Field(ge=0.0, le=10.0)
    fee_competitiveness_score: float = Field(ge=0.0, le=10.0)
    ease_of_use_score: float = Field(ge=0.0, le=10.0)
    reach_potential_score: float = Field(ge=0.0, le=10.0)
    
    # Financial projections
    estimated_gross_revenue: float
    estimated_fees: float
    estimated_net_profit: float
    profit_margin_percentage: float
    
    # Timing estimates
    estimated_listing_time_minutes: int
    estimated_time_to_sell_days: Optional[int] = None
    
    # Platform details
    features: PlatformFeatures
    fee_structure: FeeStructure
    audience_insights: AudienceInsights
    
    # Recommendations
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    optimization_tips: List[str] = Field(default_factory=list)
    
    # Risk factors
    risk_factors: List[str] = Field(default_factory=list)
    risk_level: str = "low"  # low, medium, high
    
class PricingRecommendation(BaseModel):
    strategy: str = Field(..., description="aggressive, competitive, premium, quick_sale")
    recommended_price: float
    price_range: Dict[str, float]  # {"min": x, "max": y}
    
    # Justification
    reasoning: str
    market_position: str  # below_market, at_market, above_market
    competition_analysis: str
    
    # Alternative strategies
    alternative_strategies: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Dynamic pricing suggestions
    price_adjustment_triggers: List[str] = Field(default_factory=list)
    seasonal_adjustments: Dict[str, float] = Field(default_factory=dict)
    
class ListingRecommendation(BaseModel):
    title_suggestions: List[str] = Field(default_factory=list)
    description_template: str
    key_selling_points: List[str] = Field(default_factory=list)
    
    # SEO optimization
    primary_keywords: List[str] = Field(default_factory=list)
    secondary_keywords: List[str] = Field(default_factory=list)
    category_suggestions: List[str] = Field(default_factory=list)
    
    # Content recommendations
    photo_requirements: List[str] = Field(default_factory=list)
    additional_info_needed: List[str] = Field(default_factory=list)
    
    # Platform-specific optimizations
    platform_specific_tips: Dict[str, List[str]] = Field(default_factory=dict)
    
class TimingRecommendation(BaseModel):
    best_listing_days: List[str] = Field(default_factory=list)
    best_listing_times: List[str] = Field(default_factory=list)
    seasonal_considerations: str
    market_timing_score: float = Field(ge=0.0, le=10.0)
    
    # Event-based timing
    upcoming_events: List[Dict[str, Any]] = Field(default_factory=list)
    holiday_considerations: List[str] = Field(default_factory=list)
    
class PhotographyRecommendation(BaseModel):
    current_photo_quality_score: float = Field(ge=0.0, le=10.0)
    improvement_suggestions: List[str] = Field(default_factory=list)
    
    # Technical recommendations
    lighting_tips: List[str] = Field(default_factory=list)
    angle_suggestions: List[str] = Field(default_factory=list)
    background_recommendations: List[str] = Field(default_factory=list)
    
    # Additional photos needed
    missing_photo_types: List[str] = Field(default_factory=list)
    
class ComprehensiveRecommendation(BaseModel):
    recommendation_id: str
    product_analysis_id: str
    user_id: Optional[str] = None
    
    # Core recommendations
    platform_recommendations: List[PlatformRecommendation] = Field(default_factory=list)
    pricing_recommendation: PricingRecommendation
    listing_recommendation: ListingRecommendation
    timing_recommendation: TimingRecommendation
    photography_recommendation: PhotographyRecommendation
    
    # Overall insights
    market_opportunity_score: float = Field(ge=0.0, le=10.0)
    competition_level: str = "medium"  # low, medium, high
    profit_potential: str = "good"  # poor, fair, good, excellent
    
    # Action items
    immediate_actions: List[str] = Field(default_factory=list)
    long_term_strategies: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    confidence_score: float = Field(ge=0.0, le=1.0)
    
class RecommendationFeedback(BaseModel):
    recommendation_id: str
    user_id: str
    
    # Feedback scores
    overall_satisfaction: int = Field(ge=1, le=5)
    accuracy_score: int = Field(ge=1, le=5)
    usefulness_score: int = Field(ge=1, le=5)
    
    # Specific feedback
    platform_recommendation_helpful: bool
    pricing_recommendation_helpful: bool
    listing_recommendation_helpful: bool
    
    # Outcomes
    did_follow_recommendations: bool = False
    actual_selling_price: Optional[float] = None
    actual_platform_used: Optional[str] = None
    time_to_sell_days: Optional[int] = None
    
    # Comments
    comments: Optional[str] = None
    suggestions_for_improvement: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
class RecommendationTemplate(BaseModel):
    template_id: str
    name: str
    category: str
    condition_applicability: List[str] = Field(default_factory=list)
    
    # Template content
    title_templates: List[str] = Field(default_factory=list)
    description_templates: List[str] = Field(default_factory=list)
    keyword_suggestions: List[str] = Field(default_factory=list)
    
    # Usage stats
    usage_count: int = 0
    success_rate: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
