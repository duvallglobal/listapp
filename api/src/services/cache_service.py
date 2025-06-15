import json
import asyncio
from typing import Dict, Any, Optional
import redis.asyncio as redis
from datetime import datetime, timedelta

class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def set_analysis(self, task_id: str, data: Dict[str, Any], expire_seconds: int = 3600):
        """Store analysis data in cache"""
        try:
            # Add timestamp
            data["last_updated"] = datetime.utcnow().isoformat()

            # Store as JSON
            await self.redis.setex(
                f"analysis:{task_id}",
                expire_seconds,
                json.dumps(data, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def get_analysis(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis data from cache"""
        try:
            data = await self.redis.get(f"analysis:{task_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def delete_analysis(self, task_id: str) -> bool:
        """Delete analysis data from cache"""
        try:
            result = await self.redis.delete(f"analysis:{task_id}")
            return result > 0
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def set_user_cache(self, user_id: str, key: str, data: Any, expire_seconds: int = 1800):
        """Set user-specific cache data"""
        try:
            await self.redis.setex(
                f"user:{user_id}:{key}",
                expire_seconds,
                json.dumps(data, default=str)
            )
            return True
        except Exception as e:
            print(f"User cache set error: {e}")
            return False

    async def get_user_cache(self, user_id: str, key: str) -> Optional[Any]:
        """Get user-specific cache data"""
        try:
            data = await self.redis.get(f"user:{user_id}:{key}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"User cache get error: {e}")
            return None