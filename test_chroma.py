#!/usr/bin/env python
"""Quick test to verify Chroma vector store is working"""

import sys
import uuid
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_chroma():
    from app.vectorstore.chroma_store import ChromaVectorStore
    from app.ingestion.schemas import ChunkedDocument, Chunk
    
    print("✅ Testing Chroma Vector Store")
    
    # Initialize vector store
    vector_store = ChromaVectorStore()
    print("✅ ChromaVectorStore initialized")
    
    # Test document and chunks
    test_chunks = [
        Chunk(text="Employee EMP001: John Doe, Department: HR", embedding=[0.1] * 384),
        Chunk(text="Employee EMP002: Jane Smith, Department: Engineering", embedding=[0.2] * 384),
        Chunk(text="Employee EMP003: Bob Johnson, Department: Sales", embedding=[0.3] * 384),
    ]
    
    test_doc = ChunkedDocument(chunks=test_chunks)
    
    # Test upsert
    org_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    kb_id = uuid.uuid4()
    upload_id = uuid.uuid4()
    
    print(f"\nTesting upsert to KB {kb_id}...")
    await vector_store.upsert_document_chunks(
        document=test_doc,
        document_id=doc_id,
        organization_id=org_id,
        upload_id=upload_id,
        knowledge_base_id=kb_id,
        document_name="test_roster.pdf",
    )
    print("✅ Upserted 3 test chunks")
    
    # Test search
    print(f"\nTesting search for 'Employee EMP001'...")
    query_embedding = [0.1] * 384
    results = vector_store.search(
        query_embedding=query_embedding,
        limit=10,
        organization_id=org_id,
        knowledge_base_id=kb_id,
    )
    
    print(f"✅ Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result['score']:.4f} | Text: {result['text'][:60]}...")
    
    # Test delete
    print(f"\nTesting delete for upload {upload_id}...")
    deleted = await vector_store.delete_vectors_by_upload(upload_id, kb_id)
    print(f"✅ Deleted vectors")
    
    # Verify deletion
    results_after = vector_store.search(
        query_embedding=query_embedding,
        limit=10,
        organization_id=org_id,
        knowledge_base_id=kb_id,
    )
    print(f"✅ Verified deletion: {len(results_after)} results remaining (expected 0)")
    
    if len(results_after) == 0:
        print("\n✅ All Chroma tests PASSED!")
        return True
    else:
        print("\n❌ Delete test FAILED - vectors still present")
        return False

if __name__ == "__main__":
    import asyncio
    try:
        success = asyncio.run(test_chroma())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
