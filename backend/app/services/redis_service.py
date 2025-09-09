# app/services/redis_service.py
import redis.asyncio as redis
from typing import Optional
import json
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self._redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            # Test connection
            await self._redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._redis = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance"""
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._redis
    
    # Token Blacklisting Methods
    async def blacklist_token(self, token_jti: str, expires_in: int):
        """Add token to blacklist"""
        try:
            await self.client.setex(
                f"blacklist:{token_jti}", 
                expires_in, 
                "blacklisted"
            )
            logger.info(f"Token blacklisted: {token_jti}")
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """Check if token is blacklisted"""
        try:
            result = await self.client.get(f"blacklist:{token_jti}")
            return result is not None
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False
    
    # Rate Limiting Methods
    async def check_rate_limit(self, key: str, limit: int, window: int) -> dict:
        """
        Check rate limit using sliding window
        Returns: {"allowed": bool, "remaining": int, "reset_time": int}
        """
        try:
            current_time = int(datetime.utcnow().timestamp())
            pipeline = self.client.pipeline()
            
            # Remove expired entries
            pipeline.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipeline.expire(key, window)
            
            results = await pipeline.execute()
            current_requests = results[1]
            
            if current_requests >= limit:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": current_time + window
                }
            
            return {
                "allowed": True,
                "remaining": limit - current_requests - 1,
                "reset_time": current_time + window
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if Redis is down
            return {"allowed": True, "remaining": limit - 1, "reset_time": 0}
    
    # Session Management
    async def store_session(self, session_id: str, user_data: dict, expires_in: int):
        """Store user session data"""
        try:
            await self.client.setex(
                f"session:{session_id}",
                expires_in,
                json.dumps(user_data)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data"""
        try:
            data = await self.client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        try:
            await self.client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    # Cache Methods (for future use with file metadata, etc.)
    async def set_cache(self, key: str, value: str, expires_in: int = 3600):
        """Set cache value with expiration"""
        try:
            await self.client.setex(key, expires_in, value)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[str]:
        """Get cache value"""
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache: {e}")
            return None

# Global Redis instance
redis_service = RedisService()