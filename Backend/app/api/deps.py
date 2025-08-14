from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import verify_token
from app.models.user import User
from app.services.mongodb_service import mongodb_service

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token with MongoDB session validation"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")  # JWT uses 'sub' for subject
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")
    
    print(f" Auth middleware - Username: {username}, User ID: {user_id}, Session ID: {session_id}")
    
    # Get user from database
    user = db.query(User).filter(User.email == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate MongoDB session if available
    if mongodb_service.is_available() and session_id:
        print(f" Checking existing session: {session_id}")
        session_data = mongodb_service.get_session(session_id)
        if not session_data:
            # Session expired or invalid, create new one
            print(f" Session not found in MongoDB, creating new session for user: {username}")
            session_data = {
                "user_id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "login_time": str(user.created_at),
                "ip_address": "unknown"
            }
            new_session_id = mongodb_service.create_session(str(user.id), session_data)
            if new_session_id:
                print(f" New session created: {new_session_id} for user: {username}")
                # Log session refresh activity
                mongodb_service.log_user_activity(
                    user_id=str(user.id),
                    action="session_refresh",
                    details={"old_session_id": session_id, "new_session_id": new_session_id}
                )
            else:
                print(f"ERROR: Failed to create new session for user: {username}")
        else:
            print(f" Existing session validated: {session_id}")
    else:
        # No session_id in token or MongoDB not available, create session
        if mongodb_service.is_available():
            print(f" No session found for user: {username}, creating new session")
            session_data = {
                "user_id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "login_time": str(user.created_at),
                "ip_address": "unknown"
            }
            new_session_id = mongodb_service.create_session(str(user.id), session_data)
            if new_session_id:
                print(f" New session created: {new_session_id} for user: {username}")
                # Log session creation activity
                mongodb_service.log_user_activity(
                    user_id=str(user.id),
                    action="session_created",
                    details={"session_id": new_session_id, "email": user.email}
                )
            else:
                print(f"ERROR: Failed to create session for user: {username}")
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user 