#!/usr/bin/env python
"""Minimal test for Chroma without full app context"""

import sys

print("Testing Chroma import...")
try:
    import chromadb
    print("✅ chromadb imported")
    
    print("Creating ephemeral client...")
    client = chromadb.EphemeralClient()
    print("✅ EphemeralClient created")
    
    print("Creating test collection...")
    collection = client.get_or_create_collection(
        name="test_collection",
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ Collection created")
    
    print("Upserting test data...")
    collection.upsert(
        ids=["doc1", "doc2"],
        embeddings=[[0.1, 0.2], [0.3, 0.4]],
        documents=["Test doc 1", "Test doc 2"],
        metadatas=[{"type": "test"}, {"type": "test"}]
    )
    print("✅ Data upserted")
    
    print("Querying...")
    results = collection.query(
        query_embeddings=[[0.1, 0.2]],
        n_results=2
    )
    print(f"✅ Query returned {len(results['ids'][0])} results")
    
    print("\n✅ ALL TESTS PASSED!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
