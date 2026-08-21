import requests
import sys
import time

try:
    print("Testing health...")
    resp = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"Health: {resp.status_code}")
    
    print("\nRegistering user...")
    timestamp = int(time.time())
    reg_resp = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json={
            "name": f"User{timestamp}",
            "email": f"user{timestamp}@test.com",
            "password": "Pass123!",
            "organization_name": "Org",
            "department": "Eng"
        },
        timeout=10
    )
    print(f"Register: {reg_resp.status_code}")
    
    if reg_resp.status_code == 200:
        token = reg_resp.json().get("access_token")
        print(f"Token: {token[:30]}...")
        
        print("\nTesting chat...")
        chat_resp = requests.post(
            "http://localhost:8000/api/v1/chat",
            json={
                "query": "how many unit product sold in total?",
                "knowledge_base_id": ""
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=30
        )
        print(f"Chat: {chat_resp.status_code}")
        if chat_resp.status_code == 200:
            data = chat_resp.json()
            print(f"Answer: {data.get('answer', 'N/A')[:200]}")
        else:
            print(f"Error: {chat_resp.text[:200]}")
    else:
        print(f"Register error: {reg_resp.text[:200]}")
        
except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
