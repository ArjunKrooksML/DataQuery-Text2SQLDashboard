"""
MongoDB connection and database setup for session storage and caching.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta


class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.sync_client: Optional[MongoClient] = None
        self.database = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.sync_client = MongoClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
        if self.sync_client:
            self.sync_client.close()
    
    def get_database(self):
        """Get MongoDB database instance"""
        return self.database


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


class SessionStore:
    """Session storage using MongoDB"""
    
    def __init__(self):
        self.collection = mongodb_manager.database.sessions
    
    async def create_session(self, session_id: str, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Create a new session"""
        try:
            expires_at = datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
            
            session_doc = {
                "session_id": session_id,
                "user_id": user_id,
                "session_data": session_data,
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self.collection.insert_one(session_doc)
            return True
            
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            session = await self.collection.find_one({
                "session_id": session_id,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if session:
                # Update last accessed
                await self.collection.update_one(
                    {"session_id": session_id},
                    {"$set": {"updated_at": datetime.utcnow()}}
                )
                return session
            
            return None
            
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            result = await self.collection.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "session_data": session_data,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        try:
            result = await self.collection.delete_one({"session_id": session_id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            cursor = self.collection.find({
                "user_id": user_id,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            sessions = await cursor.to_list(length=None)
            return sessions
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            return result.deleted_count
            
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0


class CacheStore:
    """Cache storage using MongoDB"""
    
    def __init__(self):
        self.collection = mongodb_manager.database.cache
    
    async def set_cache(self, key: str, value: Any, expire_minutes: int = None) -> bool:
        """Set cache value"""
        try:
            if expire_minutes is None:
                expire_minutes = settings.CACHE_EXPIRE_MINUTES
                
            expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)
            
            cache_doc = {
                "key": key,
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            }
            
            # Use upsert to handle existing keys
            await self.collection.replace_one(
                {"key": key},
                cache_doc,
                upsert=True
            )
            return True
            
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value"""
        try:
            cache_doc = await self.collection.find_one({
                "key": key,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if cache_doc:
                return cache_doc["value"]
            
            return None
            
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        try:
            result = await self.collection.delete_one({"key": key})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
    
    async def clear_user_cache(self, user_id: str) -> int:
        """Clear all cache for a user"""
        try:
            result = await self.collection.delete_many({
                "key": {"$regex": f"^user:{user_id}:"}
            })
            return result.deleted_count
            
        except Exception as e:
            print(f"Error clearing user cache: {e}")
            return 0
    
    async def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries"""
        try:
            result = await self.collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            return result.deleted_count
            
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
            return 0


class RateLimitStore:
    """Rate limiting storage using MongoDB"""
    
    def __init__(self):
        self.collection = mongodb_manager.database.rate_limits
    
    async def increment_request_count(self, user_id: str, window_start: int) -> int:
        """Increment request count for rate limiting"""
        try:
            result = await self.collection.update_one(
                {
                    "user_id": user_id,
                    "time_window": window_start
                },
                {
                    "$inc": {"request_count": 1},
                    "$setOnInsert": {
                        "window_start": window_start,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Get current count
            doc = await self.collection.find_one({
                "user_id": user_id,
                "time_window": window_start
            })
            
            return doc["request_count"] if doc else 1
            
        except Exception as e:
            print(f"Error incrementing request count: {e}")
            return 0
    
    async def get_request_count(self, user_id: str, window_start: int) -> int:
        """Get current request count"""
        try:
            doc = await self.collection.find_one({
                "user_id": user_id,
                "time_window": window_start
            })
            
            return doc["request_count"] if doc else 0
            
        except Exception as e:
            print(f"Error getting request count: {e}")
            return 0
    
    async def cleanup_old_windows(self, current_window: int) -> int:
        """Clean up old rate limit windows"""
        try:
            result = await self.collection.delete_many({
                "time_window": {"$lt": current_window}
            })
            return result.deleted_count
            
        except Exception as e:
            print(f"Error cleaning up rate limits: {e}")
            return 0


# Global instances - create them lazily to handle MongoDB unavailability
_session_store = None
_cache_store = None
_rate_limit_store = None

def get_session_store():
    global _session_store
    if _session_store is None:
        if mongodb_manager.database is not None:
            _session_store = SessionStore()
        else:
            # Create a mock session store that does nothing
            class MockSessionStore:
                async def create_session(self, *args, **kwargs): return True
                async def get_session(self, *args, **kwargs): return None
                async def update_session(self, *args, **kwargs): return True
                async def delete_session(self, *args, **kwargs): return True
                async def get_user_sessions(self, *args, **kwargs): return []
                async def cleanup_expired_sessions(self, *args, **kwargs): return 0
            _session_store = MockSessionStore()
    return _session_store

def get_cache_store():
    global _cache_store
    if _cache_store is None:
        if mongodb_manager.database is not None:
            _cache_store = CacheStore()
        else:
            # Create a mock cache store that does nothing
            class MockCacheStore:
                async def set_cache(self, *args, **kwargs): return True
                async def get_cache(self, *args, **kwargs): return None
                async def delete_cache(self, *args, **kwargs): return True
                async def clear_user_cache(self, *args, **kwargs): return 0
                async def cleanup_expired_cache(self, *args, **kwargs): return 0
            _cache_store = MockCacheStore()
    return _cache_store

def get_rate_limit_store():
    global _rate_limit_store
    if _rate_limit_store is None:
        if mongodb_manager.database is not None:
            _rate_limit_store = RateLimitStore()
        else:
            # Create a mock rate limit store that does nothing
            class MockRateLimitStore:
                async def increment_request_count(self, *args, **kwargs): return 0
                async def get_request_count(self, *args, **kwargs): return 0
                async def cleanup_old_windows(self, *args, **kwargs): return 0
            _rate_limit_store = MockRateLimitStore()
    return _rate_limit_store 