"""
MongoDB Service for DataWise Dashboard
Handles sessions, caching, rate limiting, user activity logs, and latency monitoring
"""

import hashlib
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings


class MongoDBService:
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:

            sync_client = MongoClient(settings.MONGODB_URL)
            self.db = sync_client[settings.MONGODB_DATABASE]
            

            self.db.command('ping')
            print("MongoDB connected successfully")
            
        except Exception as e:
            print(f"WARNING: MongoDB not available: {e}")
            self.db = None
    
    def is_available(self) -> bool:
        """Check if MongoDB is available"""
        return self.db is not None
    

    def create_session(self, user_id: str, session_data: Dict[str, Any]) -> str:
        """Create a new user session"""
        if not self.is_available():
            print(f"WARNING: MongoDB not available for session creation")
            return None
        
        print(f"Creating session for user: {user_id}")
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES)
        
        session_doc = {
            "session_id": session_id,
            "user_id": user_id,
            "data": session_data,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_accessed": datetime.utcnow()
        }
        
        print(f"Inserting session document: {session_id}")
        try:
            result = self.db.sessions.insert_one(session_doc)
            print(f"Session created successfully: {session_id}, MongoDB ID: {result.inserted_id}")
            return session_id
        except Exception as e:
            print(f"ERROR: Failed to create session: {str(e)}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        if not self.is_available():
            print(f"WARNING: MongoDB not available for session lookup: {session_id}")
            return None
        
        print(f"Looking up session in MongoDB: {session_id}")
        

        all_sessions = list(self.db.sessions.find({}, {"session_id": 1, "user_id": 1}))
        print(f"Total sessions in database: {len(all_sessions)}")
        if all_sessions:
            print(f"Existing session IDs: {[s.get('session_id') for s in all_sessions]}")
        
        session = self.db.sessions.find_one({
            "session_id": session_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if session:
            print(f"Session found: {session_id}")

            self.db.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"last_accessed": datetime.utcnow()}}
            )
            return session["data"]
        else:
            print(f"Session not found or expired: {session_id}")
        
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if not self.is_available():
            return False
        
        result = self.db.sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user"""
        if not self.is_available():
            return 0
        
        result = self.db.sessions.delete_many({"user_id": user_id})
        return result.deleted_count
    

    def cache_query_result(self, query: str, result: Dict[str, Any], tenant_id: str, 
                          execution_time: int) -> bool:
        """Cache a query result"""
        if not self.is_available():
            return False
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.CACHE_EXPIRE_MINUTES)
        
        cache_doc = {
            "query_hash": query_hash,
            "query": query,
            "result": result,
            "tenant_id": tenant_id,
            "execution_time": execution_time,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at
        }
        

        self.db.query_cache.replace_one(
            {"query_hash": query_hash, "tenant_id": tenant_id},
            cache_doc,
            upsert=True
        )
        return True
    
    def get_cached_query(self, query: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get cached query result"""
        if not self.is_available():
            return None
        
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        cached = self.db.query_cache.find_one({
            "query_hash": query_hash,
            "tenant_id": tenant_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return cached["result"] if cached else None
    
    def clear_query_cache(self, tenant_id: str = None) -> int:
        """Clear query cache for a tenant or all"""
        if not self.is_available():
            return 0
        
        filter_query = {"tenant_id": tenant_id} if tenant_id else {}
        result = self.db.query_cache.delete_many(filter_query)
        return result.deleted_count
    

    def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit"""
        if not self.is_available():
            return True  # Allow if MongoDB not available
        
        window_start = datetime.utcnow() - timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        request_count = self.db.rate_limits.count_documents({
            "user_id": user_id,
            "endpoint": endpoint,
            "timestamp": {"$gte": window_start}
        })
        
        return request_count < settings.RATE_LIMIT_REQUESTS
    
    def get_rate_limit_status(self, user_id: str, endpoint: str) -> dict:
        """Get current rate limit status for user and endpoint"""
        if not self.is_available():
            return {
                "allowed": True,
                "current_count": 0,
                "limit": settings.RATE_LIMIT_REQUESTS,
                "window_seconds": settings.RATE_LIMIT_WINDOW,
                "remaining": settings.RATE_LIMIT_REQUESTS,
                "reset_time": None
            }
        
        window_start = datetime.utcnow() - timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        request_count = self.db.rate_limits.count_documents({
            "user_id": user_id,
            "endpoint": endpoint,
            "timestamp": {"$gte": window_start}
        })
        
        remaining = max(0, settings.RATE_LIMIT_REQUESTS - request_count)
        reset_time = datetime.utcnow() + timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        return {
            "allowed": request_count < settings.RATE_LIMIT_REQUESTS,
            "current_count": request_count,
            "limit": settings.RATE_LIMIT_REQUESTS,
            "window_seconds": settings.RATE_LIMIT_WINDOW,
            "remaining": remaining,
            "reset_time": reset_time.isoformat()
        }
    
    def record_request(self, user_id: str, endpoint: str) -> None:
        """Record a request for rate limiting"""
        if not self.is_available():
            return
        
        expires_at = datetime.utcnow() + timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        
        self.db.rate_limits.insert_one({
            "user_id": user_id,
            "endpoint": endpoint,
            "timestamp": datetime.utcnow(),
            "expires_at": expires_at
        })
    

    def record_request_latency(self, user_id: str, endpoint: str, method: str, 
                             latency_ms: float, status_code: int, 
                             request_size: int = 0, response_size: int = 0,
                             tenant_id: str = None, error_message: str = None) -> None:
        """Record request latency and performance metrics"""
        if not self.is_available():
            return
        
        latency_doc = {
            "user_id": user_id,
            "endpoint": endpoint,
            "method": method,
            "latency_ms": latency_ms,
            "status_code": status_code,
            "request_size": request_size,
            "response_size": response_size,
            "tenant_id": tenant_id,
            "error_message": error_message,
            "timestamp": datetime.utcnow(),
            "hour": datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        }
        
        self.db.request_latency.insert_one(latency_doc)
    
    def get_latency_stats(self, tenant_id: str = None, days: int = 7, 
                         endpoint: str = None) -> Dict[str, Any]:
        """Get latency statistics for monitoring"""
        if not self.is_available():
            return {}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        

        filter_query = {"timestamp": {"$gte": start_date}}
        if tenant_id:
            filter_query["tenant_id"] = tenant_id
        if endpoint:
            filter_query["endpoint"] = endpoint
        

        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": None,
                "avg_latency": {"$avg": "$latency_ms"},
                "min_latency": {"$min": "$latency_ms"},
                "max_latency": {"$max": "$latency_ms"},
                "p95_latency": {"$percentile": {"input": "$latency_ms", "p": 95}},
                "p99_latency": {"$percentile": {"input": "$latency_ms", "p": 99}},
                "total_requests": {"$sum": 1},
                "error_count": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}},
                "avg_request_size": {"$avg": "$request_size"},
                "avg_response_size": {"$avg": "$response_size"}
            }}
        ]
        
        result = list(self.db.request_latency.aggregate(pipeline))
        
        if result:
            stats = result[0]
            stats["error_rate"] = (stats["error_count"] / stats["total_requests"]) * 100
            stats["period_days"] = days
            return stats
        
        return {
            "avg_latency": 0,
            "min_latency": 0,
            "max_latency": 0,
            "p95_latency": 0,
            "p99_latency": 0,
            "total_requests": 0,
            "error_count": 0,
            "error_rate": 0,
            "avg_request_size": 0,
            "avg_response_size": 0,
            "period_days": days
        }
    
    def get_latency_by_endpoint(self, tenant_id: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get latency statistics grouped by endpoint"""
        if not self.is_available():
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        filter_query = {"timestamp": {"$gte": start_date}}
        if tenant_id:
            filter_query["tenant_id"] = tenant_id
        
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": "$endpoint",
                "avg_latency": {"$avg": "$latency_ms"},
                "min_latency": {"$min": "$latency_ms"},
                "max_latency": {"$max": "$latency_ms"},
                "total_requests": {"$sum": 1},
                "error_count": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}}
            }},
            {"$sort": {"avg_latency": -1}}
        ]
        
        return list(self.db.request_latency.aggregate(pipeline))
    
    def get_latency_trends(self, tenant_id: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get latency trends over time (hourly)"""
        if not self.is_available():
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        filter_query = {"timestamp": {"$gte": start_date}}
        if tenant_id:
            filter_query["tenant_id"] = tenant_id
        
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": "$hour",
                "avg_latency": {"$avg": "$latency_ms"},
                "total_requests": {"$sum": 1},
                "error_count": {"$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        return list(self.db.request_latency.aggregate(pipeline))
    
    def get_slow_queries(self, tenant_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest queries for performance analysis"""
        if not self.is_available():
            return []
        
        filter_query = {}
        if tenant_id:
            filter_query["tenant_id"] = tenant_id
        
        cursor = self.db.request_latency.find(filter_query).sort("latency_ms", -1).limit(limit)
        
        return list(cursor)
    
    def get_error_patterns(self, tenant_id: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get error patterns for debugging"""
        if not self.is_available():
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        filter_query = {
            "timestamp": {"$gte": start_date},
            "status_code": {"$gte": 400}
        }
        if tenant_id:
            filter_query["tenant_id"] = tenant_id
        
        pipeline = [
            {"$match": filter_query},
            {"$group": {
                "_id": {"endpoint": "$endpoint", "status_code": "$status_code"},
                "count": {"$sum": 1},
                "avg_latency": {"$avg": "$latency_ms"},
                "error_messages": {"$addToSet": "$error_message"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        return list(self.db.request_latency.aggregate(pipeline))
    

    def log_user_activity(self, user_id: str, action: str, details: Dict[str, Any] = None) -> None:
        """Log user activity"""
        if not self.is_available():
            return
        
        log_doc = {
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow(),
            "ip_address": details.get("ip_address") if details else None
        }
        
        self.db.user_activity_logs.insert_one(log_doc)
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity logs"""
        if not self.is_available():
            return []
        
        cursor = self.db.user_activity_logs.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)
        
        return list(cursor)
    

    def store_embedding(self, embedding_type: str, data: Dict[str, Any], 
                       tenant_id: str, embedding_vector: List[float] = None) -> str:
        """Store vector embedding"""
        if not self.is_available():
            return None
        
        embedding_id = str(uuid.uuid4())
        
        embedding_doc = {
            "embedding_id": embedding_id,
            "embedding_type": embedding_type,  # schema, query, etc.
            "data": data,
            "tenant_id": tenant_id,
            "embedding_vector": embedding_vector,
            "created_at": datetime.utcnow()
        }
        
        self.db.vector_embeddings.insert_one(embedding_doc)
        return embedding_id
    
    def get_embeddings(self, embedding_type: str, tenant_id: str, 
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Get embeddings by type and tenant"""
        if not self.is_available():
            return []
        
        cursor = self.db.vector_embeddings.find({
            "embedding_type": embedding_type,
            "tenant_id": tenant_id
        }).sort("created_at", -1).limit(limit)
        
        return list(cursor)
    

    def get_usage_stats(self, tenant_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.is_available():
            return {}
        
        start_date = datetime.utcnow() - timedelta(days=days)
        

        query_filter = {"created_at": {"$gte": start_date}}
        if tenant_id:
            query_filter["tenant_id"] = tenant_id
        
        total_queries = self.db.query_cache.count_documents(query_filter)
        

        session_filter = {"created_at": {"$gte": start_date}}
        if tenant_id:
            session_filter["user_id"] = {"$regex": f"^{tenant_id}"}
        
        total_sessions = self.db.sessions.count_documents(session_filter)
        

        activity_filter = {"timestamp": {"$gte": start_date}}
        if tenant_id:
            activity_filter["user_id"] = {"$regex": f"^{tenant_id}"}
        
        total_activities = self.db.user_activity_logs.count_documents(activity_filter)
        

        latency_stats = self.get_latency_stats(tenant_id, days)
        
        return {
            "total_queries": total_queries,
            "total_sessions": total_sessions,
            "total_activities": total_activities,
            "latency_stats": latency_stats,
            "period_days": days
        }



mongodb_service = MongoDBService() 