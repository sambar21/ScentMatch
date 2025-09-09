from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
    blacklist_token,
    check_login_rate_limit,
)
from app.core.structured_logger import log_business_event 
from app.middleware.simple_logging import get_correlation_id
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.schemas.auth import LoginRequest, RefreshTokenRequest
from sqlalchemy import select

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user account.
    
    - **email**: Valid email address (will be used for login)
    - **password**: Strong password (8+ chars, mixed case, numbers)
    - **display_name**: Optional display name
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password and create user
    hashed_password = hash_password(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        bio=user_data.bio,
        avatar_url=user_data.avatar_url,
        is_active=True,
        is_verified=False  # Email verification required
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user
@router.post("/login")
async def login_user(
    login_data: LoginRequest,
    request: Request,  # ADD THIS parameter
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Authenticate user and return JWT tokens.
    
    Returns access token (30min) and refresh token (7 days).
    Rate limited: 5 attempts per 15 minutes per IP.
    """
    correlation_id = get_correlation_id()
    client_ip = request.client.host
    
    # Rate limiting for login attempts
    rate_limit = await check_login_rate_limit(f"login:{client_ip}")
    
    if not rate_limit["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {(rate_limit['reset_time'] - int(datetime.now().timestamp()))//60} minutes",
            headers={"Retry-After": str(rate_limit["reset_time"])}
        )
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account is locked
    if user.is_account_locked():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to failed login attempts"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.now(timezone.utc)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Successful login - reset failed attempts and update last login
    user.reset_failed_attempts()
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutes in seconds
    }


@router.get("/me", response_model=UserRead)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)  # Changed from Session to AsyncSession
) -> Any:
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    # Verify token
    payload = await verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database - FIXED: Use async syntax
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


@router.post("/refresh")
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)  # Changed from Session to AsyncSession
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    Implements token rotation for security.
    """
    # Verify refresh token
    payload = await verify_token(refresh_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user - FIXED: Use async syntax
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified
    }
    
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout_user( request: Request ,
    credentials: HTTPAuthorizationCredentials = Depends(security) ) -> Dict[str, str]:
    """
    Logout user by blacklisting the current token.
    """
    # Verify token exists and get payload
    payload = await verify_token(credentials.credentials, "access")  # Make async
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Blacklist the token
    success = await blacklist_token(credentials.credentials)  # Use actual blacklisting
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )
    
    return {"message": "Successfully logged out"}


@router.patch("/profile", response_model=UserRead)
async def update_profile(
    profile_data: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)  # Changed from Session to AsyncSession
) -> Any:
    """
    Update current user's profile information.
    """
    # Verify token and get user
    payload = await verify_token(credentials.credentials, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user - FIXED: Use async syntax
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()  # FIXED: Added await
    await db.refresh(user)  # FIXED: Added await
    
    return user