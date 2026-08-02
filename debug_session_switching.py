#!/usr/bin/env python3
"""
Debug script to test automatic session switching functionality.

This script will help us understand exactly what's happening when KB switches occur.
"""

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your_test_token"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def debug_session_info(session_id):
    """Get detailed session information for debugging."""
    if not session_id:
        return None
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/session/{session_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get session info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting session info: {e}")
        return None

def test_session_switching_step_by_step():
    """
    Test session switching with detailed debugging at each step.
    """
    print("🔍 DEBUGGING AUTOMATIC SESSION SWITCHING")
    print("=" * 60)
    
    # Test with actual KB IDs from your system
    # You'll need to replace these with real KB IDs from your system
    sales_kb_id = "539acc6d-310f-41fe-93e6-849f064fc8be"  # From your log
    ops_kb_id = "different-kb-id-here"  # Create a second KB for testing
    
    print(f"📋 Using KB IDs:")
    print(f"   Sales KB: {sales_kb_id}")
    print(f"   Ops KB: {ops_kb_id}")
    
    # Step 1: First query with Sales KB (no session)
    print(f"\n🚀 STEP 1: First query in Sales KB")
    chat_request_1 = {
        "query": "What are the sales numbers?",
        "knowledge_base_id": sales_kb_id,
        # No session_id - should create new session
    }
    
    print(f"📤 Request: {json.dumps(chat_request_1, indent=2)}")
    
    response_1 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_1, headers=headers)
    print(f"📥 Response Status: {response_1.status_code}")
    
    if response_1.status_code == 200:
        result_1 = response_1.json()
        session_1 = result_1["session_id"]
        kb_1 = result_1["knowledge_base_id"]
        session_changed_1 = result_1.get("session_changed", False)
        
        print(f"✅ SUCCESS:")
        print(f"   Session ID: {session_1}")
        print(f"   KB ID: {kb_1}")
        print(f"   Session Changed: {session_changed_1}")
        
        # Get detailed session info
        session_info = debug_session_info(session_1)
        if session_info:
            print(f"   Session Details: {json.dumps(session_info, indent=4)}")
    else:
        print(f"❌ FAILED: {response_1.text}")
        return
    
    print(f"\n" + "-" * 40)
    
    # Step 2: Continue in same KB
    print(f"\n🔄 STEP 2: Continue in SAME Sales KB")
    chat_request_2 = {
        "query": "Tell me more about those numbers",
        "knowledge_base_id": sales_kb_id,  # SAME KB
        "session_id": session_1,  # CONTINUE session
    }
    
    print(f"📤 Request: {json.dumps(chat_request_2, indent=2)}")
    
    response_2 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_2, headers=headers)
    print(f"📥 Response Status: {response_2.status_code}")
    
    if response_2.status_code == 200:
        result_2 = response_2.json()
        session_2 = result_2["session_id"]
        kb_2 = result_2["knowledge_base_id"]
        session_changed_2 = result_2.get("session_changed", False)
        
        print(f"✅ SUCCESS:")
        print(f"   Session ID: {session_2}")
        print(f"   KB ID: {kb_2}")
        print(f"   Session Changed: {session_changed_2}")
        print(f"   Same Session? {session_2 == session_1}")
        
        if session_2 == session_1:
            print(f"   ✅ EXPECTED: Same session continued")
        else:
            print(f"   ⚠️ UNEXPECTED: New session created")
    else:
        print(f"❌ FAILED: {response_2.text}")
        return
    
    print(f"\n" + "-" * 40)
    
    # Step 3: Switch to different KB (this should create new session)
    print(f"\n🔀 STEP 3: Switch to DIFFERENT KB")
    chat_request_3 = {
        "query": "What are the operational procedures?",
        "knowledge_base_id": ops_kb_id,  # DIFFERENT KB
        "session_id": session_1,  # Try to use old session
    }
    
    print(f"📤 Request: {json.dumps(chat_request_3, indent=2)}")
    print(f"🎯 EXPECTED: New session should be created automatically")
    
    response_3 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_3, headers=headers)
    print(f"📥 Response Status: {response_3.status_code}")
    
    if response_3.status_code == 200:
        result_3 = response_3.json()
        session_3 = result_3["session_id"]
        kb_3 = result_3["knowledge_base_id"]
        session_changed_3 = result_3.get("session_changed", False)
        
        print(f"✅ SUCCESS:")
        print(f"   Session ID: {session_3}")
        print(f"   KB ID: {kb_3}")
        print(f"   Session Changed: {session_changed_3}")
        print(f"   Different Session? {session_3 != session_1}")
        
        if session_3 != session_1:
            print(f"   ✅ EXPECTED: New session created for KB switch")
            print(f"   🔄 {session_1} → {session_3}")
        else:
            print(f"   ❌ PROBLEM: Same session used despite KB change")
            
        # Get detailed session info
        session_info = debug_session_info(session_3)
        if session_info:
            print(f"   New Session Details: {json.dumps(session_info, indent=4)}")
    else:
        print(f"❌ FAILED: {response_3.text}")
        return
    
    print(f"\n" + "-" * 40)
    
    # Step 4: Switch to "All Knowledge Bases" (None)
    print(f"\n🌐 STEP 4: Switch to 'All Knowledge Bases'")
    chat_request_4 = {
        "query": "What are the key priorities?",
        # No knowledge_base_id = "All Knowledge Bases"
        "session_id": session_3,  # Try to use ops session
    }
    
    print(f"📤 Request: {json.dumps(chat_request_4, indent=2)}")
    print(f"🎯 EXPECTED: New session should be created automatically")
    
    response_4 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_4, headers=headers)
    print(f"📥 Response Status: {response_4.status_code}")
    
    if response_4.status_code == 200:
        result_4 = response_4.json()
        session_4 = result_4["session_id"]
        kb_4 = result_4.get("knowledge_base_id")
        session_changed_4 = result_4.get("session_changed", False)
        
        print(f"✅ SUCCESS:")
        print(f"   Session ID: {session_4}")
        print(f"   KB ID: {kb_4 or 'None (All KBs)'}")
        print(f"   Session Changed: {session_changed_4}")
        print(f"   Different Session? {session_4 != session_3}")
        
        if session_4 != session_3:
            print(f"   ✅ EXPECTED: New session created for All KBs")
            print(f"   🔄 {session_3} → {session_4}")
        else:
            print(f"   ❌ PROBLEM: Same session used despite KB change")
    else:
        print(f"❌ FAILED: {response_4.text}")
        return
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 SESSION SWITCHING SUMMARY")
    print("=" * 60)
    print(f"Step 1 - Sales KB (new):     {session_1}")
    print(f"Step 2 - Sales KB (continue): {session_2} {'✅' if session_2 == session_1 else '❌'}")
    print(f"Step 3 - Ops KB (switch):     {session_3} {'✅' if session_3 != session_1 else '❌'}")  
    print(f"Step 4 - All KBs (switch):    {session_4} {'✅' if session_4 != session_3 else '❌'}")
    
    # Recommendations
    print(f"\n🔧 TROUBLESHOOTING:")
    if session_2 != session_1:
        print(f"❌ Issue: Step 2 created new session instead of continuing")
        print(f"   Check: KB comparison logic in backend")
    
    if session_3 == session_1:
        print(f"❌ Issue: Step 3 didn't create new session for KB switch")
        print(f"   Check: KB change detection logic")
        print(f"   Check: Session comparison in backend logs")
    
    if session_4 == session_3:
        print(f"❌ Issue: Step 4 didn't create new session for All KBs switch")
        print(f"   Check: None vs UUID comparison logic")

