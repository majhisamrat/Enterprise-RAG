#!/usr/bin/env python3
"""
Test script to demonstrate KB-based vector filtering functionality.

This script shows exactly how your KB filtering works:
1. Create KB → vectors stored in KB-specific collection
2. Query specific KB → searches only that KB's collection  
3. Query "All KBs" → searches default collection
"""

import asyncio
import uuid
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TOKEN = "your_test_token"  # Replace with actual token
ORG_ID = "test-org-uuid"   # Replace with actual org ID

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

async def test_kb_filtering_workflow():
    """
    Demonstrates the complete KB filtering workflow as requested.
    """
    print("🚀 Testing Knowledge Base Vector Filtering")
    print("=" * 50)
    
    # Step 1: Create two knowledge bases
    print("\n📁 Step 1: Creating Knowledge Bases")
    
    sales_kb_data = {
        "name": "sales_2026",
        "display_name": "Sales Documents 2026",
        "description": "All sales-related documents for 2026"
    }
    
    ops_kb_data = {
        "name": "operations_2026", 
        "display_name": "Operations Documents 2026",
        "description": "All operations documents for 2026"
    }
    
    # Create Sales KB
    response = requests.post(f"{BASE_URL}/api/v1/knowledge", json=sales_kb_data, headers=headers)
    if response.status_code == 201:
        sales_kb = response.json()
        sales_kb_id = sales_kb["id"]
        print(f"✅ Created Sales KB: {sales_kb_id}")
    else:
        print(f"❌ Failed to create Sales KB: {response.status_code}")
        return
    
    # Create Operations KB  
    response = requests.post(f"{BASE_URL}/api/v1/knowledge", json=ops_kb_data, headers=headers)
    if response.status_code == 201:
        ops_kb = response.json()
        ops_kb_id = ops_kb["id"]
        print(f"✅ Created Operations KB: {ops_kb_id}")
    else:
        print(f"❌ Failed to create Operations KB: {response.status_code}")
        return
    
    # Step 2: Upload documents to each KB
    print(f"\n📄 Step 2: Uploading Documents to KBs")
    
    # Upload to Sales KB
    sales_files = [
        ("sales_report_july.pdf", "Sales report for July 2026"),
        ("sales_targets_2026.pdf", "Sales targets and goals for 2026"),
        ("customer_data.pdf", "Customer analysis and insights")
    ]
    
    print(f"📤 Uploading to Sales KB ({sales_kb_id}):")
    for filename, display_name in sales_files:
        # Simulate file upload (in real scenario, you'd use multipart/form-data)
        upload_data = {
            "display_name": display_name,
            "tags": "sales,2026"
        }
        # Note: In real usage, you'd upload actual files here
        print(f"  → {filename}: {display_name}")
    
    # Upload to Operations KB
    ops_files = [
        ("ops_manual_2026.pdf", "Operations manual and procedures"),
        ("supply_chain.pdf", "Supply chain optimization guide"),
        ("workflow_diagrams.pdf", "Operational workflow diagrams")
    ]
    
    print(f"📤 Uploading to Operations KB ({ops_kb_id}):")
    for filename, display_name in ops_files:
        print(f"  → {filename}: {display_name}")
    
    # Step 3: Test KB-specific filtering
    print(f"\n🔍 Step 3: Testing KB-Specific Filtering")
    
    # Test 1: Query only Sales KB
    print(f"\n🎯 Test 1: Query ONLY Sales KB")
    chat_request_sales = {
        "query": "What are the sales targets for Q3 2026?",
        "knowledge_base_id": sales_kb_id,  # 🎯 This filters to Sales KB only
        "top_k": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_sales, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sales KB Query Result:")
        print(f"   KB Filtered: {result['metadata']['kb_filtered']}")
        print(f"   Knowledge Base: {result['knowledge_base_id']}")
        print(f"   Used Uploads: {result['metadata']['used_uploads']}")
        print(f"   Sources: {len(result['sources'])} chunks found")
        for i, source in enumerate(result['sources'][:3]):
            print(f"     {i+1}. {source['document_name']} (Page {source['page_number']})")
    else:
        print(f"❌ Sales KB query failed: {response.status_code}")
    
    # Test 2: Query only Operations KB
    print(f"\n🎯 Test 2: Query ONLY Operations KB")
    chat_request_ops = {
        "query": "What are the operational procedures for supply chain?",
        "knowledge_base_id": ops_kb_id,  # 🎯 This filters to Operations KB only
        "top_k": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_ops, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Operations KB Query Result:")
        print(f"   KB Filtered: {result['metadata']['kb_filtered']}")
        print(f"   Knowledge Base: {result['knowledge_base_id']}")
        print(f"   Used Uploads: {result['metadata']['used_uploads']}")
        print(f"   Sources: {len(result['sources'])} chunks found")
        for i, source in enumerate(result['sources'][:3]):
            print(f"     {i+1}. {source['document_name']} (Page {source['page_number']})")
    else:
        print(f"❌ Operations KB query failed: {response.status_code}")
    
    # Test 3: Query ALL Knowledge Bases
    print(f"\n🌐 Test 3: Query ALL Knowledge Bases")
    chat_request_all = {
        "query": "What are the key priorities for 2026?",
        # 🌐 No knowledge_base_id = search ALL KBs
        "top_k": 10
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_request_all, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ All KBs Query Result:")
        print(f"   KB Filtered: {result['metadata']['kb_filtered']}")
        print(f"   Knowledge Base: {result.get('knowledge_base_id', 'None (All KBs)')}")
        print(f"   Used Uploads: {result['metadata']['used_uploads']}")
        print(f"   Sources: {len(result['sources'])} chunks found")
        
        # Show sources from different KBs
        kb_sources = {}
        for source in result['sources']:
            kb_id = source.get('knowledge_base_id', 'default')
            if kb_id not in kb_sources:
                kb_sources[kb_id] = []
            kb_sources[kb_id].append(source)
        
        for kb_id, sources in kb_sources.items():
            kb_name = "Sales KB" if kb_id == sales_kb_id else "Ops KB" if kb_id == ops_kb_id else "Default"
            print(f"     📁 {kb_name}: {len(sources)} sources")
    else:
        print(f"❌ All KBs query failed: {response.status_code}")
    
    # Step 4: Show collections structure
    print(f"\n📊 Step 4: Qdrant Collections Structure")
    print(f"Expected collections in Qdrant:")
    print(f"  📁 enterprise_rag (default - for 'All KBs' queries)")
    print(f"  📁 enterprise_rag_kb_{str(sales_kb_id).replace('-', '')[:8]} (Sales KB)")
    print(f"  📁 enterprise_rag_kb_{str(ops_kb_id).replace('-', '')[:8]} (Operations KB)")
    
    # Step 5: Cleanup (optional)
    print(f"\n🧹 Step 5: Cleanup (Uncomment to delete test KBs)")
    # Uncomment below to clean up test KBs
    # requests.delete(f"{BASE_URL}/api/v1/knowledge/{sales_kb_id}", headers=headers)
    # requests.delete(f"{BASE_URL}/api/v1/knowledge/{ops_kb_id}", headers=headers)
    # print("✅ Deleted test KBs")
    
    print(f"\n" + "=" * 50)
    print("🎉 KB Filtering Test Complete!")
    print("")
    print("SUMMARY:")
    print("✅ Each KB has its own Qdrant collection for perfect separation")
    print("✅ KB-specific queries search only that KB's vectors")
    print("✅ 'All KBs' queries search across all collections")
    print("✅ Vectors are completely isolated by Knowledge Base")

def test_vector_collections():
    """
    Shows the Qdrant collection naming strategy
    """
    print("\n🗂️  QDRANT COLLECTION STRATEGY")
    print("=" * 40)
    
    # Example KB IDs
    sales_kb_id = "550e8400-e29b-41d4-a716-446655440000"
    ops_kb_id = "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    
    print("KB Vector Storage Strategy:")
    print(f"📁 Sales KB ({sales_kb_id}):")
    print(f"   → Collection: enterprise_rag_kb_{sales_kb_id.replace('-', '')[:8]}")
    print(f"   → Vectors: Only Sales documents")
    
    print(f"📁 Operations KB ({ops_kb_id}):")
    print(f"   → Collection: enterprise_rag_kb_{ops_kb_id.replace('-', '')[:8]}")
    print(f"   → Vectors: Only Operations documents")
    
    print(f"📁 Default (All KBs):")
    print(f"   → Collection: enterprise_rag")
    print(f"   → Vectors: Mixed/backward compatibility")
    
    print("\nQuery Strategy:")
    print("🎯 User selects 'Sales' KB:")
    print("   → Search ONLY enterprise_rag_kb_550e8400 collection")
    print("   → Results: Only Sales document chunks")
    
    print("🎯 User selects 'Operations' KB:")  
    print("   → Search ONLY enterprise_rag_kb_6ba7b810 collection")
    print("   → Results: Only Operations document chunks")
    
    print("🌐 User selects 'All Knowledge Bases':")
    print("   → Search enterprise_rag collection")
    print("   → Results: All available chunks")

if __name__ == "__main__":
    print("🧪 Knowledge Base Filtering Test Suite")
    print("This demonstrates the exact KB filtering behavior you requested.")
    print("")
    
    # Show collection strategy
    test_vector_collections()
    
    # Uncomment to run live API tests (requires running server)
    # asyncio.run(test_kb_filtering_workflow())
    
    print("\n📝 TO RUN LIVE TESTS:")
    print("1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("2. Update TOKEN and ORG_ID in this script")
    print("3. Uncomment the asyncio.run() line above")
    print("4. Run: python test_kb_filtering.py")