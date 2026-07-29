# API Changes - Enterprise RAG Redesign

## Summary

All changes are **additive** (new endpoints/parameters). Existing endpoints remain functional for backward compatibility.

---

## New Endpoints (Knowledge Base Management)

### Create Knowledge Base
```http
POST /api/v1/knowledge
Content-Type: application/json

{
  "name": "sales_kb",
  "display_name": "Sales Documents KB",
  "description": "Knowledge base containing sales materials and processes"
}

Response (201):
{
  "id": "uuid",
  "organization_id": "uuid",
  "name": "sales_kb",
  "display_name": "Sales Documents KB",
  "status": "active",
  "created_at": "2026-07-25T10:30:00Z"
}
```

### List Knowledge Bases
```http
GET /api/v1/knowledge?skip=0&limit=100

Response (200):
{
  "knowledge_bases": [
    {
      "id": "uuid",
      "name": "sales_kb",
      "display_name": "Sales Documents KB",
      "status": "active",
      "created_at": "2026-07-25T10:30:00Z",
      "last_queried_at": "2026-07-26T14:00:00Z",
      "statistics": {
        "total_uploads": 5,
        "total_pages": 324,
        "total_chunks": 1200,
        "total_vectors": 1200,
        "query_count": 42
      }
    }
  ],
  "total": 5
}
```

### Get Knowledge Base Details
```http
GET /api/v1/knowledge/{kb_id}

Response (200):
{
  "id": "uuid",
  "name": "sales_kb",
  "display_name": "Sales Documents KB",
  "status": "active",
  "created_at": "2026-07-25T10:30:00Z",
  "last_queried_at": "2026-07-26T14:00:00Z",
  "uploads": [
    {
      "id": "uuid",
      "filename": "sales_book.pdf",
      "upload_date": "2026-07-25T10:30:00Z",
      "page_count": 150,
      "chunk_count": 500,
      "vector_count": 500,
      "status": "completed"
    }
  ]
}
```

### Delete Knowledge Base
```http
DELETE /api/v1/knowledge/{kb_id}

Response (200):
{
  "success": true,
  "kb_id": "uuid",
  "message": "Knowledge base deleted with cascading uploads and vectors"
}
```

---

## New Endpoints (Upload Management)

### Upload to Knowledge Base
```http
POST /api/v1/knowledge/{kb_id}/upload
Content-Type: multipart/form-data

file: <binary pdf/docx/txt>
display_name: "Sales Book 2026"
tags: "sales,2026,Q3"
department: "Sales"

Response (202):
{
  "success": true,
  "upload_id": "uuid",
  "kb_id": "uuid",
  "filename": "sales_book.pdf",
  "status": "processing",
  "job_id": "celery-job-id",
  "message": "Upload queued for processing"
}
```

### Get Upload History
```http
GET /api/v1/knowledge/{kb_id}/history?skip=0&limit=50

Response (200):
{
  "kb_id": "uuid",
  "uploads": [
    {
      "id": "uuid",
      "filename": "sales_book.pdf",
      "display_name": "Sales Book 2026",
      "upload_date": "2026-07-25T10:30:00Z",
      "file_size_bytes": 2048000,
      "pages": 150,
      "chunks": 500,
      "vectors": 500,
      "embedding_model": "BAAI/bge-small-en-v1.5",
      "status": "completed",
      "processing_time_ms": 15000,
      "tags": ["sales", "2026", "Q3"]
    }
  ],
  "total": 12
}
```

### Get KB Statistics
```http
GET /api/v1/knowledge/{kb_id}/statistics

Response (200):
{
  "kb_id": "uuid",
  "kb_name": "sales_kb",
  "statistics": {
    "total_uploads": 12,
    "completed_uploads": 11,
    "failed_uploads": 1,
    "total_pages": 1800,
    "total_chunks": 6000,
    "total_vectors": 6000,
    "total_queries": 342,
    "avg_query_latency_ms": 245,
    "last_queried_at": "2026-07-26T14:00:00Z"
  }
}
```

### Reindex Knowledge Base
```http
POST /api/v1/knowledge/{kb_id}/reindex

Response (200):
{
  "success": true,
  "kb_id": "uuid",
  "kb_name": "sales_kb",
  "uploads_count": 12,
  "job_id": "celery-job-id",
  "status": "PENDING",
  "message": "Reindexing queued for 12 uploads in KB 'sales_kb'"
}
```

---

## Enhanced Endpoints (Chat)

### Chat Endpoint - Enhanced Request
```http
POST /api/v1/chat
Content-Type: application/json

{
  "query": "Compare July and August sales",
  "knowledge_base_id": "uuid-optional",
  "session_id": "uuid-optional",
  "top_k": 10
}
```

