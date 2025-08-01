"""
Cache service using MongoDB for query caching and performance optimization.
"""

import hashlib
import json
from typing import Optional, Dict, Any, List
from app.database.mongodb import cache_store
from app.core.config import settings


class CacheService:
    """Service for managing application cache"""
    
    def __init__(self):
        self.cache_store = cache_store
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key"""
        # Convert all arguments to a consistent string representation
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            key_parts.append(str(arg))
        
        # Add keyword arguments (sorted for consistency)
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Create hash of the key parts
        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def cache_query_result(self, user_id: str, connection_id: str, query: str, result: Any, expire_minutes: int = None) -> bool:
        """Cache a query result"""
        try:
            cache_key = self.generate_cache_key(
                "query_result",
                user_id,
                connection_id,
                query_hash=hashlib.sha256(query.encode()).hexdigest()
            )
            
            cache_data = {
                "user_id": user_id,
                "connection_id": connection_id,
                "query": query,
                "result": result,
                "cached_at": str(settings.CACHE_EXPIRE_MINUTES)
            }
            
            success = await self.cache_store.set_cache(cache_key, cache_data, expire_minutes)
            return success
            
        except Exception as e:
            print(f"Error caching query result: {e}")
            return False
    
    async def get_cached_query_result(self, user_id: str, connection_id: str, query: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        try:
            cache_key = self.generate_cache_key(
                "query_result",
                user_id,
                connection_id,
                query_hash=hashlib.sha256(query.encode()).hexdigest()
            )
            
            cached_data = await self.cache_store.get_cache(cache_key)
            return cached_data
            
        except Exception as e:
            print(f"Error getting cached query result: {e}")
            return None
    
    async def cache_schema(self, connection_id: str, schema: Dict[str, Any], expire_minutes: int = None) -> bool:
        """Cache database schema"""
        try:
            cache_key = self.generate_cache_key("schema", connection_id)
            
            cache_data = {
                "connection_id": connection_id,
                "schema": schema,
                "cached_at": str(settings.CACHE_EXPIRE_MINUTES)
            }
            
            success = await self.cache_store.set_cache(cache_key, cache_data, expire_minutes)
            return success
            
        except Exception as e:
            print(f"Error caching schema: {e}")
            return False
    
    async def get_cached_schema(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get cached schema"""
        try:
            cache_key = self.generate_cache_key("schema", connection_id)
            cached_data = await self.cache_store.get_cache(cache_key)
            return cached_data
            
        except Exception as e:
            print(f"Error getting cached schema: {e}")
            return None
    
    async def cache_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Cache user preferences"""
        try:
            cache_key = self.generate_cache_key("user_preferences", user_id)
            
            cache_data = {
                "user_id": user_id,
                "preferences": preferences,
                "cached_at": str(settings.CACHE_EXPIRE_MINUTES)
            }
            
            success = await self.cache_store.set_cache(cache_key, cache_data, 60)  # 1 hour
            return success
            
        except Exception as e:
            print(f"Error caching user preferences: {e}")
            return False
    
    async def get_cached_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user preferences"""
        try:
            cache_key = self.generate_cache_key("user_preferences", user_id)
            cached_data = await self.cache_store.get_cache(cache_key)
            return cached_data
            
        except Exception as e:
            print(f"Error getting cached user preferences: {e}")
            return None
    
    async def cache_llm_response(self, user_id: str, prompt: str, response: str, sql_generated: str = None) -> bool:
        """Cache LLM response"""
        try:
            cache_key = self.generate_cache_key(
                "llm_response",
                user_id,
                prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()
            )
            
            cache_data = {
                "user_id": user_id,
                "prompt": prompt,
                "response": response,
                "sql_generated": sql_generated,
                "cached_at": str(settings.CACHE_EXPIRE_MINUTES)
            }
            
            success = await self.cache_store.set_cache(cache_key, cache_data, 30)  # 30 minutes
            return success
            
        except Exception as e:
            print(f"Error caching LLM response: {e}")
            return False
    
    async def get_cached_llm_response(self, user_id: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Get cached LLM response"""
        try:
            cache_key = self.generate_cache_key(
                "llm_response",
                user_id,
                prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()
            )
            
            cached_data = await self.cache_store.get_cache(cache_key)
            return cached_data
            
        except Exception as e:
            print(f"Error getting cached LLM response: {e}")
            return None
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache for a user"""
        try:
            count = await self.cache_store.clear_user_cache(user_id)
            return count
            
        except Exception as e:
            print(f"Error invalidating user cache: {e}")
            return 0
    
    async def invalidate_connection_cache(self, connection_id: str) -> bool:
        """Invalidate cache for a specific connection"""
        try:
            cache_key = self.generate_cache_key("schema", connection_id)
            success = await self.cache_store.delete_cache(cache_key)
            return success
            
        except Exception as e:
            print(f"Error invalidating connection cache: {e}")
            return False
    
    async def get_cache_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # This would require additional methods in CacheStore
            # For now, return basic stats
            stats = {
                "total_cached_items": 0,
                "user_cached_items": 0,
                "cache_hit_rate": 0.0
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {}
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries"""
        try:
            count = await self.cache_store.cleanup_expired_cache()
            return count
            
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
            return 0


# Global cache service instance
cache_service = CacheService() 