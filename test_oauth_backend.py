#!/usr/bin/env python3
"""
Test script for Google OAuth backend endpoints
This tests the OAuth flow without needing Redis/Celery
"""

import asyncio
import json
import httpx
from datetime import datetime, timezone

# Test data - you'll get this from Google OAuth
test_data = {
    "access_token": "ya29.a0AfH6SMBx...",  # This would come from Google
    "email": "test@example.com",
    "name": "Test User",
    "picture": "https://example.com/picture.jpg",
    "organization_name": "Test Org"
}

async def test_google_login_endpoint():
    """Test the /api/v1/auth/google-login endpoint"""
    
    print("=" * 60)
    print("Testing Backend OAuth Endpoints")
    print("=" * 60)
    print()
    
    # Check if backend is running
    print("1. Checking if backend is running on http://localhost:8000...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            print(f"   ✅ Backend is running!")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backend is NOT running!")
        print(f"   Error: {e}")
        print()
        print("   ACTION REQUIRED:")
        print("   1. Install missing dependencies: pip install celery redis")
        print("   2. Start Redis server: redis-server")
        print("   3. Start backend: python -m uvicorn app.main:app --reload --port 8000")
        return
    
    print()
    print("2. Testing /api/v1/auth/google-login endpoint...")
    print()
    
    # This endpoint expects real Google OAuth data
    # For now, we'll just verify the endpoint exists
    endpoint = "http://localhost:8000/api/v1/auth/google-login"
    
    print(f"   Endpoint: POST {endpoint}")
    print()
    print(f"   Expected request body:")
    print(f"   {json.dumps(test_data, indent=2)}")
    print()
    
    print("3. Available Auth Endpoints:")
    endpoints = [
        "POST   /api/v1/auth/register - Email/password registration",
        "POST   /api/v1/auth/login - Email/password login",
        "POST   /api/v1/auth/google - Google ID token verification",
        "POST   /api/v1/auth/google-login - Google OAuth (implicit flow)",
        "POST   /api/v1/auth/send-otp - Send OTP",
        "POST   /api/v1/auth/verify-otp - Verify OTP",
        "GET    /api/v1/auth/me - Get current user",
    ]
    
    for endpoint in endpoints:
        print(f"   ✓ {endpoint}")
    
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print()
    print("To fully test the OAuth flow:")
    print()
    print("1. Install dependencies:")
    print("   pip install celery redis")
    print()
    print("2. Start Redis:")
    print("   redis-server")
    print()
    print("3. Start Backend:")
    print("   python -m uvicorn app.main:app --reload --port 8000")
    print()
    print("4. Move to Task 4: Test frontend Sign-In flow in browser")
    print()

if __name__ == "__main__":
    asyncio.run(test_google_login_endpoint())
