from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from .product import ProductCondition, ProductCategory, PriceRange

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AnalysisType(str, Enum):
    QUICK = "quick"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    BULK = "bulk"

class VisionAnalysisResult(BaseModel):
    labels: List[str] = Field(default_factory=list)
    objects: List[Dict[str, Any]] = Field(default_factory=list)
    text_detections: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    processing_time: Optional[float] = None
    
class MarketplaceAnalysis(BaseModel):
    platform: str
    average_price: Optional[float] = None
    price_range: Optional[PriceRange] = None
    total_active_listings: Optional[int] = None
    sold_listings_30d: Optional[int] = None
    average_sell_time_days: Optional[int] = None
    competition_level: Optional[str] = None  # low, medium, high
    trending: Optional[bool] = None
    seasonal_factor: Optional[float] = None
    sample_listings: List[Dict[str, Any]] = Field(default_factory=list)

class PricingAnalysis(BaseModel):
    estimated_value: PriceRange
    market_position: str = Field(..., description="below_market, at_market, above_market")
    price_confidence: float = Field(ge=0.0, le=1.0)
    factors_affecting_price: List[str] = Field(default_factory=list)
    comparable_items: List[Dict[str, Any]] = Field(default_factory=list)
    pricing_strategy: Optional[str] = None
    optimal_listing_price: Optional[float] = None
    quick_sale_price: Optional[float] = None
    
class ListingOptimization(BaseModel):
    optimized_title: str
    optimized_description: str
    suggested_keywords: List[str] = Field(default_factory=list)
    category_suggestions: List[str] = Field(default_factory=list)
    photo_recommendations: List[str] = Field(default_factory=list)
    timing_recommendations: Optional[str] = None
    
class PlatformRecommendation(BaseModel):
    platform: str
    suitability_score: float = Field(ge=0.0, le=10.0)
    estimated_fees: float
    estimated_net_profit: float
    audience_match: str = Field(..., description="poor, fair, good, excellent")
    ease_of_listing: str = Field(..., description="easy, moderate, difficult")
    time_to_sell_estimate: Optional[str] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    specific_recommendations: List[str] = Field(default_factory=list)
    
class ComprehensiveAnalysis(BaseModel):
    # Core identification
    product_name: str
    category: ProductCategory
    condition: ProductCondition
    brand: Optional[str] = None
    model: Optional[str] = None
    
    # Vision analysis results
    vision_analysis: VisionAnalysisResult
    
    # Market analysis
    marketplace_analysis: List[MarketplaceAnalysis] = Field(default_factory=list)
    
    # Pricing analysis
    pricing_analysis: PricingAnalysis
    
    # Platform recommendations
    platform_recommendations: List[PlatformRecommendation] = Field(default_factory=list)
    
    # Listing optimization
    listing_optimization: ListingOptimization
    
    # Metadata
    analysis_id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: float
    confidence_score: float = Field(ge=0.0, le=1.0)
    
class AnalysisTask(BaseModel):
    task_id: str
    user_id: Optional[str] = None
    analysis_type: AnalysisType
    status: AnalysisStatus
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_step: Optional[str] = None
    estimated_completion_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[ComprehensiveAnalysis] = None
    
class AnalysisRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image")
    condition: ProductCondition = ProductCondition.GOOD
    analysis_type: AnalysisType = AnalysisType.DETAILED
    additional_context: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    user_preferences: Optional[Dict[str, Any]] = None
    
    @validator('image_data')
    def validate_image_data(cls, v):
        if not v or len(v) < 100:
            raise ValueError("Invalid image data provided")
        # Check if it's base64 encoded
        try:
            import base64
            base64.b64decode(v.split(',')[-1])  # Handle data URL format
        except Exception:
            raise ValueError("Image data must be base64 encoded")
        return v
        
    @validator('target_platforms')
    def validate_platforms(cls, v):
        if v:
            valid_platforms = {
                'ebay', 'amazon', 'facebook_marketplace', 'poshmark', 
                'mercari', 'depop', 'vinted', 'etsy', 'bonanza'
            }
            invalid_platforms = set(v) - valid_platforms
            if invalid_platforms:
                raise ValueError(f"Invalid platforms: {invalid_platforms}")
        return v

class BulkAnalysisRequest(BaseModel):
    requests: List[AnalysisRequest] = Field(..., min_items=1, max_items=10)
    batch_name: Optional[str] = None
    priority: int = Field(default=5, ge=1, le=10)
    
class AnalysisHistory(BaseModel):
    analysis_id: str
    user_id: str
    product_name: str
    category: ProductCategory
    estimated_value: float
    recommended_platform: str
    created_at: datetime
    thumbnail_url: Optional[str] = None
    
class AnalysisStats(BaseModel):
    total_analyses: int
    analyses_this_month: int
    average_estimated_value: float
    most_common_category: str
    most_recommended_platform: str
    success_rate: float
    average_processing_time: float
    
class AnalysisFilter(BaseModel):
    user_id: Optional[str] = None
    category: Optional[ProductCategory] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    platform: Optional[str] = None
    status: Optional[AnalysisStatus] = None
    
class AnalysisExport(BaseModel):
    format: str = Field(..., regex="^(csv|json|xlsx)$")
    filters: Optional[AnalysisFilter] = None
    include_images: bool = False
    include_detailed_analysis: bool = True
