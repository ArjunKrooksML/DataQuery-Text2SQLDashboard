"""
Database Connection Management API Endpoints
Handles CRUD operations for multi-tenant database connections.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.database_connection_service import DatabaseConnectionService, AccessDeniedError
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.connection import (
    ConnectionCreate, ConnectionUpdate, ConnectionResponse, 
    ConnectionTestResponse, SchemaResponse
)
import uuid

router = APIRouter()


@router.get("/", response_model=List[ConnectionResponse])
def get_user_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all database connections for the current user"""
    connection_service = DatabaseConnectionService(db)
    connections = connection_service.get_user_connections(current_user.id)
    
    return [
        ConnectionResponse(
            id=str(conn.id),
            name=conn.name,
            database_type=conn.database_type,
            host=conn.host,
            port=conn.port,
            database_name=conn.database_name,
            username=conn.username,
            is_active=conn.is_active,
            last_connected_at=conn.last_connected_at,
            created_at=conn.created_at,
            updated_at=conn.updated_at
        )
        for conn in connections
    ]


@router.post("/", response_model=ConnectionResponse)
def create_connection(
    connection_data: ConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new database connection for the current user"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        connection = connection_service.create_connection(
            user_id=current_user.id,
            connection_data=connection_data.dict()
        )
        
        return ConnectionResponse(
            id=str(connection.id),
            name=connection.name,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            is_active=connection.is_active,
            last_connected_at=connection.last_connected_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create connection: {str(e)}"
        )


@router.get("/{connection_id}", response_model=ConnectionResponse)
def get_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific database connection"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        conn_id = uuid.UUID(connection_id)
        connection = connection_service.get_connection_by_id(conn_id)
        
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found"
            )
        
        # Check if user has access
        if not connection_service.user_has_access(current_user.id, conn_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this database connection"
            )
        
        return ConnectionResponse(
            id=str(connection.id),
            name=connection.name,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            is_active=connection.is_active,
            last_connected_at=connection.last_connected_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid connection ID format"
        )


@router.put("/{connection_id}", response_model=ConnectionResponse)
def update_connection(
    connection_id: str,
    connection_data: ConnectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a database connection"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        conn_id = uuid.UUID(connection_id)
        
        # Check if user has access
        if not connection_service.user_has_access(current_user.id, conn_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this database connection"
            )
        
        connection = connection_service.update_connection(conn_id, connection_data.dict(exclude_unset=True))
        
        return ConnectionResponse(
            id=str(connection.id),
            name=connection.name,
            database_type=connection.database_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            is_active=connection.is_active,
            last_connected_at=connection.last_connected_at,
            created_at=connection.created_at,
            updated_at=connection.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data: {str(e)}"
        )


@router.delete("/{connection_id}")
def delete_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a database connection"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        conn_id = uuid.UUID(connection_id)
        
        # Check if user has access
        if not connection_service.user_has_access(current_user.id, conn_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this database connection"
            )
        
        success = connection_service.delete_connection(conn_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database connection not found"
            )
        
        return {"message": "Database connection deleted successfully"}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid connection ID format"
        )


@router.post("/{connection_id}/test", response_model=ConnectionTestResponse)
def test_connection(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Test if a database connection is working"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        conn_id = uuid.UUID(connection_id)
        
        # Check if user has access
        if not connection_service.user_has_access(current_user.id, conn_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this database connection"
            )
        
        result = connection_service.test_connection(conn_id)
        
        return ConnectionTestResponse(
            success=result["success"],
            message=result.get("message", ""),
            error=result.get("error", "")
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid connection ID format"
        )


@router.get("/{connection_id}/schema", response_model=SchemaResponse)
def get_database_schema(
    connection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get schema for a specific database connection"""
    connection_service = DatabaseConnectionService(db)
    
    try:
        conn_id = uuid.UUID(connection_id)
        
        # Check if user has access
        if not connection_service.user_has_access(current_user.id, conn_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this database connection"
            )
        
        schema = connection_service.detect_schema(conn_id)
        
        return SchemaResponse(
            connection_id=connection_id,
            schema=schema,
            success=True
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid connection ID format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect schema: {str(e)}"
        ) 