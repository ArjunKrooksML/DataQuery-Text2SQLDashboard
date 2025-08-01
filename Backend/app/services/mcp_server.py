"""
MCP (Model Context Protocol) Server Implementation
This server communicates with the main backend API instead of directly accessing the database.
"""

import asyncio
import json
import httpx
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# MCP Server Models
class MCPRequest(BaseModel):
    prompt: str
    context_type: str = "database"
    include_schema: bool = True
    include_sample_data: bool = True

class MCPResponse(BaseModel):
    context: Dict[str, Any]
    relevant_tables: List[str]
    suggested_sql: Optional[str] = None
    confidence_score: float

import os

class MCPServer:
    def __init__(self, backend_url: str = None):
        self.backend_url = backend_url or os.getenv("BACKEND_URL", "http://backend:8000")
        self.api_base = f"{self.backend_url}/api/v1"
    
    async def get_database_schema(self) -> List[Dict[str, Any]]:
        """Get database schema from main backend"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base}/queries/schema")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching schema: {e}")
                return []
    
    async def get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get sample data from main backend"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_base}/queries/sample-data/{table_name}?limit={limit}")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching sample data: {e}")
                return []
    
    def analyze_prompt(self, prompt: str, schema: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze prompt to find relevant database context"""
        prompt_lower = prompt.lower()
        
        # Find relevant tables and columns
        relevant_tables = set()
        relevant_columns = []
        
        for table_info in schema:
            table_name = table_info.get("table_name", "").lower()
            column_name = table_info.get("column_name", "").lower()
            
            # Check if table or column names appear in the prompt
            if table_name in prompt_lower:
                relevant_tables.add(table_info["table_name"])
                relevant_columns.append(table_info)
            elif column_name in prompt_lower:
                relevant_tables.add(table_info["table_name"])
                relevant_columns.append(table_info)
        
        return {
            "schema": schema,
            "relevant_tables": list(relevant_tables),
            "relevant_columns": relevant_columns,
            "prompt_analysis": {
                "detected_tables": list(relevant_tables),
                "detected_columns": [col["column_name"] for col in relevant_columns]
            }
        }
    
    def generate_sql_suggestion(self, prompt: str, context: Dict[str, Any]) -> Optional[str]:
        """Generate SQL suggestion based on prompt and context"""
        relevant_tables = context.get("relevant_tables", [])
        
        if not relevant_tables:
            return None
        
        # Simple SQL generation logic
        if "sales" in prompt.lower() and "region" in prompt.lower():
            return "SELECT region, SUM(sales_amount) FROM sales_data GROUP BY region"
        elif "count" in prompt.lower():
            return f"SELECT COUNT(*) FROM {relevant_tables[0]}"
        elif "top" in prompt.lower() or "best" in prompt.lower():
            return f"SELECT * FROM {relevant_tables[0]} ORDER BY sales_amount DESC LIMIT 5"
        
        return None
    
    async def process_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Process MCP request and return context"""
        try:
            # Get schema from main backend
            schema = await self.get_database_schema()
            
            # Analyze the prompt
            context = self.analyze_prompt(request.prompt, schema)
            
            # Get sample data for relevant tables
            sample_data = {}
            if request.include_sample_data:
                for table_name in context["relevant_tables"]:
                    data = await self.get_sample_data(table_name, limit=3)
                    if data:
                        sample_data[table_name] = data
            
            context["sample_data"] = sample_data
            
            # Generate SQL suggestion
            suggested_sql = None
            if request.include_schema:
                suggested_sql = self.generate_sql_suggestion(request.prompt, context)
            
            return MCPResponse(
                context=context,
                relevant_tables=context["relevant_tables"],
                suggested_sql=suggested_sql,
                confidence_score=0.85 if context["relevant_tables"] else 0.3
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MCP processing error: {str(e)}")

# Standalone MCP Server
mcp_app = FastAPI(title="DataWise MCP Server", version="1.0.0")
mcp_server = MCPServer()

@mcp_app.post("/mcp/context", response_model=MCPResponse)
async def get_context(request: MCPRequest):
    """Get database context for a prompt"""
    return await mcp_server.process_mcp_request(request)

@mcp_app.get("/mcp/schema")
async def get_schema():
    """Get complete database schema from main backend"""
    return await mcp_server.get_database_schema()

@mcp_app.get("/mcp/sample-data/{table_name}")
async def get_sample_data(table_name: str, limit: int = 5):
    """Get sample data from main backend"""
    return await mcp_server.get_sample_data(table_name, limit)

@mcp_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mcp-server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp_app, host="0.0.0.0", port=8001) 