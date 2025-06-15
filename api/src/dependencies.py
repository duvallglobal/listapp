from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import redis.asyncio as redis
from supabase import create_client, Client
from typing import Optional
import jwt
from datetime import datetime, timedelta

from .config import settings

# Security
security = HTTPBearer()

# Redis client (singleton)
_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client

# Supabase client (singleton)
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    return _supabase_client

async def get_current_user(token: str = Depends(security)):
    """Get current authenticated user from JWT token"""
    try:
        # Extract token from Bearer format
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
        
        # Verify JWT token with Supabase
        supabase = get_supabase_client()
        
        # Get user from token
        user_response = supabase.auth.get_user(token_str)
        
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_response.user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(token: Optional[str] = Depends(security)):
    """Get current user if authenticated, otherwise return None"""
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

async def verify_user_credits(user_id: str, required_credits: int = 1) -> bool:
    """Verify user has enough credits for operation"""
    supabase = get_supabase_client()
    
    try:
        # Get user credits
        result = supabase.table("users").select("credits").eq("user_id", user_id).single().execute()
        
        if not result.data:
            return False
        
        current_credits = int(result.data.get("credits", 0))
        return current_credits >= required_credits
        
    except Exception as e:
        print(f"Error verifying credits: {e}")
        return False

async def deduct_user_credits(user_id: str, credits_to_deduct: int = 1) -> bool:
    """Deduct credits from user account"""
    supabase = get_supabase_client()
    
    try:
        # Get current credits
        result = supabase.table("users").select("credits").eq("user_id", user_id).single().execute()
        
        if not result.data:
            return False
        
        current_credits = int(result.data.get("credits", 0))
        
        if current_credits < credits_to_deduct:
            return False
        
        # Deduct credits
        new_credits = current_credits - credits_to_deduct
        
        update_result = supabase.table("users").update({
            "credits": str(new_credits)
        }).eq("user_id", user_id).execute()
        
        return True
        
    except Exception as e:
        print(f"Error deducting credits: {e}")
        return False

class RateLimiter:
    """Simple rate limiter using Redis"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
        try:
            current = await self.redis.get(key)
            
            if current is None:
                await self.redis.setex(key, window, 1)
                return True
            
            if int(current) >= limit:
                return False
            
            await self.redis.incr(key)
            return True
            
        except Exception as e:
            print(f"Rate limiter error: {e}")
            return True  # Allow on error

async def check_rate_limit(user_id: str):
    """Check rate limit for user"""
    redis_client = await get_redis_client()
    rate_limiter = RateLimiter(redis_client)
    
    # Check per-minute limit
    minute_key = f"rate_limit:minute:{user_id}:{datetime.now().strftime('%Y%m%d%H%M')}"
    if not await rate_limiter.is_allowed(minute_key, settings.RATE_LIMIT_PER_MINUTE, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per minute"
        )
    
    # Check per-hour limit
    hour_key = f"rate_limit:hour:{user_id}:{datetime.now().strftime('%Y%m%d%H')}"
    if not await rate_limiter.is_allowed(hour_key, settings.RATE_LIMIT_PER_HOUR, 3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per hour"
        )

async def get_user_subscription_tier(user_id: str) -> str:
    """Get user's subscription tier"""
    supabase = get_supabase_client()
    
    try:
        result = supabase.table("users").select("subscription").eq("user_id", user_id).single().execute()
        
        if result.data and result.data.get("subscription"):
            # Get subscription details
            sub_result = supabase.table("subscriptions").select("price_id, status").eq(
                "id", result.data["subscription"]
            ).single().execute()
            
            if sub_result.data and sub_result.data.get("status") == "active":
                price_id = sub_result.data.get("price_id", "")
                
                if "basic" in price_id.lower():
                    return "basic"
                elif "pro" in price_id.lower():
                    return "pro"
                elif "business" in price_id.lower():
                    return "business"
                elif "enterprise" in price_id.lower():
                    return "enterprise"
        
        return "free"
        
    except Exception as e:
        print(f"Error getting subscription tier: {e}")
        return "free"
