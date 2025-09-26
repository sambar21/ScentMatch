
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class RefreshTokenRequest(BaseModel):
 
    refresh_token: str = Field(..., description="Valid refresh token")


class TokenResponse(BaseModel):
 
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")


class LoginResponse(TokenResponse):
   
    user: dict = Field(..., description="User information")


class LogoutResponse(BaseModel):
  
    message: str = Field(..., description="Logout confirmation message")