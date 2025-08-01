from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database.connection import Base


class DatabaseSchema(Base):
    __tablename__ = "database_schemas"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    is_nullable = Column(String, default="YES")
    column_default = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    sample_data = Column(JSON, nullable=True)  # Store sample data for context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 