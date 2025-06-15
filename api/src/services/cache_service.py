
import redis
import json
import hashlib
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key"""
        return f"{prefix}:{identifier}"
    
    def _hash_data(self, data: Any) -> str:
        """Generate a hash for complex data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def store_analysis(self, analysis_result: Dict[str, Any], ttl: Optional[int] = None) -> str:
        """Store analysis result in cache"""
        cache_key = self._generate_key("analysis", self._hash_data(analysis_result))
        
        cache_data = {
            "result": analysis_result,
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": ttl or self.default_ttl
        }
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl,
            json.dumps(cache_data)
        )
        
        return cache_key
    
    def get_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis result from cache"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def store_product_data(self, product_id: str, product_data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Store product data"""
        cache_key = self._generate_key("product", product_id)
        
        cache_data = {
            "data": product_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl,
            json.dumps(cache_data)
        )
    
    def get_product_data(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve product data"""
        cache_key = self._generate_key("product", product_id)
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)["data"]
            return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def store_market_data(self, search_query: str, market_data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Store market research data"""
        query_hash = self._hash_data(search_query)
        cache_key = self._generate_key("market", query_hash)
        
        cache_data = {
            "query": search_query,
            "data": market_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.redis_client.setex(
            cache_key,
            ttl or (self.default_ttl * 2),  # Market data cached longer
            json.dumps(cache_data)
        )
    
    def get_market_data(self, search_query: str) -> Optional[Dict[str, Any]]:
        """Retrieve market research data"""
        query_hash = self._hash_data(search_query)
        cache_key = self._generate_key("market", query_hash)
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)["data"]
            return None
        except Exception as e:
            print(f"Cache retrieval error: {e}")
            return None
    
    def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
