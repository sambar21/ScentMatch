# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user fields that can be shared across schemas"""
    display_name: Optional[str] = Field(None, max_length=100, description="User's display name")
    first_name: Optional[str] = Field(None, max_length=50, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=50, description="User's last name")
    bio: Optional[str] = Field(None, max_length=500, description="User's biography")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to user's avatar")


class UserCreate(UserBase):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., 
        min_length=8,
        max_length=128,
        description="User's password (8-128 characters)"
    )
    
    @field_validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('email')
    def validate_email_format(cls, v):
        """Additional email validation"""
        if len(v) > 255:
            raise ValueError('Email address too long')
        return v.lower()


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    display_name: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserRead(UserBase):
    """Schema for user data output"""
    id: UUID = Field(..., description="User's unique identifier")
    email: EmailStr = Field(..., description="User's email address")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    full_name: Optional[str] = Field(None, description="User's full name")
    
    class Config:
        from_attributes = True  # Updated for Pydantic V2
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid)
        }


class UserProfile(UserRead):
    """Extended user profile with additional fields"""
    failed_login_attempts: int = Field(..., description="Failed login attempt count")
    is_superuser: bool = Field(..., description="Whether user has admin privileges")


class UserInDB(UserBase):
    """Internal schema with sensitive fields"""
    id: UUID
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    failed_login_attempts: int
    is_superuser: bool
    
    class Config:
        from_attributes = True  # Updated for Pydantic V2