from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ProductCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_garden"
    SPORTS_OUTDOORS = "sports_outdoors"
    BOOKS_MEDIA = "books_media"
    TOYS_GAMES = "toys_games"
    AUTOMOTIVE = "automotive"
    HEALTH_BEAUTY = "health_beauty"
    JEWELRY_ACCESSORIES = "jewelry_accessories"
    COLLECTIBLES = "collectibles"
    OTHER = "other"

class ImageAnalysisRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image data")
    condition: ProductCondition = Field(default=ProductCondition.GOOD)
    additional_info: Optional[str] = Field(None, description="Additional product information")
    
    @validator('image_data')
    def validate_image_data(cls, v):
        if not v or len(v) < 100:
            raise ValueError("Invalid image data")
        return v

class ProductFeatures(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    year: Optional[int] = None
    condition_details: Optional[str] = None
    key_features: List[str] = Field(default_factory=list)
    defects: List[str] = Field(default_factory=list)
    accessories_included: List[str] = Field(default_factory=list)

class ProductIdentification(BaseModel):
    name: str = Field(..., description="Product name")
    category: ProductCategory
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    upc: Optional[str] = None
    ean: Optional[str] = None
    asin: Optional[str] = None
    mpn: Optional[str] = None  # Manufacturer Part Number
    features: ProductFeatures = Field(default_factory=ProductFeatures)
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in identification")
    
class PriceRange(BaseModel):
    low: float = Field(ge=0, description="Lowest estimated price")
    median: float = Field(ge=0, description="Median estimated price")
    high: float = Field(ge=0, description="Highest estimated price")
    currency: str = Field(default="USD")
    
    @validator('median')
    def validate_price_order(cls, v, values):
        if 'low' in values and v < values['low']:
            raise ValueError("Median price cannot be lower than low price")
        return v
    
    @validator('high')
    def validate_high_price(cls, v, values):
        if 'median' in values and v < values['median']:
            raise ValueError("High price cannot be lower than median price")
        return v

class MarketData(BaseModel):
    source: str = Field(..., description="Data source (e.g., 'ebay', 'amazon')")
    average_price: Optional[float] = None
    price_range: Optional[PriceRange] = None
    total_listings: Optional[int] = None
    sold_listings: Optional[int] = None
    average_days_to_sell: Optional[int] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    sample_listings: List[Dict[str, Any]] = Field(default_factory=list)

class ProductAnalysisResult(BaseModel):
    product_id: Optional[str] = None
    identification: ProductIdentification
    condition: ProductCondition
    estimated_pricing: PriceRange
    market_data: List[MarketData] = Field(default_factory=list)
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: Optional[float] = None
    
class BulkAnalysisRequest(BaseModel):
    images: List[ImageAnalysisRequest] = Field(..., max_items=10)
    batch_id: Optional[str] = None
    
    @validator('images')
    def validate_images_count(cls, v):
        if len(v) == 0:
            raise ValueError("At least one image is required")
        if len(v) > 10:
            raise ValueError("Maximum 10 images per batch")
        return v

class ProductSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[ProductCategory] = None
    condition: Optional[ProductCondition] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = None
    
    @validator('price_max')
    def validate_price_range(cls, v, values):
        if v is not None and 'price_min' in values and values['price_min'] is not None:
            if v < values['price_min']:
                raise ValueError("Maximum price cannot be lower than minimum price")
        return v

class ProductListing(BaseModel):
    title: str
    description: str
    price: float
    condition: ProductCondition
    images: List[str] = Field(default_factory=list)
    seller_info: Optional[Dict[str, Any]] = None
    listing_url: Optional[str] = None
    platform: str
    posted_date: Optional[datetime] = None
    sold_date: Optional[datetime] = None
    shipping_cost: Optional[float] = None
    location: Optional[str] = None
