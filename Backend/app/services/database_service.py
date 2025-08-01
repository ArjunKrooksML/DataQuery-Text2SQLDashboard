import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.query_history import QueryHistory, QueryType
from app.schemas.query import QueryResponse


class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def execute_sql_query(self, query: str, user_id: Optional[int] = None) -> QueryResponse:
        """Execute SQL query and return results"""
        start_time = time.time()
        
        try:
            # Execute the query
            result = self.db.execute(text(query))
            
            # Get column names
            columns = result.keys()
            
            # Fetch all rows
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log the query
            self._log_query(query, QueryType.SQL, execution_time, user_id)
            
            return QueryResponse(
                success=True,
                data=data,
                columns=list(columns),
                row_count=len(data),
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log the failed query
            self._log_query(query, QueryType.SQL, execution_time, user_id, str(e))
            
            return QueryResponse(
                success=False,
                message=str(e),
                execution_time_ms=execution_time
            )
    
    def get_database_schema(self) -> List[Dict[str, Any]]:
        """Get database schema information"""
        schema_query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
        """
        
        result = self.db.execute(text(schema_query))
        return [dict(row) for row in result.fetchall()]
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            result = self.db.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception:
            return []
    
    def _log_query(self, query: str, query_type: QueryType, execution_time: int, 
                   user_id: Optional[int] = None, error_message: Optional[str] = None):
        """Log query execution"""
        # Note: This method needs to be updated for multi-tenant architecture
        # For now, we'll skip logging since we need connection_id
        pass 