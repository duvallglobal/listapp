
from functools import lru_cache
from typing import Optional, AsyncGenerator
import redis.asyncio as redis
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

from .config import settings, get_settings

# Security
security = HTTPBearer()

# Supabase client
@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# Redis client
async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis client instance"""
    redis_client = redis.from_url(
        settings.REDIS_URL,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
    try:
        yield redis_client
    finally:
        await redis_client.close()

# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
):
    """Get current authenticated user"""
    try:
        # Verify JWT token with Supabase
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        return user.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase_client)
):
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user.user if user else None
    except Exception:
        return None

# Rate limiting dependency
class RateLimiter:
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
    
    async def __call__(
        self,
        request,
        redis_client: redis.Redis = Depends(get_redis_client)
    ):
        """Rate limiting implementation"""
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        current = await redis_client.get(key)
        if current is None:
            await redis_client.setex(key, self.period, 1)
            return True
        
        if int(current) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        await redis_client.incr(key)
        return True

# Create rate limiter instances
rate_limit_per_minute = RateLimiter(calls=60, period=60)
rate_limit_per_hour = RateLimiter(calls=1000, period=3600)

# Subscription validation
async def require_subscription(
    user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """Ensure user has active subscription"""
    try:
        result = supabase.table("subscriptions").select("*").eq("user_id", user.id).eq("status", "active").execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Active subscription required"
            )
        
        return result.data[0]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not verify subscription status"
        )
