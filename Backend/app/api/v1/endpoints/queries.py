from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.multi_tenant_query_service import MultiTenantQueryService
from app.services.llm_service import LLMService
from app.schemas.query import (
    QueryRequest, QueryResponse, LLMQueryRequest, 
    LLMQueryResponse, QueryLogResponse
)
from app.api.deps import get_current_active_user
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/sql", response_model=QueryResponse)
def execute_sql_query(
    query_request: QueryRequest,
    connection_id: uuid.UUID = Query(..., description="Database connection ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Execute SQL query on a specific client database"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query_service = MultiTenantQueryService(db)
    
    return query_service.execute_sql_query(
        query_request.query, 
        current_user.id, 
        connection_id
    )


@router.post("/llm", response_model=LLMQueryResponse)
def execute_llm_query(
    llm_request: LLMQueryRequest,
    connection_id: uuid.UUID = Query(..., description="Database connection ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Execute LLM query with database context"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    llm_service = LLMService(db)
    
    return llm_service.process_llm_query(llm_request.prompt, current_user.id, connection_id)


@router.get("/logs", response_model=List[QueryLogResponse])
def get_query_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get query logs"""
    query_service = MultiTenantQueryService(db)
    user_id = current_user.id if current_user else None
    
    return query_service.get_query_logs(limit, user_id)


@router.get("/schema")
def get_database_schema(
    connection_id: uuid.UUID = Query(..., description="Database connection ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get database schema from a specific client database"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query_service = MultiTenantQueryService(db)
    return query_service.get_database_schema(current_user.id, connection_id)


@router.get("/sample-data/{table_name}")
def get_sample_data(
    table_name: str,
    connection_id: uuid.UUID = Query(..., description="Database connection ID"),
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Get sample data from a specific client database table"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query_service = MultiTenantQueryService(db)
    return query_service.get_sample_data(current_user.id, connection_id, table_name, limit) 