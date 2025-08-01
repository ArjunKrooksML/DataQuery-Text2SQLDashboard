"""
Session management service using MongoDB for storage.
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.database.mongodb import session_store
from app.core.config import settings


class SessionService:
    """Service for managing user sessions"""
    
    def __init__(self):
        self.session_store = session_store
    
    def generate_session_id(self, user_id: str) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.utcnow().isoformat()
        unique_string = f"{user_id}:{timestamp}:{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    async def create_user_session(self, user_id: str, session_data: Dict[str, Any] = None) -> Optional[str]:
        """Create a new session for a user"""
        try:
            session_id = self.generate_session_id(user_id)
            
            if session_data is None:
                session_data = {
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            success = await self.session_store.create_session(session_id, user_id, session_data)
            
            if success:
                return session_id
            return None
            
        except Exception as e:
            print(f"Error creating user session: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        try:
            session = await self.session_store.get_session(session_id)
            return session
            
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Update session data"""
        try:
            # Update last activity
            session_data["last_activity"] = datetime.utcnow().isoformat()
            
            success = await self.session_store.update_session(session_id, session_data)
            return success
            
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            success = await self.session_store.delete_session(session_id)
            return success
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        try:
            sessions = await self.session_store.get_user_sessions(user_id)
            return sessions
            
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    async def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active"""
        try:
            session = await self.session_store.get_session(session_id)
            return session is not None
            
        except Exception as e:
            print(f"Error validating session: {e}")
            return False
    
    async def refresh_session(self, session_id: str) -> bool:
        """Refresh session by updating last activity"""
        try:
            session = await self.session_store.get_session(session_id)
            if session:
                session_data = session.get("session_data", {})
                session_data["last_activity"] = datetime.utcnow().isoformat()
                
                success = await self.session_store.update_session(session_id, session_data)
                return success
            
            return False
            
        except Exception as e:
            print(f"Error refreshing session: {e}")
            return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        try:
            count = await self.session_store.cleanup_expired_sessions()
            return count
            
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0


# Global session service instance
session_service = SessionService() 