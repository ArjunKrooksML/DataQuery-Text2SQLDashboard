from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
import uuid


class DatabaseConnection(Base):
    __tablename__ = "database_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    database_type = Column(String(50), nullable=False)
    host = Column(String(255))
    port = Column(Integer)
    database_name = Column(String(255))
    username = Column(String(255))
    password_encrypted = Column(Text)
    connection_string_encrypted = Column(Text)
    schema_json = Column(JSONB)
    is_active = Column(Boolean, default=True)
    last_connected_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    

    user = relationship("User", back_populates="database_connections")
    query_history = relationship("QueryHistory", back_populates="database_connection")
    query_cache = relationship("QueryCache", back_populates="database_connection") 