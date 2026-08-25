#!/usr/bin/env python
"""Check where vectors are stored in ChromaVectorStore"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import the vector store
from app.vectorstore.chroma_store import ChromaVectorStore

# Create an instance
vs = ChromaVectorStore()
print("✅ ChromaVectorStore initialized")
print(f"   In-memory store: {vs._in_memory_store}")
print(f"   Collections cache: {list(vs._collections.keys())}")

# Check if any vectors are stored
if vs._in_memory_store:
    print(f"\n📦 In-Memory Storage Contents:")
    for collection_name, collection_data in vs._in_memory_store.items():
        print(f"\n   Collection: {collection_name}")
        print(f"   - Total vectors: {len(collection_data.get('ids', []))}")
        if collection_data.get('ids'):
            print(f"   - First 3 IDs: {collection_data['ids'][:3]}")
            print(f"   - Document count: {len(collection_data.get('documents', []))}")
            if collection_data.get('documents'):
                print(f"   - First doc preview: {collection_data['documents'][0][:80]}...")
else:
    print("\n❌ In-memory store is empty or not initialized")

print("\n✅ Vector Storage Check Complete")
