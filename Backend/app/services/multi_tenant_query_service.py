"""
Multi-Tenant Query Service
Handles query execution on client databases with proper isolation.
"""

import time
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from app.models.query_history import QueryHistory, QueryType
from app.models.database_connection import DatabaseConnection
from app.schemas.query import QueryResponse
from app.services.database_connection_service import DatabaseConnectionService, AccessDeniedError


class MultiTenantQueryService:
    def __init__(self, db: Session):
        self.db = db
        self.connection_service = DatabaseConnectionService(db)
    
    def execute_sql_query(self, query: str, user_id: uuid.UUID, connection_id: uuid.UUID) -> QueryResponse:
        """Execute SQL query on a specific client database"""
        start_time = time.time()
        
        try:
            # Get client database connection
            client_engine = self.connection_service.get_client_connection(user_id, connection_id)
            
            # Execute query on client database
            with client_engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Get column names
                columns = result.keys()
                
                # Fetch all rows
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                data = [dict(zip(columns, row)) for row in rows]
                
                execution_time = int((time.time() - start_time) * 1000)
                
                # Log the query in platform database
                self._log_query(query, QueryType.SQL, execution_time, user_id, connection_id)
                
                return QueryResponse(
                    success=True,
                    data=data,
                    columns=list(columns),
                    row_count=len(data),
                    execution_time_ms=execution_time
                )
                
        except AccessDeniedError as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_query(query, QueryType.SQL, execution_time, user_id, connection_id, str(e))
            
            return QueryResponse(
                success=False,
                message=f"Access denied: {str(e)}",
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_query(query, QueryType.SQL, execution_time, user_id, connection_id, str(e))
            
            return QueryResponse(
                success=False,
                message=str(e),
                execution_time_ms=execution_time
            )
    
    def get_database_schema(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get schema from a specific client database"""
        try:
            # Get client database connection
            client_engine = self.connection_service.get_client_connection(user_id, connection_id)
            
            # Get schema from client database
            with client_engine.connect() as conn:
                schema_query = text("""
                    SELECT 
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    ORDER BY table_name, ordinal_position
                """)
                
                result = conn.execute(schema_query)
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"Error getting schema: {e}")
            return []
    
    def get_sample_data(self, user_id: uuid.UUID, connection_id: uuid.UUID, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a specific client database table"""
        try:
            # Get client database connection
            client_engine = self.connection_service.get_client_connection(user_id, connection_id)
            
            # Get sample data from client database
            with client_engine.connect() as conn:
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"Error getting sample data: {e}")
            return []
    
    def get_user_connections(self, user_id: uuid.UUID) -> List[DatabaseConnection]:
        """Get all database connections for a user"""
        return self.connection_service.get_user_connections(user_id)
    
    def test_connection(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> Dict[str, Any]:
        """Test connection to a client database"""
        try:
            # Test the connection
            client_engine = self.connection_service.get_client_connection(user_id, connection_id)
            
            with client_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return {"success": True, "message": "Connection successful"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_query(self, query: str, query_type: QueryType, execution_time: int, 
                   user_id: uuid.UUID, connection_id: uuid.UUID, error_message: Optional[str] = None):
        """Log query execution in platform database"""
        try:
            log_entry = QueryHistory(
                id=uuid.uuid4(),
                user_id=user_id,
                database_connection_id=connection_id,
                natural_language_query=None,  # For SQL queries
                generated_sql_query=query,
                execution_time_ms=execution_time,
                row_count=0,  # Will be updated if successful
                status="success" if error_message is None else "error",
                error_message=error_message
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            print(f"Error logging query: {e}")
            self.db.rollback() 