**New Parameter**: `knowledge_base_id` (optional UUID)
- If provided: Search only vectors from this KB
- If omitted: Search all KBs (backward compatible)

### Chat Endpoint - Enhanced Response
```json
{
  "answer": "Based on the sales data from July and August...",
  "session_id": "uuid",
  "knowledge_base_id": "uuid-if-filtered",
  "sources": [
    {
      "citation_key": "[Source 1]",
      "document_id": "uuid",
      "upload_id": "uuid",
      "document_name": "sales_book.pdf",
      "upload_date": "2026-07-25T10:30:00Z",
      "title": "Sales Book 2026",
      "page_number": 42,
      "text_snippet": "Sales in July reached $2.5M with...",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "model": "gemini-2.5-flash",
    "prompt_tokens": 2048,
    "completion_tokens": 512,
    "total_tokens": 2560,
    "latency_ms": 245,
    "context_documents": 5,
    "kb_filtered": true,
    "used_uploads": ["upload-uuid-1", "upload-uuid-2"]
  }
}
```

**New Response Fields**:
- `knowledge_base_id`: Which KB was filtered (if any)
- `sources[].upload_id`: Upload ID (NEW)
- `sources[].document_name`: Original filename (NEW)
- `sources[].upload_date`: When document was uploaded (NEW)
- `metadata.kb_filtered`: Boolean indicating KB filter was applied (NEW)
- `metadata.used_uploads`: List of upload IDs used in results (NEW)

---

## New Analytics Endpoints

### Dashboard Summary
```http
GET /api/v1/analytics/dashboard

Response (200):
{
  "organization_id": "uuid",
  "timestamp": "2026-07-26T14:00:00Z",
  "summary": {
    "total_knowledge_bases": 5,
    "total_uploads": 42,
    "total_pages": 5000,
    "total_chunks": 18000,
    "total_vectors": 18000,
    "total_queries": 1200
  },
  "knowledge_bases": [
    {
      "id": "uuid",
      "name": "sales_kb",
      "display_name": "Sales Documents KB",
      "status": "active",
      "created_at": "2026-07-25T10:30:00Z",
      "last_queried_at": "2026-07-26T14:00:00Z",
      "statistics": { ... },
      "latest_uploads": [
        {
          "id": "uuid",
          "filename": "sales_book.pdf",
          "upload_date": "2026-07-25T10:30:00Z",
          "pages": 150,
          "chunks": 500,
          "vectors": 500,
          "status": "completed"
        }
      ]
    }
  ]
}
```

### Query Analytics
```http
GET /api/v1/analytics/queries?days=7&kb_id=uuid-optional&limit=100

Response (200):
{
  "organization_id": "uuid",
  "period_days": 7,
  "timestamp": "2026-07-26T14:00:00Z",
  "summary": {
    "total_queries": 342,
    "avg_latency_ms": 245.5,
    "avg_retrieved_chunks": 5.2,
    "total_retrieved_chunks": 1782
  },
  "by_knowledge_base": {
    "sales_kb": {
      "query_count": 200,
      "avg_latency_ms": 210,
      "avg_retrieved": 5.5
    },
    "ops_kb": {
      "query_count": 142,
      "avg_latency_ms": 290,
      "avg_retrieved": 4.8
    }
  },
  "recent_queries": [
    {
      "id": "uuid",
      "query": "Compare July and August sales...",
      "knowledge_base_id": "uuid",
      "retrieved_count": 6,
      "latency_ms": 215,
      "used_uploads": ["upload-1", "upload-2"],
      "created_at": "2026-07-26T13:55:00Z"
    }
  ]
}
```

### Usage Analytics
```http
GET /api/v1/analytics/usage?days=30

Response (200):
{
  "organization_id": "uuid",
  "period_days": 30,
  "timestamp": "2026-07-26T14:00:00Z",
  "summary": {
    "total_queries": 5420,
    "total_chat_messages": 8500,
    "total_uploads": 156,
    "total_pages_indexed": 25000,
    "total_vectors": 90000,
    "avg_upload_processing_time_ms": 12500,
    "queries_per_day": 180.67,
    "messages_per_day": 283.33
  },
  "daily_breakdown": [
    {
      "date": "2026-07-26",
      "query_count": 185,
      "retrieved_chunks": 960,
      "avg_latency_ms": 248
    }
  ]
}
```

