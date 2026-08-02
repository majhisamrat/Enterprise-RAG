#!/usr/bin/env python3
"""
Test script to demonstrate automatic new session creation when KB changes.

This shows how the chat system now automatically creates a new session
when the user switches between different knowledge bases.
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your_test_token"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_auto_new_session():
    """
    Demonstrates automatic new session creation on KB switch.
    """
    print("🧪 Testing Automatic New Session Creation on KB Switch")
    print("=" * 60)
    
    # Scenario: User starts chat in Sales KB, then switches to Operations KB
    
    # Step 1: First query in Sales KB
    print("\n📋 Step 1: First query in Sales KB")
    
    sales_kb_id = "550e8400-e29b-41d4-a716-446655440000"  # Example Sales KB
    
    chat_request_1 = {
        "query": "What are the Q3 sales targets?",
        "knowledge_base_id": sales_kb_id,
        # No session_id - will create new session
    }
    
    print(f"🔹 Query: {chat_request_1['query']}")
    print(f"🔹 KB: Sales ({sales_kb_id})")
    print(f"🔹 Session: None (new session will be created)")
    
    response_1 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_1, headers=headers)
    
    if response_1.status_code == 200:
        result_1 = response_1.json()
        session_1 = result_1["session_id"]
        kb_1 = result_1["knowledge_base_id"]
        
        print(f"✅ Response:")
        print(f"   📝 Session ID: {session_1}")
        print(f"   📁 Knowledge Base: {kb_1}")
        print(f"   🎯 KB Filtered: {result_1['metadata']['kb_filtered']}")
        print(f"   💬 Answer: {result_1['answer'][:100]}...")
    else:
        print(f"❌ First query failed: {response_1.status_code}")
        return
    
    # Step 2: Continue conversation in same KB
    print(f"\n📋 Step 2: Follow-up query in SAME KB")
    
    chat_request_2 = {
        "query": "Can you provide more details about those targets?",
        "knowledge_base_id": sales_kb_id,  # Same KB
        "session_id": session_1,  # Continue same session
    }
    
    print(f"🔹 Query: {chat_request_2['query']}")
    print(f"🔹 KB: Sales ({sales_kb_id}) - SAME KB")
    print(f"🔹 Session: {session_1} - CONTINUE EXISTING")
    
    response_2 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_2, headers=headers)
    
    if response_2.status_code == 200:
        result_2 = response_2.json()
        session_2 = result_2["session_id"]
        
        print(f"✅ Response:")
        print(f"   📝 Session ID: {session_2}")
        
        if session_2 == session_1:
            print(f"   ✅ SAME SESSION - Conversation continued")
        else:
            print(f"   ⚠️ NEW SESSION - Unexpected")
    else:
        print(f"❌ Second query failed: {response_2.status_code}")
        return
    
    # Step 3: Switch to different KB - should auto-create new session
    print(f"\n📋 Step 3: Switch to DIFFERENT KB")
    
    ops_kb_id = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"  # Example Operations KB
    
    chat_request_3 = {
        "query": "What are the operational procedures?",
        "knowledge_base_id": ops_kb_id,  # DIFFERENT KB
        "session_id": session_1,  # Try to use old session
    }
    
    print(f"🔹 Query: {chat_request_3['query']}")
    print(f"🔹 KB: Operations ({ops_kb_id}) - DIFFERENT KB")
    print(f"🔹 Session: {session_1} - FROM SALES KB")
    print(f"🔹 Expected: Auto-create NEW session")
    
    response_3 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_3, headers=headers)
    
    if response_3.status_code == 200:
        result_3 = response_3.json()
        session_3 = result_3["session_id"]
        kb_3 = result_3["knowledge_base_id"]
        
        print(f"✅ Response:")
        print(f"   📝 Session ID: {session_3}")
        print(f"   📁 Knowledge Base: {kb_3}")
        
        if session_3 != session_1:
            print(f"   ✨ NEW SESSION CREATED - KB switch detected!")
            print(f"   🔄 {session_1} (Sales) → {session_3} (Operations)")
        else:
            print(f"   ⚠️ SAME SESSION - Auto-creation failed")
            
        print(f"   🎯 KB Filtered: {result_3['metadata']['kb_filtered']}")
        print(f"   💬 Answer: {result_3['answer'][:100]}...")
    else:
        print(f"❌ Third query failed: {response_3.status_code}")
        return
    
    # Step 4: Switch to "All Knowledge Bases"
    print(f"\n📋 Step 4: Switch to 'All Knowledge Bases'")
    
    chat_request_4 = {
        "query": "What are the key priorities across all departments?",
        # No knowledge_base_id = "All Knowledge Bases"
        "session_id": session_3,  # Try to use Operations session
    }
    
    print(f"🔹 Query: {chat_request_4['query']}")
    print(f"🔹 KB: All Knowledge Bases (None)")
    print(f"🔹 Session: {session_3} - FROM OPERATIONS KB")
    print(f"🔹 Expected: Auto-create NEW session")
    
    response_4 = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_4, headers=headers)
    
    if response_4.status_code == 200:
        result_4 = response_4.json()
        session_4 = result_4["session_id"]
        kb_4 = result_4.get("knowledge_base_id", None)
        
        print(f"✅ Response:")
        print(f"   📝 Session ID: {session_4}")
        print(f"   📁 Knowledge Base: {kb_4 or 'All KBs'}")
        
        if session_4 != session_3:
            print(f"   ✨ NEW SESSION CREATED - KB switch detected!")
            print(f"   🔄 {session_3} (Operations) → {session_4} (All KBs)")
        else:
            print(f"   ⚠️ SAME SESSION - Auto-creation failed")
            
        print(f"   🎯 KB Filtered: {result_4['metadata']['kb_filtered']}")
        print(f"   💬 Answer: {result_4['answer'][:100]}...")
    else:
        print(f"❌ Fourth query failed: {response_4.status_code}")
        return
    
    # Summary
    print(f"\n" + "=" * 60)
    print("📊 SESSION CREATION SUMMARY")
    print("=" * 60)
    print(f"Session 1 (Sales KB):      {session_1}")
    print(f"Session 2 (Sales KB):      {session_2} {'✅ Same' if session_2 == session_1 else '❌ Different'}")
    print(f"Session 3 (Operations KB): {session_3} {'✅ New' if session_3 != session_1 else '❌ Same'}")
    print(f"Session 4 (All KBs):       {session_4} {'✅ New' if session_4 != session_3 else '❌ Same'}")
    
    print(f"\n🎯 EXPECTED BEHAVIOR:")
    print(f"✅ Same KB = Same Session (continue conversation)")
    print(f"✅ Different KB = New Session (fresh context)")
    print(f"✅ KB Switch = Auto-detect and create new session")

def show_workflow():
    """Show the workflow diagram"""
    print("🔄 AUTOMATIC NEW SESSION WORKFLOW")
    print("=" * 50)
    print("")
    print("User Flow:")
    print("1. 👤 User chats in 'Sales' KB")
    print("   → 📝 Session A created")
    print("")
    print("2. 👤 User continues in 'Sales' KB") 
    print("   → 📝 Session A continued (same context)")
    print("")
    print("3. 👤 User switches to 'Operations' KB")
    print("   → 🔍 Backend detects KB change")
    print("   → ✨ Session B auto-created")
    print("   → 🚀 Fresh conversation context")
    print("")
    print("4. 👤 User switches to 'All Knowledge Bases'")
    print("   → 🔍 Backend detects KB change") 
    print("   → ✨ Session C auto-created")
    print("   → 🌐 Global context")
    print("")
    print("Benefits:")
    print("✅ Clean context separation by KB")
    print("✅ No mixed conversation history")
    print("✅ Automatic - no manual session management")
    print("✅ Seamless user experience")

if __name__ == "__main__":
    print("🧪 Automatic New Session Creation Test")
    print("")
    
    # Show workflow
    show_workflow()
    
    print("\n📝 TO RUN LIVE TESTS:")
    print("1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("2. Update TOKEN in this script")
    print("3. Create some test KBs and get their IDs")
    print("4. Update KB IDs in the test")
    print("5. Run: python test_auto_new_session.py")
    print("")
    print("Uncomment the line below to run live test:")
    # test_auto_new_session()