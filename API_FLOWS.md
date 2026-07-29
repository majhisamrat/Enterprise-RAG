# API Flow Documentation

## 1. UPLOAD FLOW (Multi-Step)

### Step 1: Create Knowledge Base (First Time)

```
POST /api/v1/knowledge
{
  "name": "Sales_Q3_2026",
  "display_name": "Sales Q3 2026",
  "description": "Revenue data from Q3"
}

Response:
{
  "id": "kb_uuid_001",
  "name": "Sales_Q3_2026",
  "created_at": "2026-07-25T10:00:00Z",
  "status": "active"
}
```

**Database Change:**
```
INSERT INTO knowledge_bases (id, org_id, user_id, name, display_name, ...)
```

### Step 2: Upload Document to Knowledge Base

```
POST /api/v1/knowledge/{kb_id}/upload
(multipart/form-data)
{
  "file": <file.pdf>,
  "display_name": "July_Sales_Book"  // optional, defaults to filename
}

Response:
{
  "upload_id": "upload_uuid_001",
  "kb_id": "kb_uuid_001",
  "status": "PROCESSING",
  "filename": "sales_book.pdf",
  "created_at": "2026-07-25T10:30:00Z"
}
```

**Database Changes:**
```
1. INSERT INTO uploads (
     id, kb_id, org_id, user_id,
     filename, file_type, storage_path,
     processing_status = 'PROCESSING',
     created_at
   )

2. CREATE Celery task: process_document_ingestion_task
   Parameters: {
     upload_id, file_path, kb_id, org_id, user_id
   }
```

### Step 3: Background Ingestion (Async)

```
[Celery Worker Task]

1. Parse PDF
   - Extract text, OCR, clean
   - Identify pages: 45 pages

2. Chunk (Recursive)
   - Split into 128 chunks
   - Overlap: 20%

3. Embed
   - Model: BAAI/bge-small-en-v1.5
   - Dimension: 384
   - 128 vectors created

4. Index in Qdrant
   - Collection: enterprise_documents_kb_uuid_001
   - Upsert 128 points with metadata:
     {
       "chunk_id": "chunk_001_kb_uuid_001",
       "upload_id": "upload_uuid_001",
       "knowledge_base_id": "kb_uuid_001",
       "organization_id": "org_uuid_001",
       "user_id": "user_uuid_001",
       "document_name": "sales_book.pdf",
       "upload_date": "2026-07-25",
       "page_number": 1,
       "chunk_number": 1,
       "chunk_text": "...",
       "embedding_model": "BAAI/bge-small-en-v1.5"
     }

5. Index in Elasticsearch
   - Index: enterprise_documents_kb_uuid_001
   - Index all 128 chunks for BM25 search

6. Update Upload record
   UPDATE uploads SET
     processing_status = 'COMPLETED',
     page_count = 45,
     chunk_count = 128,
     total_vectors = 128,
     processing_end_at = NOW(),
     processing_duration_ms = 2500

7. Increment KB query_count = 0, last_queried_at = null
```

### Step 4: Check Upload Status

```
GET /api/v1/knowledge/{kb_id}/history

Response:
{
  "uploads": [
    {
      "id": "upload_uuid_001",
      "filename": "sales_book.pdf",
      "display_name": "July_Sales_Book",
      "upload_date": "2026-07-25T10:30:00Z",
      "status": "COMPLETED",
      "page_count": 45,
      "chunk_count": 128,
      "total_vectors": 128,
      "embedding_model": "BAAI/bge-small-en-v1.5",
      "processing_duration_ms": 2500,
      "file_size_bytes": 5242880
    }
  ]
}
```

---

## 2. CHAT FLOW (With KB Filtering)

### Scenario A: Chat Without KB Filter (Across All KBs)

