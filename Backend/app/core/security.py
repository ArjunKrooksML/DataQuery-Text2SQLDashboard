from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        session_id: str = payload.get("session_id")
        
        if username is None:
            return None
            
        # Return complete payload for MongoDB session management
        return {
            "sub": username,
            "user_id": user_id,
            "session_id": session_id,
            "username": username  # Keep for backward compatibility
        }
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token without full validation"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        return None


def extract_token_from_auth_header(auth_header: str) -> Optional[str]:
    """Extract JWT token from Authorization header"""
    if not auth_header:
        return None
    
    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix
    
    return None 