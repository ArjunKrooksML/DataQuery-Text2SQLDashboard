from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api.v1.api import api_router
from app.core.config import settings

# Optional imports for MongoDB and Redis
try:
    from app.database.mongodb import mongodb_manager
    from app.middleware.rate_limiter import rate_limit_middleware
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("⚠️  MongoDB not available - session storage and caching disabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting DataWise API...")
    
    # Connect to MongoDB if available
    if MONGODB_AVAILABLE and settings.MONGODB_URL:
        try:
            await mongodb_manager.connect()
            print("✅ Connected to MongoDB")
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
            print("   Continuing without MongoDB features...")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down DataWise API...")
    
    # Disconnect from MongoDB if available
    if MONGODB_AVAILABLE:
        try:
            await mongodb_manager.disconnect()
            print("✅ Disconnected from MongoDB")
        except Exception as e:
            print(f"⚠️  MongoDB disconnect error: {e}")

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

# Add rate limiting middleware if MongoDB is available
if MONGODB_AVAILABLE and settings.MONGODB_URL:
    app.middleware("http")(rate_limit_middleware)
    print("✅ Rate limiting enabled")
else:
    print("⚠️  Rate limiting disabled (MongoDB not available)")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "DataWise API is running!",
        "version": "1.0.0",
        "features": {
            "mongodb": MONGODB_AVAILABLE and bool(settings.MONGODB_URL),
            "rate_limiting": MONGODB_AVAILABLE and bool(settings.MONGODB_URL)
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mongodb": MONGODB_AVAILABLE and bool(settings.MONGODB_URL)} 