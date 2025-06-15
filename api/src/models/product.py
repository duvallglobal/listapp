from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProductCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    VERY_GOOD = "very_good"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


class ProductCategory(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    HOME_GARDEN = "home_garden"
    SPORTS = "sports"
    COLLECTIBLES = "collectibles"
    BOOKS = "books"
    TOYS = "toys"
    AUTOMOTIVE = "automotive"
    JEWELRY = "jewelry"
    OTHER = "other"


class PriceRange(BaseModel):
    min_price: float = Field(ge=0)
    max_price: float = Field(ge=0)
    average_price: float = Field(ge=0)

    @validator('max_price')
    def max_price_must_be_greater_than_min(cls, v, values):
        if 'min_price' in values and v < values['min_price']:
            raise ValueError('max_price must be greater than or equal to min_price')
        return v


class ProductIdentification(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    brand: Optional[str] = None
    model: Optional[str] = None
    category: ProductCategory
    subcategory: Optional[str] = None

    # Product identifiers
    upc: Optional[str] = None
    ean: Optional[str] = None
    isbn: Optional[str] = None
    mpn: Optional[str] = None  # Manufacturer Part Number

    # Physical attributes
    color: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None

    # Product details
    description: str = Field(default="", max_length=1000)
    features: List[str] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)

    # Quality assessment
    condition: ProductCondition = ProductCondition.GOOD
    condition_notes: Optional[str] = None

    # Confidence scores
    identification_confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    condition_confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ProductImage(BaseModel):
    image_url: Optional[str] = None
    image_data: Optional[str] = None  # base64 encoded
    image_quality_score: float = Field(ge=0.0, le=10.0, default=7.0)
    image_analysis: Dict[str, Any] = Field(default_factory=dict)

    # Image metadata
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[str] = None


class Product(BaseModel):
    id: Optional[str] = None
    identification: ProductIdentification
    images: List[ProductImage] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # User context
    user_id: Optional[str] = None
    acquisition_cost: Optional[float] = None
    acquisition_date: Optional[datetime] = None

    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }