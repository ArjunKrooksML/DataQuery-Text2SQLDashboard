"""
Latency monitoring middleware for tracking request performance
"""

import time
import json
from typing import Optional
from fastapi import Request, Response
from app.services.mongodb_service import mongodb_service
from app.api.deps import get_current_user


async def latency_monitor_middleware(request: Request, call_next):
    """Middleware to monitor request latency and performance"""
    
    # Record start time
    start_time = time.time()
    
    # Get request details
    endpoint = request.url.path
    method = request.method
    user_id = "anonymous"
    tenant_id = None
    request_size = 0
    response_size = 0
    error_message = None
    
    # Try to get user ID from JWT token
    try:
        user = await get_current_user(request)
        if user:
            user_id = str(user.id)
            tenant_id = str(user.id)  # For now, using user_id as tenant_id
    except:
        pass  # User not authenticated, use anonymous
    
    # Calculate request size
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            request_size = len(body)
    except:
        pass
    
    # Process the request
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Calculate response size
        try:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            response_size = len(response_body)
            
            # Recreate response with body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        except:
            pass
            
    except Exception as e:
        # Request failed
        status_code = 500
        error_message = str(e)
        response = Response(
            content=json.dumps({"error": "Internal server error"}),
            status_code=500,
            media_type="application/json"
        )
    
    # Calculate latency
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    
    # Record latency in MongoDB
    mongodb_service.record_request_latency(
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        latency_ms=latency_ms,
        status_code=status_code,
        request_size=request_size,
        response_size=response_size,
        tenant_id=tenant_id,
        error_message=error_message
    )
    
    # Add latency headers to response
    response.headers["X-Request-Latency"] = f"{latency_ms:.2f}ms"
    
    return response


def get_latency_stats(tenant_id: Optional[str] = None, days: int = 7):
    """Get latency statistics for monitoring dashboard"""
    return mongodb_service.get_latency_stats(tenant_id, days)


def get_latency_by_endpoint(tenant_id: Optional[str] = None, days: int = 7):
    """Get latency statistics grouped by endpoint"""
    return mongodb_service.get_latency_by_endpoint(tenant_id, days)


def get_latency_trends(tenant_id: Optional[str] = None, days: int = 7):
    """Get latency trends over time"""
    return mongodb_service.get_latency_trends(tenant_id, days)


def get_slow_queries(tenant_id: Optional[str] = None, limit: int = 10):
    """Get the slowest queries for performance analysis"""
    return mongodb_service.get_slow_queries(tenant_id, limit)


def get_error_patterns(tenant_id: Optional[str] = None, days: int = 7):
    """Get error patterns for debugging"""
    return mongodb_service.get_error_patterns(tenant_id, days) 