```
POST /api/v1/chat
{
  "query": "What were the sales in July?",
  "session_id": "session_uuid_001",
  "top_k": 5
}

Step 1: Retrieve or Create Session
  IF session_id:
    - Fetch ChatSession + last 6 messages (context window)
  ELSE:
    - Create new ChatSession
    - kb_id = null (cross-all-KBs search)

Step 2: Hybrid Retrieval (NO KB FILTER)
  HybridRetriever.retrieve(
    query: "What were the sales in July?",
    limit: 5,
    organization_id: org_uuid_001,
    filters: {
      organization_id: org_uuid_001
      // NO kb_id filter → searches all KBs
    }
  )
  
  Qdrant Query:
    SELECT TOP 5 vectors
    WHERE organization_id == org_uuid_001
    ORDER BY similarity DESC
  
  Returns:
  [
    {
      "chunk_id": "chunk_001_kb_uuid_001",
      "upload_id": "upload_uuid_001",
      "kb_id": "kb_uuid_001",
      "document_name": "sales_book.pdf",
      "upload_date": "2026-07-25",
      "text": "July sales totaled $2.5M",
      "score": 0.92
    },
    ...
  ]

Step 3: Build Prompt with Context
  PromptBuilder.build(
    query: "What were the sales in July?",
    documents: [5 chunks above],
    conversation_history: [last 6 messages]
  )

Step 4: Generate LLM Response
  LLM.generate(prompt)
  → "Based on the July sales document, July sales totaled $2.5M"

Step 5: Persist to Database
  INSERT INTO chat_messages (
    session_id, role='user', content='What were the sales in July?'
  )
  INSERT INTO chat_messages (
    session_id, role='assistant', content='Based on...'
  )
  INSERT INTO query_logs (
    user_id, org_id, kb_id=null,
    query='What were the sales in July?',
    retrieved_count=5,
    used_upload_ids=['upload_uuid_001'],
    latency_ms=450
  )

Response:
{
  "answer": "Based on the July sales document, July sales totaled $2.5M",
  "session_id": "session_uuid_001",
  "sources": [
    {
      "upload_id": "upload_uuid_001",
      "document_name": "sales_book.pdf",
      "upload_date": "2026-07-25",
      "page_number": 1,
      "snippet": "July sales totaled $2.5M",
      "score": 0.92
    }
  ],
  "metadata": {
    "latency_ms": 450,
    "tokens_used": 284,
    "retrieved_chunks": 5
  }
}
```

### Scenario B: Chat WITH KB Filter (Single KB)

```
POST /api/v1/chat
{
  "query": "Compare July and August sales",
  "session_id": "session_uuid_002",
  "knowledge_base_id": "kb_uuid_001",
  "top_k": 5
}

Step 2 (Modified): Hybrid Retrieval WITH KB FILTER
  HybridRetriever.retrieve(
    query: "Compare July and August sales",
    limit: 5,
    organization_id: org_uuid_001,
    filters: {
      organization_id: org_uuid_001,
      knowledge_base_id: kb_uuid_001  // ← FILTER
    }
  )
  
  Qdrant Query:
    SELECT TOP 5 vectors
    WHERE organization_id == org_uuid_001
      AND knowledge_base_id == kb_uuid_001
    ORDER BY similarity DESC

  Returns only vectors from uploads in kb_uuid_001:
  [
    {
      "chunk_id": "chunk_045_kb_uuid_001",
      "upload_id": "upload_uuid_001",  // July
      "kb_id": "kb_uuid_001",
      "document_name": "sales_book.pdf",
      "upload_date": "2026-07-25",
      "text": "July sales totaled $2.5M",
      "score": 0.94
    },
    {
      "chunk_id": "chunk_089_kb_uuid_001",
      "upload_id": "upload_uuid_002",  // August
      "kb_id": "kb_uuid_001",
      "document_name": "loss_book.pdf",
      "upload_date": "2026-08-20",
      "text": "August sales totaled $3.1M",
      "score": 0.91
    },
    ...
  ]

Rest of flow same as Scenario A

INSERT INTO query_logs (
  user_id, org_id, kb_id=kb_uuid_001,  // ← KB specified
  query='Compare July and August sales',
  retrieved_count=5,
  used_upload_ids=['upload_uuid_001', 'upload_uuid_002'],
  latency_ms=420
)
```

---

## 3. RETRIEVAL FLOW (Hybrid Search)

### Detailed Retrieval Process

