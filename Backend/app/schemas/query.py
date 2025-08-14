from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime
from app.models.query_history import QueryType


class QueryRequest(BaseModel):
    query: str
    query_type: QueryType
    user_id: Optional[int] = None


class QueryResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    columns: Optional[List[str]] = None
    row_count: Optional[int] = None


class QueryLogResponse(BaseModel):
    id: str
    query_type: str
    query_text: str
    status: str
    execution_time_ms: Optional[int]
    created_at: datetime
    user_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class LLMQueryRequest(BaseModel):
    prompt: str
    include_schema: bool = True
    include_sample_data: bool = True


class LLMQueryResponse(BaseModel):
    response: str
    sql_generated: Optional[str] = None
    confidence_score: Optional[float] = None
    execution_time_ms: Optional[int] = None 