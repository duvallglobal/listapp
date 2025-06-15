
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    FREE_TRIAL = "free_trial"
    BASIC = "basic" 
    PRO = "pro"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Preferences
    notifications_enabled: bool = True
    marketing_emails: bool = False
    default_condition: str = "good"
    preferred_marketplaces: list[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    default_condition: Optional[str] = None
    preferred_marketplaces: Optional[list[str]] = None

class UserSubscription(BaseModel):
    id: str
    user_id: str
    tier: SubscriptionTier
    status: SubscriptionStatus
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserUsage(BaseModel):
    user_id: str
    subscription_tier: SubscriptionTier
    analyses_used: int
    analyses_limit: int
    reset_date: datetime
    overage_analyses: int = 0
    
    @property
    def usage_percentage(self) -> float:
        if self.analyses_limit <= 0:
            return 0.0
        return min(100.0, (self.analyses_used / self.analyses_limit) * 100)
    
    @property
    def can_analyze(self) -> bool:
        return self.analyses_limit < 0 or self.analyses_used < self.analyses_limit

class UserStats(BaseModel):
    total_analyses: int
    total_estimated_value: float
    favorite_platforms: list[str]
    most_analyzed_category: Optional[str] = None
    average_confidence_score: Optional[float] = None
    join_date: datetime
    last_analysis_date: Optional[datetime] = None

class UserNotificationSettings(BaseModel):
    email_analysis_complete: bool = True
    email_weekly_summary: bool = True
    email_marketing: bool = False
    push_analysis_complete: bool = True
    push_price_alerts: bool = True
    sms_enabled: bool = False
