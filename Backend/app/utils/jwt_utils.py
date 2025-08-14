"""
JWT utility functions for token extraction and validation
"""

from typing import Optional, Dict, Any
from fastapi import Request
from app.core.security import extract_user_id_from_token, extract_token_from_auth_header, verify_token


def get_user_info_from_request(request: Request) -> Dict[str, Any]:
    """
    Extract comprehensive user information from request
    Returns a dictionary with user_id, session_id, and other user data
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"user_id": None, "session_id": None, "authenticated": False}
        
        token = extract_token_from_auth_header(auth_header)
        if not token:
            return {"user_id": None, "session_id": None, "authenticated": False}
        
        # Use the full verify_token for complete payload
        payload = verify_token(token)
        if not payload:
            return {"user_id": None, "session_id": None, "authenticated": False}
        
        return {
            "user_id": payload.get("user_id"),
            "session_id": payload.get("session_id"),
            "username": payload.get("username"),
            "email": payload.get("sub"),
            "authenticated": True
        }
        
    except Exception as e:
        print(f"Error extracting user info from request: {e}")
        return {"user_id": None, "session_id": None, "authenticated": False}


def get_rate_limit_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting
    Uses user ID if authenticated, otherwise falls back to IP address
    """
    user_info = get_user_info_from_request(request)
    
    if user_info["authenticated"] and user_info["user_id"]:
        return f"user:{user_info['user_id']}"
    
    # Fallback to IP address for unauthenticated users
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def extract_user_id_from_request(request: Request) -> Optional[str]:
    """
    Simple function to extract just the user ID from request
    Compatible with existing rate limiter interface
    """
    user_info = get_user_info_from_request(request)
    return user_info["user_id"] if user_info["authenticated"] else None


def is_token_valid(request: Request) -> bool:
    """
    Check if the request contains a valid JWT token
    """
    user_info = get_user_info_from_request(request)
    return user_info["authenticated"]


def get_token_payload(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the full JWT token payload from request
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        token = extract_token_from_auth_header(auth_header)
        if not token:
            return None
        
        return verify_token(token)
        
    except Exception as e:
        print(f"Error getting token payload: {e}")
        return None
