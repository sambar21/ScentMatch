# backend/app/core/security.py
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.core.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_jti() -> str:
    """Generate a unique JWT ID."""
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
    )


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": generate_jti(),
            "type": "access",
        }
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": generate_jti(),
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Decode JWT and verify type; no blacklist check."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


def extract_token_from_header(authorization: str) -> Optional[str]:
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
    """Generate a short-lived token for password reset."""
    data = {"email": email, "type": "password_reset"}
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode = data.copy()
    to_encode.update(
        {"exp": expire, "iat": datetime.now(timezone.utc), "jti": generate_jti()}
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


# ===== Optional: Simple in-memory login rate limit (single instance) =====
login_attempts: Dict[str, list[int]] = {}  # identifier -> list of attempt timestamps


def check_login_rate_limit(
    identifier: str, limit: int = 5, window_minutes: int = 15
) -> dict:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    window_sec = window_minutes * 60
    attempts = login_attempts.get(identifier, [])

    # Keep only attempts in window
    attempts = [ts for ts in attempts if ts > now_ts - window_sec]
    allowed = len(attempts) < limit
    remaining = max(0, limit - len(attempts))

    # Record this attempt if allowed
    if allowed:
        attempts.append(now_ts)
        login_attempts[identifier] = attempts

    return {
        "allowed": allowed,
        "remaining": remaining,
        "reset_time": now_ts + window_sec,
    }
