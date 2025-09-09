
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for user login request"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")


class LoginResponse(TokenResponse):
    """Schema for login response with user data"""
    user: dict = Field(..., description="User information")


class LogoutResponse(BaseModel):
    """Schema for logout response"""
    message: str = Field(..., description="Logout confirmation message")