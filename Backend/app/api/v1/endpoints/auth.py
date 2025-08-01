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

router = APIRouter()


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
        print(f"🔍 Registration attempt for email: {user_create.email}")
        print(f"📝 User data: {user_create.dict()}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        
        if existing_user:
            print(f"❌ User already exists: {existing_user.email} (ID: {existing_user.id})")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_create.email}' already exists"
            )
        
        print(f"✅ No existing user found, creating new user: {user_create.email}")
        
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
        
        print(f"📝 User object created, adding to database...")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ User created successfully: {db_user.email} (ID: {db_user.id})")
        
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
        
        print(f"📤 Returning response: {response_data}")
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions (like "user already exists")
        print(f"❌ HTTP Exception raised")
        raise
    except Exception as e:
        # Log the actual error for debugging
        print(f"❌ Registration error: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
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
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 