```
HybridRetriever.retrieve(
  query: "What were Q3 revenues?",
  limit: 5,
  organization_id: org_uuid_001,
  knowledge_base_id: kb_uuid_001 (optional)
)

┌─ PHASE 1: Concurrent Dense + Sparse Search ─────────────────────┐
│                                                                   │
│  Thread 1: Dense Search (Qdrant)                                 │
│  ├─ Embed query using BAAI/bge-small-en-v1.5 → [384 dims]       │
│  ├─ Search Qdrant collection:                                    │
│  │  WHERE org_id == org_uuid_001 AND kb_id == kb_uuid_001        │
│  ├─ Return TOP 10 candidates with scores:                        │
│  │  [                                                            │
│  │    {chunk_id, upload_id, text, score: 0.92, source: dense}   │
│  │    {chunk_id, upload_id, text, score: 0.88, source: dense}   │
│  │    ...                                                        │
│  │  ]                                                            │
│  │                                                               │
│  Thread 2: Sparse Search (Elasticsearch)                         │
│  ├─ Parse query terms: ["Q3", "revenues"]                        │
│  ├─ BM25 search Elasticsearch index:                             │
│  │  WHERE org_id == org_uuid_001 AND kb_id == kb_uuid_001        │
│  ├─ Return TOP 10 candidates with BM25 scores:                   │
│  │  [                                                            │
│  │    {chunk_id, upload_id, text, score: 42.5, source: sparse}  │
│  │    {chunk_id, upload_id, text, score: 38.2, source: sparse}  │
│  │    ...                                                        │
│  │  ]                                                            │
│                                                                   │
└─ PHASE 2: Reciprocal Rank Fusion (RRF) ──────────────────────────┘

RRF combines dense + sparse scores:
  RRF_score = (1 / (k + rank_dense)) + (1 / (k + rank_sparse))
  where k = 60 (constant)

Merge and deduplicate by chunk_id:
[
  {chunk_id, upload_id, text, dense_score: 0.92, sparse_score: 42.5, rrf_score: 0.034},
  {chunk_id, upload_id, text, dense_score: 0.88, sparse_score: 38.2, rrf_score: 0.031},
  ...
]

Sort by RRF_score DESC → TOP 5 candidates

┌─ PHASE 3: Cross-Encoder Reranking (Optional) ────────────────────┐
│                                                                    │
│ IF settings.ENABLE_RERANKER:                                       │
│   ├─ Load BGE Reranker (cross-encoder)                            │
│   ├─ For each TOP 6 candidates:                                   │
│   │   Rerank(query, chunk_text) → relevance_score 0-1             │
│   ├─ Return TOP 5 by rerank score                                 │
│                                                                    │
│ ELSE:                                                              │
│   └─ Return TOP 5 by RRF score                                    │
│                                                                    │
└─ PHASE 4: Final Results ─────────────────────────────────────────┘

Final Retrieved Documents:
[
  {
    "chunk_id": "chunk_045_kb_uuid_001",
    "upload_id": "upload_uuid_001",
    "knowledge_base_id": "kb_uuid_001",
    "document_name": "sales_book.pdf",
    "upload_date": "2026-07-25",
    "page_number": 5,
    "text": "Q3 revenues reached $7.8M with 45% YoY growth",
    "dense_score": 0.92,
    "sparse_score": 42.5,
    "rrf_score": 0.034,
    "final_score": 0.89  // After reranking
  },
  ...
]
```

---

## 4. REINDEX FLOW

### Scenario: Reindex Single Knowledge Base

