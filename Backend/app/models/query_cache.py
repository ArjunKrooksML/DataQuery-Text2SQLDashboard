from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
import uuid


class QueryCache(Base):
    __tablename__ = "query_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_hash = Column(String(64), unique=True, nullable=False)
    database_connection_id = Column(UUID(as_uuid=True), ForeignKey("database_connections.id", ondelete="CASCADE"), nullable=False)
    sql_query = Column(Text, nullable=False)
    result_data = Column(JSONB)  # Query result as JSONB
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    database_connection = relationship("DatabaseConnection", back_populates="query_cache") 