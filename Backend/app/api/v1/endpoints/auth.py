from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.config import settings
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.services.mongodb_service import mongodb_service

router = APIRouter()


@router.get("/test-mongodb")
def test_mongodb():
    """Test MongoDB connection and session creation"""
    try:
        # Test MongoDB availability
        is_available = mongodb_service.is_available()
        
        if not is_available:
            return {"error": "MongoDB not available"}
        
        # Test session creation
        test_session_data = {
            "test": "data",
            "timestamp": "2025-08-11"
        }
        
        session_id = mongodb_service.create_session("test-user", test_session_data)
        
        if session_id:
            # Test activity logging
            mongodb_service.log_user_activity(
                user_id="test-user",
                action="test",
                details={"test": "activity"}
            )
            
            return {
                "status": "success",
                "mongodb_available": True,
                "session_created": True,
                "session_id": session_id,
                "activity_logged": True
            }
        else:
            return {"error": "Failed to create session"}
            
    except Exception as e:
        return {"error": f"MongoDB test failed: {str(e)}"}


@router.get("/debug/users")
def list_users(db: Session = Depends(get_db)):
    """Debug endpoint to list all users (remove in production)"""
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at
            }
            for user in users
        ]
    }


@router.post("/register", response_model=UserResponse)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        print(f" Registration attempt for email: {user_create.email}")
        print(f" User data: {user_create.dict()}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        
        if existing_user:
            print(f"ERROR: User already exists: {existing_user.email} (ID: {existing_user.id})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_create.email}' already exists"
            )
        
        print(f" No existing user found, creating new user: {user_create.email}")
        
        # Create new user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            company_name=user_create.company_name,
            is_active=user_create.is_active
        )
        
        print(f" User object created, adding to database...")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f" User created successfully: {db_user.email} (ID: {db_user.id})")
        
        # Convert UUID to string for response
        response_data = {
            "id": str(db_user.id),
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "company_name": db_user.company_name,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at
        }
        
        print(f" Returning response: {response_data}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (like "user already exists")
        print(f"ERROR: HTTP Exception raised")
        raise
    except Exception as e:
        # Log the actual error for debugging
        print(f"ERROR: Registration error: {str(e)}")
        print(f"ERROR: Error type: {type(e).__name__}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        print(f" Login attempt for user: {user.email}")
        
        # Create MongoDB session
        try:
            session_data = {
                "user_id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "login_time": str(user.created_at),
                "ip_address": "unknown"  # Could be extracted from request
            }
            
            print(f" Creating MongoDB session for user: {user.email}")
            session_id = mongodb_service.create_session(str(user.id), session_data)
            
            if session_id:
                print(f" MongoDB session created: {session_id} for user: {user.email}")
                
                # Log user activity
                mongodb_service.log_user_activity(
                    user_id=str(user.id),
                    action="login",
                    details={"session_id": session_id, "email": user.email}
                )
                print(f" User activity logged for: {user.email}")
            else:
                print(f"WARNING: Failed to create MongoDB session for user: {user.email}")
                session_id = None
                
        except Exception as e:
            print(f"ERROR: MongoDB session creation error: {str(e)}")
            session_id = None
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "session_id": session_id}, 
            expires_delta=access_token_expires
        )
        
        print(f" Login successful for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        ) 