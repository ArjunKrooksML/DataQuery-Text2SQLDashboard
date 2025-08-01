from fastapi import APIRouter
from app.api.v1.endpoints import queries, auth, connections

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(connections.router, prefix="/connections", tags=["database-connections"]) 