# backend/app/middleware/security_middleware.py
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import asyncio
from collections import defaultdict, deque
from app.middleware.simple_logging import get_correlation_id
from app.core.structured_logger import get_logger

logger = get_logger("security")

class RateLimiter:
    """In-memory rate limiter (use Redis in real production)"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> tuple[bool, int]:
        """Check if request is allowed, return (allowed, remaining_requests)"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        client_requests = self.requests[client_id]
        while client_requests and client_requests[0] < minute_ago:
            client_requests.popleft()
        
        # Check if limit exceeded
        if len(client_requests) >= self.requests_per_minute:
            return False, 0
        
        # Add current request
        client_requests.append(now)
        remaining = self.requests_per_minute - len(client_requests)
        
        return True, remaining

# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)  # 100 requests per minute

async def security_middleware(request: Request, call_next):
    """Security middleware with rate limiting and headers"""
    
    # Get client identifier
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    client_id = f"{client_ip}:{hash(user_agent) % 10000}"
    
    # Check rate limit
    allowed, remaining = rate_limiter.is_allowed(client_id)
    
    if not allowed:
        correlation_id = get_correlation_id()
        
        # Log rate limit hit
        logger.warning(
            "Rate limit exceeded",
            extra={
                "correlation_id": correlation_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "event_type": "rate_limit_exceeded"
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED", 
                    "message": "Too many requests. Please try again later.",
                    "correlation_id": correlation_id,
                    "retry_after": 60
                }
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + 60))
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    response.headers.update({
        # Rate limiting info
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(time.time() + 60)),
        
        # Security headers
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # API info
        "X-API-Version": "1.0.0",
        "X-Powered-By": "FastAPI"  # You might want to remove this in production
    })
    
    return response

async def request_size_middleware(request: Request, call_next):
    """Limit request size to prevent abuse"""
    
    max_size = 10 * 1024 * 1024  # 10MB limit
    content_length = request.headers.get("content-length")
    
    if content_length and int(content_length) > max_size:
        correlation_id = get_correlation_id()
        
        logger.warning(
            "Request size too large",
            extra={
                "correlation_id": correlation_id,
                "content_length": content_length,
                "max_allowed": max_size,
                "client_ip": request.client.host if request.client else "unknown",
                "event_type": "request_too_large"
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "error": {
                    "code": "REQUEST_TOO_LARGE",
                    "message": f"Request size exceeds maximum of {max_size} bytes",
                    "correlation_id": correlation_id
                }
            }
        )
    
    return await call_next(request)