### KB Detailed Statistics
```http
GET /api/v1/analytics/knowledge-bases/{kb_id}/detailed

Response (200):
{
  "kb_id": "uuid",
  "kb_name": "sales_kb",
  "kb_display_name": "Sales Documents KB",
  "created_at": "2026-07-25T10:30:00Z",
  "last_queried_at": "2026-07-26T14:00:00Z",
  "status": "active",
  "statistics": {
    "total_uploads": 12,
    "completed_uploads": 11,
    "failed_uploads": 1,
    "total_pages": 1800,
    "total_chunks": 6000,
    "total_vectors": 6000,
    "total_queries": 342,
    "avg_upload_time_ms": 12500,
    "avg_query_latency_ms": 245
  },
  "uploads": [
    {
      "id": "uuid",
      "filename": "sales_book.pdf",
      "display_name": "Sales Book 2026",
      "file_type": "application/pdf",
      "file_size_bytes": 2048000,
      "pages": 150,
      "chunks": 500,
      "vectors": 500,
      "embedding_model": "BAAI/bge-small-en-v1.5",
      "status": "completed",
      "processing_time_ms": 15000,
      "error": null,
      "created_at": "2026-07-25T10:30:00Z",
      "tags": ["sales", "2026", "Q3"]
    }
  ],
  "recent_queries": [
    {
      "query": "What were the top selling products in July?",
      "retrieved_count": 6,
      "latency_ms": 215,
      "created_at": "2026-07-26T13:55:00Z"
    }
  ]
}
```

### Performance Metrics
```http
GET /api/v1/analytics/performance?days=7

Response (200):
{
  "organization_id": "uuid",
  "period_days": 7,
  "timestamp": "2026-07-26T14:00:00Z",
  "query_metrics": {
    "total_queries": 1200,
    "avg_latency_ms": 245.5,
    "p50_latency_ms": 210,
    "p95_latency_ms": 485,
    "p99_latency_ms": 650,
    "avg_retrieved_chunks": 5.2
  },
  "upload_metrics": {
    "total_uploads": 42,
    "avg_processing_time_ms": 12500,
    "p50_processing_time_ms": 10000,
    "p95_processing_time_ms": 25000,
    "failed_uploads": 2
  }
}
```

---

## Backward Compatibility

### Deprecated but Functional: /documents Routes

```http
POST /api/v1/documents/upload

# Still works, creates uploads in "default" KB
# Response includes upload_id, status, etc.
```

**Note**: Files uploaded via old `/documents` endpoint are associated with a default KB per organization.

---

## QueryLog Tracking

Automatically created for each chat query:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "organization_id": "uuid",
  "knowledge_base_id": "uuid-or-null",
  "query_text": "Full query text",
  "retrieved_count": 6,
  "latency_ms": 245,
  "used_upload_ids": ["upload-1", "upload-2"],
  "created_at": "2026-07-26T13:55:00Z"
}
```

---

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2026-07-26T14:00:00Z"
}
```

Common status codes:
- **400**: Invalid input (bad UUID, missing required fields)
- **401**: Unauthorized (no auth token)
- **403**: Forbidden (KB doesn't belong to org)
- **404**: Not found (KB/upload/resource doesn't exist)
- **500**: Server error
- **202**: Accepted (async processing queued)

---

## Rate Limiting & Pagination

- **Pagination**: `skip` (default 0) and `limit` (default 100, max 1000)
- **Rate limiting**: Applied per organization
- **Query timeouts**: 30s for analytics, 60s for reindex

---

## Migration Guide for Clients

### For Frontend (if using chat endpoint):

**Before**:
```javascript
const response = await fetch('/api/v1/chat', {
  method: 'POST',
  body: JSON.stringify({
    query: "What is the sales process?"
  })
})
```

**After (with KB filtering)**:
```javascript
const response = await fetch('/api/v1/chat', {
  method: 'POST',
  body: JSON.stringify({
    query: "What is the sales process?",
    knowledge_base_id: "selected-kb-id"  // Optional
  })
})
```

**Response includes new fields**:
```javascript
const data = await response.json()
data.knowledge_base_id  // NEW
data.sources[0].upload_id  // NEW
data.sources[0].document_name  // NEW
data.sources[0].upload_date  // NEW
data.metadata.kb_filtered  // NEW
data.metadata.used_uploads  // NEW
```

---

## Testing Endpoints

Use the provided E2E test suite:

```bash
pytest tests/test_enterprise_rag_e2e.py -v
```

Or manually with curl:

```bash
# Create KB
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "test_kb",
    "display_name": "Test KB"
  }'

# List KBs
curl http://localhost:8000/api/v1/knowledge \
  -H "Authorization: Bearer <token>"

# Upload document
curl -X POST http://localhost:8000/api/v1/knowledge/{kb_id}/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf"

# Chat with KB filter
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "What is the process?",
    "knowledge_base_id": "{kb_id}"
  }'

# Dashboard
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer <token>"
```

---

## Complete API Reference

See `API_FLOWS.md` for detailed request/response examples.
