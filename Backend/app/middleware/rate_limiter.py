"""
Rate limiting middleware using MongoDB for tracking request limits.
"""

import time
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.database.mongodb import rate_limit_store
from app.core.config import settings


class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(self):
        self.rate_limit_store = rate_limit_store
    
    def get_window_start(self, window_seconds: int = None) -> int:
        """Get the start of the current time window"""
        if window_seconds is None:
            window_seconds = settings.RATE_LIMIT_WINDOW
        
        current_time = int(time.time())
        return (current_time // window_seconds) * window_seconds
    
    async def check_rate_limit(self, user_id: str, window_seconds: int = None) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            window_start = self.get_window_start(window_seconds)
            current_count = await self.rate_limit_store.get_request_count(user_id, window_start)
            
            return current_count < settings.RATE_LIMIT_REQUESTS
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True  # Allow request if rate limiting fails
    
    async def increment_request_count(self, user_id: str, window_seconds: int = None) -> int:
        """Increment request count for user"""
        try:
            window_start = self.get_window_start(window_seconds)
            current_count = await self.rate_limit_store.increment_request_count(user_id, window_start)
            
            return current_count
            
        except Exception as e:
            print(f"Error incrementing request count: {e}")
            return 0
    
    async def cleanup_old_windows(self, window_seconds: int = None) -> int:
        """Clean up old rate limit windows"""
        try:
            current_window = self.get_window_start(window_seconds)
            count = await self.rate_limit_store.cleanup_old_windows(current_window)
            return count
            
        except Exception as e:
            print(f"Error cleaning up rate limit windows: {e}")
            return 0


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware function"""
    
    # Skip rate limiting for certain endpoints
    if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register", "/health"]:
        response = await call_next(request)
        return response
    
    # Get user ID from request (assuming it's in headers or query params)
    user_id = None
    
    # Try to get user ID from authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        # In a real implementation, you would decode the JWT token here
        # For now, we'll use a simple approach
        user_id = "user_from_token"  # This should be extracted from JWT
    
    # If no user ID found, use IP address as fallback
    if not user_id:
        user_id = request.client.host
    
    # Check rate limit
    is_allowed = await rate_limiter.check_rate_limit(user_id)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": settings.RATE_LIMIT_WINDOW
            }
        )
    
    # Increment request count
    current_count = await rate_limiter.increment_request_count(user_id)
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(settings.RATE_LIMIT_REQUESTS - current_count)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + settings.RATE_LIMIT_WINDOW)
    
    return response


def get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request"""
    # This is a simplified version - in production, you'd decode JWT tokens
    auth_header = request.headers.get("Authorization")
    
    if auth_header and auth_header.startswith("Bearer "):
        # In a real implementation, decode JWT and extract user_id
        # For now, return a placeholder
        return "user_from_token"
    
    return None 