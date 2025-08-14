#!/usr/bin/env python3
"""
New Database setup script for DataWise backend.
Creates tables based on the new schema with UUIDs and proper relationships.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.database.connection import Base
from app.models.user import User
from app.models.database_connection import DatabaseConnection
from app.models.query_history import QueryHistory
from app.models.query_cache import QueryCache
from app.models.user_sessions import UserSession
from app.core.security import get_password_hash
from app.services.database_connection_service import DatabaseConnectionService
import uuid

def create_new_database():
    """Create new database tables with proper schema"""
    
    # Show which database we're connecting to
    print(f"🔗 Connecting to database: {settings.DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create sample user
        user = create_sample_user(db)
        
        # Create sample database connection
        connection = create_sample_database_connection(db, user.id)
        
        # Create sample query history
        create_sample_query_history(db, user.id, connection.id)
        
        print("✅ Platform database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# REMOVED: Business data tables (sales_data, orders, customers)
# These should be in client databases, not platform database
# Platform database should only contain:
# - users (user management)
# - database_connections (client DB configs)
# - query_history (query logs)
# - query_cache (cached results)
# - user_sessions (authentication sessions)

def create_sample_user(db):
    """Create a sample user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "admin@datadashboard.com").first()
    
    if not existing_user:
        user = User(
            id=uuid.uuid4(),
            email="admin@datadashboard.com",
            password_hash=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            company_name="DataWise",
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Created sample user: admin@datadashboard.com / admin123")
        print(f"   User ID: {user.id}")
        
        return user
    else:
        print(f"✅ Sample user already exists: admin@datadashboard.com")
        return existing_user

def create_sample_database_connection(db, user_id):
    """Create a sample database connection"""
    
    # Check if connection already exists
    existing_connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.user_id == user_id,
        DatabaseConnection.name == "Platform Database"
    ).first()
    
    if not existing_connection:
        # Get password from environment or use default
        db_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        
        # Create connection service to handle encryption
        connection_service = DatabaseConnectionService(db)
        
        # Create connection data for PLATFORM database
        connection_data = {
            "name": "Platform Database",
            "database_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database_name": "datawiser_platform",  # Platform database itself
            "username": "postgres",
            "password": db_password,  # Use actual password from environment
            "is_active": True
        }
        
        # Create connection with proper encryption
        connection = connection_service.create_connection(user_id, connection_data)
        
        print(f"✅ Created platform database connection")
        print(f"   Connection ID: {connection.id}")
        print(f"   Database: {connection.database_name}")
        print(f"   Host: {connection.host}:{connection.port}")
        
        return connection
    else:
        print(f"✅ Platform database connection already exists")
        return existing_connection

def create_sample_query_history(db, user_id, connection_id):
    """Create sample query history"""
    
    # Check if query history already exists
    existing_history = db.query(QueryHistory).filter(
        QueryHistory.user_id == user_id
    ).first()
    
    if not existing_history:
        sample_queries = [
            {
                "natural_language_query": "Show me sales by region",
                "generated_sql_query": "SELECT region, SUM(sales_amount) FROM sales_data GROUP BY region",
                "execution_time_ms": 45,
                "row_count": 4,
                "status": "success"
            },
            {
                "natural_language_query": "What are the top selling products?",
                "generated_sql_query": "SELECT product_name, SUM(sales_amount) FROM sales_data GROUP BY product_name ORDER BY SUM(sales_amount) DESC",
                "execution_time_ms": 32,
                "row_count": 3,
                "status": "success"
            },
            {
                "natural_language_query": "Show me recent orders",
                "generated_sql_query": "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10",
                "execution_time_ms": 28,
                "row_count": 5,
                "status": "success"
            }
        ]
        
        for query_data in sample_queries:
            query_history = QueryHistory(
                id=uuid.uuid4(),
                user_id=user_id,
                database_connection_id=connection_id,
                natural_language_query=query_data["natural_language_query"],
                generated_sql_query=query_data["generated_sql_query"],
                execution_time_ms=query_data["execution_time_ms"],
                row_count=query_data["row_count"],
                status=query_data["status"]
            )
            
            db.add(query_history)
        
        db.commit()
        print(f"✅ Created sample query history")
    else:
        print(f"✅ Sample query history already exists")

if __name__ == "__main__":
    print("🚀 Setting up new database schema...")
    print(f"📁 Environment file loaded from: {Path(__file__).parent.parent / '.env'}")
    print(f"🔧 DATABASE_URL from environment: {os.getenv('DATABASE_URL', 'Not set')}")
    create_new_database()
    print("✅ Database setup completed!") 