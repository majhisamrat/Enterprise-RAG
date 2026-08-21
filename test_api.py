#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Register new user
register_data = {
    "name": "Test User 3",
    "email": "test3@example.com",
    "password": "TestPass123!",
    "organization_name": "Test Organization",
    "department": "Engineering"
}

print("Registering user...")
register_resp = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"Status: {register_resp.status_code}")

if register_resp.status_code == 200:
    token_data = register_resp.json()
    token = token_data.get("access_token")
    print(f"Got token: {token[:50]}...")
    
    # Test chat endpoint
    chat_data = {
        "query": "how many unit product sold in total?",
        "knowledge_base_id": ""
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\nTesting chat endpoint...")
    chat_resp = requests.post(f"{BASE_URL}/chat", json=chat_data, headers=headers, timeout=30)
    print(f"Status: {chat_resp.status_code}")
    print(f"Response:\n{json.dumps(chat_resp.json(), indent=2)}")
else:
    print(f"Registration failed: {register_resp.text}")
