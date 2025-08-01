from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.query_history import QueryHistory, QueryType
from app.schemas.query import QueryLogResponse, QueryResponse, LLMQueryResponse
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService


class QueryService:
    def __init__(self, db: Session):
        self.db = db
        self.database_service = DatabaseService(db)
        self.llm_service = LLMService(db)
    
    def execute_sql_query(self, query: str, user_id: Optional[int] = None) -> QueryResponse:
        """Execute SQL query using database service"""
        return self.database_service.execute_sql_query(query, user_id)
    
    def execute_llm_query(self, prompt: str, user_id: Optional[int] = None) -> LLMQueryResponse:
        """Execute LLM query using LLM service"""
        return self.llm_service.process_llm_query(prompt, user_id)
    
    def get_query_logs(self, limit: int = 50, user_id: Optional[int] = None) -> List[QueryLogResponse]:
        """Get query logs with optional filtering"""
        query = self.db.query(QueryHistory)
        
        if user_id:
            query = query.filter(QueryHistory.user_id == user_id)
        
        logs = query.order_by(QueryHistory.created_at.desc()).limit(limit).all()
        
        return [QueryLogResponse.from_orm(log) for log in logs]
    
    def get_database_schema(self):
        """Get database schema information"""
        return self.database_service.get_database_schema()
    
    def get_sample_data(self, table_name: str, limit: int = 5):
        """Get sample data from a table"""
        return self.database_service.get_sample_data(table_name, limit) 