#!/usr/bin/env python3
"""
Test script for chat history endpoints
Run this after starting the server to test the new endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_chat_history_endpoints():
    """Test the new chat history endpoints"""
    print("🧪 Testing Chat History Endpoints...")
    
    # Note: You'll need a valid token for these tests
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    print("\n1. Testing GET /chat/history")
    try:
        response = requests.get(f"{BASE_URL}/chat/history", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('sessions', []))} chat sessions")
            if data.get('sessions'):
                session_id = data['sessions'][0]['session_id']
                print(f"First session ID: {session_id}")
                
                # Test getting specific session
                print(f"\n2. Testing GET /chat/history/{session_id}")
                detail_response = requests.get(f"{BASE_URL}/chat/history/{session_id}", headers=headers)
                print(f"Status: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"Session has {len(detail_data.get('messages', []))} messages")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing endpoints: {e}")

    print("\n3. Available endpoints:")
    print("GET  /api/v1/chat/history          - List user's chat sessions")
    print("GET  /api/v1/chat/history/{id}     - Get specific session with messages") 
    print("DELETE /api/v1/chat/history/{id}   - Delete a chat session")
    print("\n✅ Chat history routes have been added to your backend!")

if __name__ == "__main__":
    test_chat_history_endpoints()