```
POST /api/v1/knowledge/{kb_id}/reindex

Step 1: Fetch KB + All Uploads
  SELECT kb FROM knowledge_bases WHERE id = kb_id
  SELECT uploads FROM uploads WHERE kb_id = kb_id
  
  uploads = [
    {id: upload_uuid_001, filename: sales_book.pdf, ...},
    {id: upload_uuid_002, filename: loss_book.pdf, ...}
  ]

Step 2: For Each Upload
  FOR upload IN uploads:
    
    2a. Fetch Original File
        IF storage_path exists:
          Read file from disk/S3
        ELSE:
          ERROR: "Original file deleted, cannot reindex"
    
    2b. Re-process Document
        Parse → Chunk → Embed (same as upload flow)
        NEW 128 vectors created
    
    2c. Delete Old Vectors
        DELETE FROM qdrant_collection
          WHERE upload_id == upload_uuid_001
        DELETE FROM elasticsearch_index
          WHERE upload_id == upload_uuid_001
    
    2d. Insert New Vectors
        Upsert 128 new vectors to Qdrant + Elasticsearch
        WITH updated:
          embedding_model: (potentially new model)
          embedding_dimension: (potentially new dimension)
          created_at: NOW()
    
    2e. Update Upload Record
        UPDATE uploads SET
          processing_status = 'COMPLETED',
          chunk_count = 128,  // Might differ if chunking changed
          total_vectors = 128,
          processing_duration_ms = 2400,
          updated_at = NOW()

Step 3: Update KB Metadata
  UPDATE knowledge_bases SET
    updated_at = NOW(),
    last_reindexed_at = NOW()

Step 4: Return Summary
{
  "kb_id": "kb_uuid_001",
  "status": "REINDEX_COMPLETED",
  "uploads_reindexed": 2,
  "total_vectors_created": 256,
  "duration_ms": 4800,
  "errors": []
}
```

---

## 5. DELETE KNOWLEDGE BASE FLOW

### Cascading Delete

```
DELETE /api/v1/knowledge/{kb_id}

Step 1: Fetch KB
  SELECT kb FROM knowledge_bases WHERE id = kb_id

Step 2: Delete Related Data (Cascade)
  
  2a. Delete Uploads + Vectors
      SELECT uploads FROM uploads WHERE kb_id = kb_id
      FOR upload IN uploads:
        - Delete from Qdrant collection
        - Delete from Elasticsearch index
        - Delete embedding_collections records
        - Delete vector_metadata records
      DELETE FROM uploads WHERE kb_id = kb_id
  
  2b. Delete Chat Sessions
      SELECT sessions FROM chat_sessions WHERE kb_id = kb_id
      FOR session IN sessions:
        - Delete chat_messages
        - Delete query_logs
      DELETE FROM chat_sessions WHERE kb_id = kb_id
  
  2c. Delete Query Logs
      DELETE FROM query_logs WHERE kb_id = kb_id
  
  2d. Delete KB
      DELETE FROM knowledge_bases WHERE id = kb_id

Step 3: Response
{
  "status": "DELETED",
  "kb_id": "kb_uuid_001",
  "deleted_uploads": 2,
  "deleted_vectors": 256,
  "deleted_messages": 45
}

Other KBs unaffected ✓
```

---

## 6. DASHBOARD FLOW

### Get Knowledge Base Summary

```
GET /api/v1/dashboard

Response:
{
  "knowledge_bases": [
    {
      "id": "kb_uuid_001",
      "name": "Sales_2026",
      "display_name": "Sales Q1-Q4 2026",
      "created_at": "2026-01-15T10:00:00Z",
      "last_queried_at": "2026-07-25T14:30:00Z",
      "query_count": 156,
      "uploads": {
        "total": 2,
        "total_pages": 89,
        "total_chunks": 256,
        "total_vectors": 256,
        "average_processing_time_ms": 2400
      },
      "latest_uploads": [
        {
          "id": "upload_uuid_002",
          "filename": "loss_book.pdf",
          "upload_date": "2026-08-20T09:30:00Z",
          "pages": 44,
          "chunks": 128,
          "vectors": 128,
          "status": "COMPLETED"
        },
        {
          "id": "upload_uuid_001",
          "filename": "sales_book.pdf",
          "upload_date": "2026-07-25T10:30:00Z",
          "pages": 45,
          "chunks": 128,
          "vectors": 128,
          "status": "COMPLETED"
        }
      ]
    }
  ],
  "total_kbs": 1,
  "total_vectors": 256,
  "total_queries": 156,
  "last_query_at": "2026-07-25T14:30:00Z"
}
```

---

End of API Flow Documentation