def test_force_new_session():
    """Test the force_new_session parameter"""
    print(f"\n🔧 TESTING FORCE NEW SESSION")
    print("=" * 40)
    
    # Force new session
    chat_request = {
        "query": "Test query with forced new session",
        "knowledge_base_id": "539acc6d-310f-41fe-93e6-849f064fc8be",
        "force_new_session": True
    }
    
    print(f"📤 Request: {json.dumps(chat_request, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request, headers=headers)
    print(f"📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS:")
        print(f"   Session ID: {result['session_id']}")
        print(f"   Session Changed: {result.get('session_changed', False)}")
        print(f"   Expected: session_changed should be True")
    else:
        print(f"❌ FAILED: {response.text}")

if __name__ == "__main__":
    print("🔍 Session Switching Debug Tool")
    print(f"Timestamp: {datetime.now()}")
    print("")
    
    print("📝 SETUP INSTRUCTIONS:")
    print("1. Make sure your server is running")
    print("2. Update TOKEN in this script")
    print("3. Create 2 different KBs and update the KB IDs")
    print("4. Run this script and check the results")
    print("")
    
    print("Uncomment the lines below to run tests:")
    # test_session_switching_step_by_step()
    # test_force_new_session()
    
    print("\n💡 TIP: Check your server logs while running this")
    print("Look for messages like '🔄 KB changed' and '✨ Created NEW session'")