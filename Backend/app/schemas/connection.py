"""
Pydantic schemas for database connection management.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ConnectionBase(BaseModel):
    name: str = Field(..., description="Connection name")
    database_type: str = Field(..., description="Database type (postgresql, mysql, sqlite)")
    host: Optional[str] = Field(None, description="Database host")
    port: Optional[int] = Field(None, description="Database port")
    database_name: Optional[str] = Field(None, description="Database name")
    username: Optional[str] = Field(None, description="Database username")
    password: Optional[str] = Field(None, description="Database password")


class ConnectionCreate(ConnectionBase):
    """Schema for creating a new database connection"""
    name: str = Field(..., min_length=1, max_length=255)
    database_type: str = Field(..., pattern="^(postgresql|mysql|sqlite)$")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "My PostgreSQL Database",
                "database_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database_name": "my_database",
                "username": "my_user",
                "password": "my_password"
            }
        }


class ConnectionUpdate(BaseModel):
    """Schema for updating a database connection"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    database_type: Optional[str] = Field(None, pattern="^(postgresql|mysql|sqlite)$")
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Database Name",
                "host": "new-host.com",
                "port": 5432
            }
        }


class ConnectionResponse(BaseModel):
    """Schema for database connection response"""
    id: str
    name: str
    database_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    last_connected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConnectionTestResponse(BaseModel):
    """Schema for connection test response"""
    success: bool
    message: str = ""
    error: str = ""
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Connection successful"
            }
        }


class SchemaResponse(BaseModel):
    """Schema for database schema response"""
    connection_id: str
    schema_data: Dict[str, Any]
    success: bool
    
    class Config:
        schema_extra = {
            "example": {
                "connection_id": "uuid-here",
                "schema_data": {
                    "tables": [
                        {
                            "name": "users",
                            "columns": [
                                {"name": "id", "type": "integer", "nullable": False},
                                {"name": "email", "type": "varchar", "nullable": False}
                            ]
                        }
                    ]
                },
                "success": True
            }
        } 