from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
import uuid
import enum


class QueryType(str, enum.Enum):
    SQL = "sql"
    LLM = "llm"


class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    database_connection_id = Column(UUID(as_uuid=True), ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=False)
    natural_language_query = Column(Text, nullable=False)
    generated_sql_query = Column(Text, nullable=False)
    execution_time_ms = Column(Integer)
    row_count = Column(Integer)
    status = Column(String(20), default="success")  # success, error, timeout
    error_message = Column(Text)
    result_hash = Column(String(64))  # For caching
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="query_history")
    database_connection = relationship("DatabaseConnection", back_populates="query_history") 