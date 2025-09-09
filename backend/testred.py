# test_security.py
import asyncio
from app.core.security import create_access_token, verify_token, blacklist_token
from app.services.redis_service import redis_service

async def test_security():
    await redis_service.connect()
    
    # Create a test token
    token_data = {"sub": "test-user", "email": "test@example.com"}
    token = create_access_token(token_data)
    print(f"Created token: {token[:50]}...")
    
    # Verify token works
    payload = await verify_token(token, "access")
    print(f"Token verified: {payload['sub'] if payload else 'FAILED'}")
    
    # Blacklist token
    success = await blacklist_token(token)
    print(f"Token blacklisted: {success}")
    
    # Try to verify blacklisted token
    payload = await verify_token(token, "access")
    print(f"Blacklisted token verified: {'FAILED - GOOD!' if not payload else 'PROBLEM - Still valid'}")
    
    await redis_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_security())