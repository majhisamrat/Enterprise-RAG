#!/usr/bin/env python3
"""
Test script to verify KB selection enforcement
Tests three scenarios:
1. 0 KBs exist
2. 1 KB exists (should auto-select)
3. 3+ KBs exist (should require selection)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = ""  # Will be set by login

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def get_auth_token():
    """Login and get auth token"""
    global TOKEN
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        if response.status_code == 200:
            TOKEN = response.json()["access_token"]
            print(f"✓ Authenticated successfully")
            return TOKEN
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None

def test_kb_requirements():
    """Test KB requirements endpoint"""
    print_section("TEST: KB Requirements Endpoint")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(
            f"{BASE_URL}/chat/kb-requirements",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ KB Requirements Retrieved:")
            print(f"  - KB Count: {data['kb_count']}")
            print(f"  - Require Selection: {data['require_kb_selection']}")
            print(f"  - Message: {data['message']}")
            print(f"  - Available KBs: {len(data['kbs'])}")
            for kb in data['kbs']:
                print(f"    • {kb['display_name']} (ID: {kb['id']})")
            return data
        else:
            print(f"✗ Failed to get KB requirements: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_chat_without_kb(query="Hello"):
    """Test chat without KB selection (should fail if 2+ KBs exist)"""
    print_section("TEST: Chat Without KB Selection")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            headers=headers,
            json={
                "query": query,
                "session_id": None,
                "top_k": 10
            }
        )
        
        if response.status_code == 200:
            print(f"✓ Chat succeeded without KB selection")
            print(f"  Response: {response.json()['answer'][:100]}...")
        elif response.status_code == 400:
            print(f"✗ Chat failed with 400 (Expected when 2+ KBs exist)")
            print(f"  Error: {response.json()['detail']}")
        else:
            print(f"✗ Unexpected status: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_chat_with_kb(kb_id, query="Hello"):
    """Test chat with KB selection"""
    print_section(f"TEST: Chat With KB Selection ({kb_id})")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            headers=headers,
            json={
                "query": query,
                "session_id": None,
                "knowledge_base_id": kb_id,
                "top_k": 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Chat succeeded with KB selection:")
            print(f"  - Session ID: {data['session_id']}")
            print(f"  - Answer: {data['answer'][:100]}...")
            if data.get('sources'):
                print(f"  - Sources used: {len(data['sources'])}")
        else:
            print(f"✗ Chat failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def main():
    print("🧪 KB SELECTION ENFORCEMENT TEST SUITE")
    print(f"⏱️  Timestamp: {datetime.now().isoformat()}")
    
    # Step 1: Authenticate
    print_section("STEP 1: Authentication")
    if not get_auth_token():
        print("Cannot proceed without authentication")
        return
    
    # Step 2: Check KB requirements
    print_section("STEP 2: Check KB Requirements")
    kb_data = test_kb_requirements()
    if not kb_data:
        print("Cannot proceed without KB data")
        return
    
    kb_count = kb_data['kb_count']
    require_selection = kb_data['require_kb_selection']
    kbs = kb_data['kbs']
    
    # Step 3: Run scenario-specific tests
    print_section("STEP 3: Scenario-Specific Tests")
    
    if kb_count == 0:
        print("📋 Scenario: 0 KBs exist")
        print("  - Chat input should be disabled")
        print("  - Message: No KBs available")
        test_chat_without_kb()
        
    elif kb_count == 1:
        print("📋 Scenario: 1 KB exists")
        print("  - Should auto-select the KB")
        print("  - Chat input should be enabled")
        if kbs:
            test_chat_with_kb(kbs[0]['id'], f"Tell me about {kbs[0]['display_name']}")
            
    else:  # 2+ KBs
        print(f"📋 Scenario: {kb_count} KBs exist")
        print("  - 'All Knowledge Bases' option removed from dropdown")
        print("  - Chat input should be disabled until selection")
        print("  - Chat without KB selection should fail with 400")
        
        # Test without KB selection
        test_chat_without_kb()
        
        # Test with KB selection
        if kbs:
            for kb in kbs[:2]:  # Test with first 2 KBs
                test_chat_with_kb(kb['id'], f"Tell me about {kb['display_name']}")
    
    print_section("TEST SUITE COMPLETE")
    print("✅ All tests completed")

if __name__ == "__main__":
    main()
