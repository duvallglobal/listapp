from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ConditionType(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new" 
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class AnalysisRequest(BaseModel):
    condition: ConditionType
    notes: Optional[str] = None

class ProductIdentification(BaseModel):
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    age_estimate: Optional[str] = None
    authenticity_confidence: Optional[float] = Field(None, ge=0, le=1)

class VisionAnalysis(BaseModel):
    confidence: float = Field(..., ge=0, le=1)
    detected_objects: List[str] = Field(default_factory=list)
    text_content: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    quality_assessment: Optional[str] = None
    damage_indicators: List[str] = Field(default_factory=list)

class MarketData(BaseModel):
    similar_products: List[Dict[str, Any]] = Field(default_factory=list)
    price_range: Dict[str, float] = Field(default_factory=dict)
    average_price: Optional[float] = None
    market_trends: Dict[str, Any] = Field(default_factory=dict)
    competition_level: Optional[str] = None

class PlatformRecommendation(BaseModel):
    platform: str
    suitability_score: float = Field(..., ge=0, le=1)
    estimated_price: float
    estimated_sale_time: Optional[str] = None
    fees_percentage: float
    net_profit: float
    reasoning: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)

class ListingContent(BaseModel):
    title: str
    description: str
    key_features: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    condition_statement: str
    shipping_recommendations: List[str] = Field(default_factory=list)

class AnalysisResult(BaseModel):
    task_id: str
    status: AnalysisStatus
    stage: Optional[str] = None
    progress: int = Field(0, ge=0, le=100)

    # Core analysis data
    product_identification: Optional[ProductIdentification] = None
    vision_analysis: Optional[VisionAnalysis] = None
    market_data: Optional[MarketData] = None

    # Recommendations
    platform_recommendations: List[PlatformRecommendation] = Field(default_factory=list)
    listing_content: Optional[ListingContent] = None

    # Metadata
    user_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[AnalysisResult] = None
    error: Optional[str] = None
    message: Optional[str] = None

class AnalysisHistoryItem(BaseModel):
    id: str
    user_id: str
    product_name: str
    condition: ConditionType
    estimated_value: Optional[float] = None
    best_platform: Optional[str] = None
    confidence_score: Optional[float] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AnalysisStats(BaseModel):
    total_analyses: int
    period_days: int
    daily_breakdown: Dict[str, int]
    average_per_day: float
    most_analyzed_categories: List[Dict[str, Any]] = Field(default_factory=list)
    average_estimated_value: Optional[float] = None