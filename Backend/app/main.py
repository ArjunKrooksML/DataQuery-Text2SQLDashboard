from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api.v1.api import api_router
from app.core.config import settings
from app.services.mongodb_service import mongodb_service
from app.middleware.rate_limiter import rate_limit_middleware
from app.middleware.latency_monitor import latency_monitor_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(" Starting DataWise API...")
    
    # Check MongoDB availability
    if mongodb_service.is_available():
        print(" MongoDB connected successfully")
        print(" Session storage and caching enabled")
        print(" Rate limiting enabled")
        print(" Latency monitoring enabled")
    else:
        print("WARNING:  MongoDB not available - session storage and caching disabled")
        print("WARNING:  Rate limiting disabled (MongoDB not available)")
        print("WARNING:  Latency monitoring disabled (MongoDB not available)")
    
    yield
    
    # Shutdown
    print(" Shutting down DataWise API...")

# Create FastAPI app
app = FastAPI(
    title="DataWise API",
    description="AI-Powered SQL Dashboard API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add latency monitoring middleware (first, to capture all requests)
if mongodb_service.is_available():
    app.middleware("http")(latency_monitor_middleware)
    print(" Latency monitoring enabled")

# Add rate limiting middleware if MongoDB is available
if mongodb_service.is_available():
    app.middleware("http")(rate_limit_middleware)
    print(" Rate limiting enabled")
else:
    print("WARNING:  Rate limiting disabled (MongoDB not available)")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "DataWise API is running!",
        "version": "1.0.0",
        "features": {
            "mongodb": mongodb_service.is_available(),
            "rate_limiting": mongodb_service.is_available(),
            "session_storage": mongodb_service.is_available(),
            "query_caching": mongodb_service.is_available(),
            "latency_monitoring": mongodb_service.is_available()
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "mongodb": mongodb_service.is_available(),
        "services": {
            "sessions": mongodb_service.is_available(),
            "caching": mongodb_service.is_available(),
            "rate_limiting": mongodb_service.is_available(),
            "latency_monitoring": mongodb_service.is_available()
        }
    } 