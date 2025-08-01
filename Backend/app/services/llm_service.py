import time
import json
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
from app.core.config import settings
from app.models.query_history import QueryHistory, QueryType
from app.schemas.query import LLMQueryResponse
from app.services.database_service import DatabaseService
from app.services.multi_tenant_query_service import MultiTenantQueryService


class LLMService:
    def __init__(self, db: Session):
        self.db = db
        self.database_service = DatabaseService(db)
        self.multi_tenant_service = MultiTenantQueryService(db)
        
        # Initialize OpenAI client only if API key is provided
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def get_database_context(self, prompt: str, user_id: uuid.UUID, connection_id: uuid.UUID) -> Dict[str, Any]:
        """Get relevant database context for the prompt from client database"""
        context = {
            "schema": [],
            "sample_data": {},
            "relevant_tables": []
        }
        
        try:
            # Get database schema from client database
            schema = self.multi_tenant_service.get_database_schema(user_id, connection_id)
            context["schema"] = schema
            
            # Analyze prompt to find relevant tables
            prompt_lower = prompt.lower()
            relevant_tables = set()
            
            for table_info in schema:
                table_name = table_info["table_name"].lower()
                column_name = table_info["column_name"].lower()
                
                # Check if table or column names appear in the prompt
                if table_name in prompt_lower or column_name in prompt_lower:
                    relevant_tables.add(table_info["table_name"])
            
            context["relevant_tables"] = list(relevant_tables)
            
            # Get sample data for relevant tables from client database
            for table_name in relevant_tables:
                sample_data = self.multi_tenant_service.get_sample_data(user_id, connection_id, table_name, limit=3)
                if sample_data:
                    context["sample_data"][table_name] = sample_data
                    
        except Exception as e:
            print(f"Error getting database context: {e}")
        
        return context
    
    def generate_sql_from_prompt(self, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query from natural language prompt"""
        if not self.client:
            return None
            
        try:
            schema_info = json.dumps(context["schema"], indent=2)
            sample_data = json.dumps(context["sample_data"], indent=2)
            
            sql_generation_prompt = f"""
            You are a SQL expert. Based on the following database schema and sample data, 
            generate a SQL query for the user's request.
            
            Database Schema:
            {schema_info}
            
            Sample Data:
            {sample_data}
            
            User Request: {prompt}
            
            Generate only the SQL query, no explanations. If the request cannot be answered with SQL, return null.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a SQL expert. Generate only SQL queries, no explanations."},
                    {"role": "user", "content": sql_generation_prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Basic validation - ensure it starts with SELECT
            if sql_query and sql_query.upper().startswith("SELECT"):
                return sql_query
            return None
            
        except Exception as e:
            print(f"Error generating SQL: {e}")
            return None
    
    def process_llm_query(self, prompt: str, user_id: uuid.UUID, connection_id: uuid.UUID) -> LLMQueryResponse:
        """Process LLM query with database context from client database"""
        start_time = time.time()
        
        try:
            # Check if OpenAI client is available
            if not self.client:
                execution_time = int((time.time() - start_time) * 1000)
                self._log_query(prompt, execution_time, user_id, connection_id, "OpenAI API key not configured")
                return LLMQueryResponse(
                    response="I apologize, but the AI service is not currently available. Please configure your OpenAI API key to use LLM features. You can set the OPENAI_API_KEY environment variable or add it to your .env file.",
                    execution_time_ms=execution_time
                )
            
            # Get database context from client database
            context = self.get_database_context(prompt, user_id, connection_id)
            
            # Generate SQL if possible
            sql_generated = self.generate_sql_from_prompt(prompt, context)
            
            # Create enhanced prompt with context
            enhanced_prompt = self._create_enhanced_prompt(prompt, context, sql_generated)
            
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI assistant with access to a database. Answer questions based on the available data."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log the query
            self._log_query(prompt, execution_time, user_id, connection_id)
            
            return LLMQueryResponse(
                response=ai_response,
                sql_generated=sql_generated,
                confidence_score=0.85,  # Mock confidence score
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log the failed query
            self._log_query(prompt, execution_time, user_id, connection_id, str(e))
            
            return LLMQueryResponse(
                response=f"I apologize, but I encountered an error: {str(e)}",
                execution_time_ms=execution_time
            )
    
    def _create_enhanced_prompt(self, prompt: str, context: Dict[str, Any], sql_generated: Optional[str]) -> str:
        """Create enhanced prompt with database context"""
        schema_info = json.dumps(context["schema"], indent=2)
        sample_data = json.dumps(context["sample_data"], indent=2)
        
        enhanced_prompt = f"""
        You are an AI assistant with access to a database. Answer the user's question based on the available data.
        
        Database Schema:
        {schema_info}
        
        Sample Data:
        {sample_data}
        
        Generated SQL Query (if applicable):
        {sql_generated if sql_generated else "No SQL query generated"}
        
        User Question: {prompt}
        
        Please provide a helpful, natural language response. If you can answer with data, include relevant information. 
        If you generated a SQL query, explain what it does and what the results would show.
        """
        
        return enhanced_prompt
    
    def _log_query(self, prompt: str, execution_time: int, user_id: uuid.UUID, connection_id: uuid.UUID,
                   error_message: Optional[str] = None):
        """Log LLM query execution"""
        try:
            log_entry = QueryHistory(
                id=uuid.uuid4(),
                user_id=user_id,
                database_connection_id=connection_id,
                natural_language_query=prompt,
                generated_sql_query=None,  # Will be set if SQL is generated
                execution_time_ms=execution_time,
                status="success" if not error_message else "error",
                error_message=error_message,
                query_type=QueryType.LLM
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            print(f"Error logging LLM query: {e}")
            self.db.rollback()
        pass 