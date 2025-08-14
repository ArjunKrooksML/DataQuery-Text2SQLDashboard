"""
Monitoring API endpoints for latency statistics and performance metrics
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_current_active_user
from app.models.user import User
from app.middleware.latency_monitor import (
    get_latency_stats,
    get_latency_by_endpoint,
    get_latency_trends,
    get_slow_queries,
    get_error_patterns
)
from app.services.mongodb_service import mongodb_service

router = APIRouter()


@router.get("/latency/stats")
async def get_latency_statistics(
    days: int = Query(7, description="Number of days to analyze"),
    endpoint: Optional[str] = Query(None, description="Filter by specific endpoint"),
    current_user: User = Depends(get_current_active_user)
):
    """Get overall latency statistics"""
    try:
        tenant_id = str(current_user.id)
        stats = get_latency_stats(tenant_id, days)
        
        if endpoint:
            # Filter by specific endpoint
            endpoint_stats = get_latency_stats(tenant_id, days, endpoint)
            return {
                "endpoint": endpoint,
                "stats": endpoint_stats,
                "period_days": days
            }
        
        return {
            "overall_stats": stats,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving latency stats: {str(e)}")


@router.get("/latency/endpoints")
async def get_latency_by_endpoints(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get latency statistics grouped by endpoint"""
    try:
        tenant_id = str(current_user.id)
        endpoint_stats = get_latency_by_endpoint(tenant_id, days)
        
        return {
            "endpoint_stats": endpoint_stats,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving endpoint stats: {str(e)}")


@router.get("/latency/trends")
async def get_latency_trends(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get latency trends over time"""
    try:
        tenant_id = str(current_user.id)
        trends = get_latency_trends(tenant_id, days)
        
        return {
            "trends": trends,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving latency trends: {str(e)}")


@router.get("/latency/slow-queries")
async def get_slow_queries(
    limit: int = Query(10, description="Number of slow queries to return"),
    current_user: User = Depends(get_current_active_user)
):
    """Get the slowest queries for performance analysis"""
    try:
        tenant_id = str(current_user.id)
        slow_queries = get_slow_queries(tenant_id, limit)
        
        return {
            "slow_queries": slow_queries,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving slow queries: {str(e)}")


@router.get("/latency/errors")
async def get_error_patterns(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get error patterns for debugging"""
    try:
        tenant_id = str(current_user.id)
        error_patterns = get_error_patterns(tenant_id, days)
        
        return {
            "error_patterns": error_patterns,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving error patterns: {str(e)}")


@router.get("/usage/stats")
async def get_usage_statistics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive usage statistics"""
    try:
        tenant_id = str(current_user.id)
        usage_stats = mongodb_service.get_usage_stats(tenant_id, days)
        
        return {
            "usage_stats": usage_stats,
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving usage stats: {str(e)}")


@router.get("/performance/summary")
async def get_performance_summary(
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a comprehensive performance summary"""
    try:
        tenant_id = str(current_user.id)
        
        # Get various performance metrics
        latency_stats = get_latency_stats(tenant_id, days)
        endpoint_stats = get_latency_by_endpoint(tenant_id, days)
        slow_queries = get_slow_queries(tenant_id, 5)
        error_patterns = get_error_patterns(tenant_id, days)
        usage_stats = mongodb_service.get_usage_stats(tenant_id, days)
        
        # Calculate performance score (0-100)
        performance_score = 100
        
        # Deduct points for high latency
        if latency_stats.get("avg_latency", 0) > 1000:  # > 1 second
            performance_score -= 20
        elif latency_stats.get("avg_latency", 0) > 500:  # > 500ms
            performance_score -= 10
        
        # Deduct points for high error rate
        if latency_stats.get("error_rate", 0) > 5:  # > 5% errors
            performance_score -= 30
        elif latency_stats.get("error_rate", 0) > 1:  # > 1% errors
            performance_score -= 15
        
        # Deduct points for slow queries
        if slow_queries and len(slow_queries) > 0:
            performance_score -= 10
        
        performance_score = max(0, performance_score)
        
        return {
            "performance_summary": {
                "performance_score": performance_score,
                "latency_overview": {
                    "average_latency_ms": latency_stats.get("avg_latency", 0),
                    "p95_latency_ms": latency_stats.get("p95_latency", 0),
                    "p99_latency_ms": latency_stats.get("p99_latency", 0)
                },
                "error_overview": {
                    "error_rate_percent": latency_stats.get("error_rate", 0),
                    "total_errors": latency_stats.get("error_count", 0)
                },
                "usage_overview": {
                    "total_requests": latency_stats.get("total_requests", 0),
                    "total_queries": usage_stats.get("total_queries", 0),
                    "total_sessions": usage_stats.get("total_sessions", 0)
                },
                "top_slow_endpoints": endpoint_stats[:3] if endpoint_stats else [],
                "recent_errors": error_patterns[:3] if error_patterns else []
            },
            "period_days": days
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance summary: {str(e)}") 