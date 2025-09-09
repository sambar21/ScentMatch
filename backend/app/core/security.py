# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import string
from app.services.redis_service import redis_service



pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  
)

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


def hash_password(password: str) -> str:
   
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
  
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  
        "iat": datetime.now(timezone.utc),  # Issued at
        "jti": generate_jti(),  # JWT ID for token tracking/blacklisting
        "type": "access"  
    })
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a long-lived refresh token for token rotation.
    
    Args:
        data: Dictionary containing user claims
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": generate_jti(),
        "type": "refresh"
    })
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token with blacklist checking.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti:
            is_blacklisted = await redis_service.is_token_blacklisted(jti)
            if is_blacklisted:
                return None
                
        return payload
        
    except JWTError:
        return None


def generate_jti() -> str:
    """
    Generate a unique JWT ID for token tracking and blacklisting.
    
    Returns:
        Random string suitable for use as JWT ID
    """
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


def extract_token_from_header(authorization: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value (e.g., "Bearer abc123...")
        
    Returns:
        Token string if valid Bearer format, None otherwise
    """
    if not authorization:
        return None
        
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate a secure token for password reset functionality.
    
    Args:
        email: User's email address
        
    Returns:
        JWT token valid for password reset (shorter expiration)
    """
    data = {"email": email, "type": "password_reset"}
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry for security
    
    to_encode = data.copy()
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": generate_jti()
    })
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)

async def blacklist_token(token: str) -> bool:
    """
    Add token to blacklist in Redis.
    
    Args:
        token: JWT token to blacklist
        
    Returns:
        True if successfully blacklisted, False otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[ALGORITHM],
            options={"verify_exp": False}  # Don't verify expiration for blacklisting
        )
        
        jti = payload.get("jti")
        if not jti:
            return False
        
        # Calculate remaining TTL
        exp = payload.get("exp")
        if exp:
            remaining_seconds = exp - int(datetime.now(timezone.utc).timestamp())
            if remaining_seconds > 0:
                return await redis_service.blacklist_token(jti, remaining_seconds)
        
        return False
        
    except JWTError:
        return False


async def check_login_rate_limit(identifier: str) -> dict:
    """
    Check rate limit for login attempts.
    5 attempts per 15 minutes per IP/email
    
    Args:
        identifier: IP address or email to check
        
    Returns:
        Dictionary with rate limit info
    """
    return await redis_service.check_rate_limit(
        f"login:{identifier}",
        limit=5,
        window=900  # 15 minutes
    )