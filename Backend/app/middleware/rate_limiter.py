"""
Rate limiting middleware using MongoDB for tracking request limits.
"""

import time
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.services.mongodb_service import mongodb_service
from app.core.config import settings
from app.utils.jwt_utils import get_rate_limit_identifier, get_user_info_from_request


class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(self):
        self.mongodb_service = mongodb_service
    
    def get_window_start(self, window_seconds: int = None) -> int:
        """Get the start of the current time window"""
        if window_seconds is None:
            window_seconds = settings.RATE_LIMIT_WINDOW
        
        current_time = int(time.time())
        return (current_time // window_seconds) * window_seconds
    
    def check_rate_limit(self, user_id: str, endpoint: str) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            return self.mongodb_service.check_rate_limit(user_id, endpoint)
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True  # Allow request if rate limiting fails
    
    def record_request(self, user_id: str, endpoint: str) -> None:
        """Record a request for rate limiting"""
        try:
            self.mongodb_service.record_request(user_id, endpoint)
            
        except Exception as e:
            print(f"Error recording request: {e}")


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware function"""
    
    # Skip rate limiting for certain endpoints
    if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register", "/health"]:
        response = await call_next(request)
        return response
    
    # Get unique identifier for rate limiting (user ID or IP)
    rate_limit_id = get_rate_limit_identifier(request)
    
    # Get user info for better logging and headers
    user_info = get_user_info_from_request(request)
    
    # Get endpoint for rate limiting
    endpoint = request.url.path
    
    # Check rate limit and get status
    rate_status = rate_limiter.mongodb_service.get_rate_limit_status(rate_limit_id, endpoint)
    
    if not rate_status["allowed"]:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": settings.RATE_LIMIT_WINDOW,
                "current_count": rate_status["current_count"],
                "limit": rate_status["limit"],
                "remaining": rate_status["remaining"],
                "reset_time": rate_status["reset_time"]
            },
            headers={
                "X-RateLimit-Limit": str(rate_status["limit"]),
                "X-RateLimit-Remaining": str(rate_status["remaining"]),
                "X-RateLimit-Reset": rate_status["reset_time"],
                "Retry-After": str(settings.RATE_LIMIT_WINDOW)
            }
        )
    
    # Record request
    rate_limiter.record_request(rate_limit_id, endpoint)
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    # Add comprehensive rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_status["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rate_status["remaining"])
    response.headers["X-RateLimit-Window"] = str(settings.RATE_LIMIT_WINDOW)
    response.headers["X-RateLimit-Reset"] = rate_status["reset_time"]
    
    # Add user identification in headers (for debugging)
    if user_info["authenticated"]:
        response.headers["X-RateLimit-User"] = f"user:{user_info['user_id']}"
    else:
        response.headers["X-RateLimit-User"] = rate_limit_id
    
    return response


 