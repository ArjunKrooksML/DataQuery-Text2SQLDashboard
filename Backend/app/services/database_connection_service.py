"""
Database Connection Service for Multi-Tenant Architecture
Manages dynamic connections to client databases with proper isolation.
"""

import uuid
import base64
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet
from app.models.database_connection import DatabaseConnection
from app.models.user import User
from app.core.config import settings
from app.core.security import get_password_hash


class DatabaseConnectionService:
    def __init__(self, db: Session):
        self.db = db
        self.encryption_key = settings.SECRET_KEY.encode()[:32]  # Use first 32 bytes
        self.cipher = Fernet(base64.urlsafe_b64encode(self.encryption_key))
    
    def create_connection(self, user_id: uuid.UUID, connection_data: Dict[str, Any]) -> DatabaseConnection:
        """Create a new database connection for a user"""
        
        # Encrypt sensitive data
        encrypted_password = self.encrypt_password(connection_data.get("password", ""))
        encrypted_connection_string = self.encrypt_connection_string(connection_data)
        
        connection = DatabaseConnection(
            id=uuid.uuid4(),
            user_id=user_id,
            name=connection_data["name"],
            database_type=connection_data["database_type"],
            host=connection_data.get("host"),
            port=connection_data.get("port"),
            database_name=connection_data.get("database_name"),
            username=connection_data.get("username"),
            password_encrypted=encrypted_password,
            connection_string_encrypted=encrypted_connection_string,
            is_active=True
        )
        
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        
        return connection
    
    def get_user_connections(self, user_id: uuid.UUID) -> List[DatabaseConnection]:
        """Get all database connections for a specific user"""
        return self.db.query(DatabaseConnection).filter(
            DatabaseConnection.user_id == user_id,
            DatabaseConnection.is_active == True
        ).all()
    
    def get_connection_by_id(self, connection_id: uuid.UUID) -> Optional[DatabaseConnection]:
        """Get a specific database connection by ID"""
        return self.db.query(DatabaseConnection).filter(
            DatabaseConnection.id == connection_id
        ).first()
    
    def user_has_access(self, user_id: uuid.UUID, connection_id: uuid.UUID) -> bool:
        """Check if user has access to a specific database connection"""
        connection = self.get_connection_by_id(connection_id)
        return connection and connection.user_id == user_id and connection.is_active
    
    def test_connection(self, connection_id: uuid.UUID) -> Dict[str, Any]:
        """Test if a database connection is working"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            return {"success": False, "error": "Connection not found"}
        
        try:
            # Decrypt connection details
            decrypted_password = self.decrypt_password(connection.password_encrypted)
            
            # Create connection string
            if connection.database_type == "postgresql":
                connection_string = f"postgresql://{connection.username}:{decrypted_password}@{connection.host}:{connection.port}/{connection.database_name}"
            elif connection.database_type == "mysql":
                connection_string = f"mysql+pymysql://{connection.username}:{decrypted_password}@{connection.host}:{connection.port}/{connection.database_name}"
            elif connection.database_type == "sqlite":
                connection_string = f"sqlite:///{connection.database_name}"
            else:
                return {"success": False, "error": f"Unsupported database type: {connection.database_type}"}
            
            # Test connection
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Update last connected timestamp
            connection.last_connected_at = text("NOW()")
            self.db.commit()
            
            return {"success": True, "message": "Connection successful"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_client_connection(self, user_id: uuid.UUID, connection_id: uuid.UUID):
        """Get a client database connection with access control"""
        
        # Verify user has access
        if not self.user_has_access(user_id, connection_id):
            raise AccessDeniedError("User cannot access this database connection")
        
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            raise ValueError("Database connection not found")
        
        # Decrypt connection details
        decrypted_password = self.decrypt_password(connection.password_encrypted)
        
        # Create dynamic connection
        return self.create_dynamic_connection(connection, decrypted_password)
    
    def create_dynamic_connection(self, connection: DatabaseConnection, password: str):
        """Create a dynamic connection to a client database"""
        
        if connection.database_type == "postgresql":
            connection_string = f"postgresql://{connection.username}:{password}@{connection.host}:{connection.port}/{connection.database_name}"
        elif connection.database_type == "mysql":
            connection_string = f"mysql+pymysql://{connection.username}:{password}@{connection.host}:{connection.port}/{connection.database_name}"
        elif connection.database_type == "sqlite":
            connection_string = f"sqlite:///{connection.database_name}"
        else:
            raise ValueError(f"Unsupported database type: {connection.database_type}")
        
        return create_engine(connection_string)
    
    def detect_schema(self, connection_id: uuid.UUID) -> Dict[str, Any]:
        """Detect and cache schema for a client database"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            raise ValueError("Database connection not found")
        
        try:
            # Get client database connection
            client_engine = self.get_client_connection(connection.user_id, connection_id)
            
            # Detect schema
            schema = self.analyze_database_schema(client_engine)
            
            # Cache schema in platform database
            connection.schema_json = schema
            self.db.commit()
            
            return schema
            
        except Exception as e:
            raise Exception(f"Failed to detect schema: {str(e)}")
    
    def analyze_database_schema(self, engine) -> Dict[str, Any]:
        """Analyze database schema and return structure"""
        schema = {"tables": []}
        
        with engine.connect() as conn:
            # Get list of tables
            if engine.dialect.name == "postgresql":
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            elif engine.dialect.name == "mysql":
                tables_query = text("SHOW TABLES")
            else:
                tables_query = text("SELECT name FROM sqlite_master WHERE type='table'")
            
            tables = conn.execute(tables_query).fetchall()
            
            for table in tables:
                table_name = table[0]
                table_info = {"name": table_name, "columns": []}
                
                # Get column information
                if engine.dialect.name == "postgresql":
                    columns_query = text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """)
                elif engine.dialect.name == "mysql":
                    columns_query = text("DESCRIBE " + table_name)
                else:
                    columns_query = text("PRAGMA table_info(" + table_name + ")")
                
                columns = conn.execute(columns_query, {"table_name": table_name}).fetchall()
                
                for column in columns:
                    if engine.dialect.name == "postgresql":
                        column_info = {
                            "name": column[0],
                            "type": column[1],
                            "nullable": column[2] == "YES"
                        }
                    elif engine.dialect.name == "mysql":
                        column_info = {
                            "name": column[0],
                            "type": column[1],
                            "nullable": column[2] == "YES"
                        }
                    else:
                        column_info = {
                            "name": column[1],
                            "type": column[2],
                            "nullable": column[3] == 0
                        }
                    
                    table_info["columns"].append(column_info)
                
                schema["tables"].append(table_info)
        
        return schema
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt database password"""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt database password"""
        return self.cipher.decrypt(encrypted_password.encode()).decode()
    
    def encrypt_connection_string(self, connection_data: Dict[str, Any]) -> str:
        """Encrypt full connection string"""
        if connection_data["database_type"] == "postgresql":
            connection_string = f"postgresql://{connection_data['username']}:{connection_data['password']}@{connection_data['host']}:{connection_data['port']}/{connection_data['database_name']}"
        elif connection_data["database_type"] == "mysql":
            connection_string = f"mysql+pymysql://{connection_data['username']}:{connection_data['password']}@{connection_data['host']}:{connection_data['port']}/{connection_data['database_name']}"
        else:
            connection_string = f"sqlite:///{connection_data['database_name']}"
        
        return self.cipher.encrypt(connection_string.encode()).decode()
    
    def update_connection(self, connection_id: uuid.UUID, update_data: Dict[str, Any]) -> DatabaseConnection:
        """Update a database connection"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            raise ValueError("Database connection not found")
        
        # Update fields
        for field, value in update_data.items():
            if field == "password":
                connection.password_encrypted = self.encrypt_password(value)
            elif hasattr(connection, field):
                setattr(connection, field, value)
        
        self.db.commit()
        self.db.refresh(connection)
        return connection
    
    def delete_connection(self, connection_id: uuid.UUID) -> bool:
        """Delete a database connection"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            return False
        
        connection.is_active = False
        self.db.commit()
        return True


class AccessDeniedError(Exception):
    """Raised when user doesn't have access to a resource"""
    pass 