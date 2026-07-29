# Quick Start Guide - Enterprise RAG

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Qdrant (vector DB)
- Elasticsearch (optional, for BM25 search)
- Redis (for Celery)
- Celery worker running

---

## 1. Database Setup

### Run Alembic Migration

```bash
# Apply all migrations
alembic upgrade head

# Verify migration
psql -U postgres -d enterprise_rag -c "\dt"
```

You should see new tables:
- `knowledge_bases`
- `uploads`
- `embedding_collections`
- `query_logs`
- `vector_metadata`

---

## 2. Data Migration (Optional)

If you have existing documents, migrate them to the new schema:

```bash
python scripts/migrate_documents_to_uploads.py
```

This will:
- Create default KB per organization
- Backfill Upload records from existing Documents
- Verify data consistency

---

## 3. Create Your First Knowledge Base

```bash
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "sales_2026",
    "display_name": "2026 Sales Documents",
    "description": "Sales materials and policies for 2026"
  }'
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "organization_id": "org-uuid",
  "name": "sales_2026",
  "display_name": "2026 Sales Documents",
  "status": "active",
  "created_at": "2026-07-25T10:30:00Z"
}
```

Save the `id` for next steps.

---

## 4. Upload Documents

```bash
KB_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8000/api/v1/knowledge/$KB_ID/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sales_book.pdf" \
  -F "display_name=Sales Book 2026" \
  -F "tags=sales,2026,Q3"
```

**Response**:
```json
{
  "success": true,
  "upload_id": "upload-uuid",
  "kb_id": "550e8400...",
  "filename": "sales_book.pdf",
  "status": "processing",
  "job_id": "celery-job-id",
  "message": "Upload queued for processing"
}
```

The file is now being processed asynchronously. Check status with:

```bash
curl http://localhost:8000/api/v1/knowledge/$KB_ID/history \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. Chat with KB Filter

Once the document is processed (status: `completed`), query it:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "What are the top sales targets for 2026?",
    "knowledge_base_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 10
  }'
```

**Response**:
```json
{
  "answer": "Based on the 2026 sales documents, the top targets are...",
  "session_id": "session-uuid",
  "knowledge_base_id": "550e8400...",
  "sources": [
    {
      "citation_key": "[Source 1]",
      "document_name": "sales_book.pdf",
      "upload_date": "2026-07-25T10:30:00Z",
      "page_number": 42,
      "relevance_score": 0.92,
      "text_snippet": "Top sales targets for 2026 include..."
    }
  ],
  "metadata": {
    "latency_ms": 245,
    "kb_filtered": true,
    "used_uploads": ["upload-uuid"],
    "context_documents": 5
  }
}
```

---

## 6. View Analytics Dashboard

```bash
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq
```

Shows:
- All KBs in organization
- Upload statistics
- Query counts
- Performance metrics

---

## 7. Check KB Statistics

```bash
KB_ID="550e8400-e29b-41d4-a716-446655440000"

curl http://localhost:8000/api/v1/knowledge/$KB_ID/statistics \
  -H "Authorization: Bearer $TOKEN" | jq
```

Output:
```json
{
  "kb_id": "550e8400...",
  "kb_name": "sales_2026",
  "statistics": {
    "total_uploads": 1,
    "completed_uploads": 1,
    "failed_uploads": 0,
    "total_pages": 150,
    "total_chunks": 500,
    "total_vectors": 500,
    "total_queries": 3,
    "avg_query_latency_ms": 245
  }
}
```

---

## 8. Upload Another Document to Same KB

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/$KB_ID/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@policies_2026.pdf" \
  -F "display_name=2026 Policies" \
  -F "tags=policies,compliance"
```

Now queries will search both documents:

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "Compare sales targets with compliance policies",
    "knowledge_base_id": "550e8400...",
    "top_k": 15
  }'
```

Response will include chunks from both uploads with `used_uploads` showing both IDs.

---

## 9. Reindex Knowledge Base

If you need to re-process all documents in a KB:

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/$KB_ID/reindex \
  -H "Authorization: Bearer $TOKEN"
```

**Response**:
```json
{
  "success": true,
  "kb_id": "550e8400...",
  "kb_name": "sales_2026",
  "uploads_count": 2,
  "job_id": "celery-job-id",
  "status": "PENDING",
  "message": "Reindexing queued for 2 uploads in KB 'sales_2026'"
}
```

The reindex job will:
1. Delete old vectors from Qdrant
2. Re-chunk and re-embed documents
3. Re-index to vector store
4. Update upload status

---

## 10. Query Analytics

```bash
# Last 7 days of queries
curl "http://localhost:8000/api/v1/analytics/queries?days=7" \
  -H "Authorization: Bearer $TOKEN" | jq

# Last 30 days of usage
curl "http://localhost:8000/api/v1/analytics/usage?days=30" \
  -H "Authorization: Bearer $TOKEN" | jq

# KB-specific details
curl "http://localhost:8000/api/v1/analytics/knowledge-bases/$KB_ID/detailed" \
  -H "Authorization: Bearer $TOKEN" | jq

# Performance metrics
curl "http://localhost:8000/api/v1/analytics/performance?days=7" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## 11. List All Knowledge Bases

```bash
curl http://localhost:8000/api/v1/knowledge \
  -H "Authorization: Bearer $TOKEN" | jq
```

Shows all KBs for your organization with statistics.

---

## 12. Delete Knowledge Base (Cascade)

```bash
curl -X DELETE http://localhost:8000/api/v1/knowledge/$KB_ID \
  -H "Authorization: Bearer $TOKEN"
```

**Warning**: This will delete:
- KB record
- All uploads in KB
- All vectors in Qdrant
- All entries in Elasticsearch

**Response**:
```json
{
  "success": true,
  "kb_id": "550e8400...",
  "message": "Knowledge base deleted with cascading uploads and vectors"
}
```

---

## Common Use Cases

### Use Case 1: Multi-KB Organization

```bash
# Create KBs
curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "sales_2026", "display_name": "Sales 2026"}'

curl -X POST http://localhost:8000/api/v1/knowledge \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "ops_2026", "display_name": "Operations 2026"}'

# Upload to each
curl -X POST http://localhost:8000/api/v1/knowledge/sales-kb-id/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sales.pdf"

curl -X POST http://localhost:8000/api/v1/knowledge/ops-kb-id/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@ops.pdf"

# Query only sales
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "...", "knowledge_base_id": "sales-kb-id"}'

# Query only ops
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "...", "knowledge_base_id": "ops-kb-id"}'

# Query all (no filter)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "..."}'
```

### Use Case 2: Version Tracking

```bash
# Upload v1
curl -X POST http://localhost:8000/api/v1/knowledge/$KB_ID/upload \
  -F "file=@policy_v1.pdf" \
  -F "display_name=Policy v1 (Jan 2026)"

# Upload v2
curl -X POST http://localhost:8000/api/v1/knowledge/$KB_ID/upload \
  -F "file=@policy_v2.pdf" \
  -F "display_name=Policy v2 (Jul 2026)"

# Check upload history with dates
curl http://localhost:8000/api/v1/knowledge/$KB_ID/history \
  | jq '.uploads[] | {display_name, upload_date, pages, chunks}'

# Query will return results from both versions
# Sources include upload_date to show which version
```

### Use Case 3: Department-Specific KBs

```bash
# Create department KBs
for dept in sales ops hr finance; do
  curl -X POST http://localhost:8000/api/v1/knowledge \
    -d "{\"name\": \"${dept}_docs\", \"display_name\": \"$dept Documents\"}"
done

# Each department uploads its docs
# Query restricted to department's KB for privacy
```

---

## Troubleshooting

### Upload stuck in "processing"

Check Celery worker:
```bash
celery -A app.tasks.celery_app inspect active
```

### Vectors not found in chat

1. Wait for upload to complete (check status: `completed`)
2. Verify Qdrant is running and reachable
3. Check QueryLog table for error messages

### QueryLog not created

Ensure AsyncSession commit happens in RAGOrchestrator. Check logs for:
```
DB insert error
```

### Reindex fails

1. Verify all uploads have `storage_path` set
2. Check file exists at storage_path
3. Verify Celery worker is running
4. Check Qdrant/Elasticsearch availability

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/enterprise_rag

# Vector Store
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Elasticsearch
ELASTIC_HOST=localhost
ELASTIC_PORT=9200

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Embedding
EMBEDDING_DIMENSION=384
```

---

## Next Steps

1. **Run Tests**: `pytest tests/test_enterprise_rag_e2e.py -v`
2. **Monitor Logs**: `tail -f logs/app.log`
3. **Dashboard Monitoring**: Check `/api/v1/analytics/dashboard` regularly
4. **Set Up Alerts**: Monitor QueryLog and failed uploads
5. **Tune Parameters**: Adjust `top_k`, chunk_size, etc. based on results

---

## Full API Documentation

See:
- `API_CHANGES.md` - Complete endpoint reference
- `ENTERPRISE_RAG_IMPLEMENTATION.md` - Architecture details
- `tests/test_enterprise_rag_e2e.py` - Usage examples

---

## Support

For issues:
1. Check logs: `app/logs/`
2. Verify dependencies running: Postgres, Qdrant, Elasticsearch, Redis, Celery
3. Review `ENTERPRISE_RAG_IMPLEMENTATION.md` deployment checklist
4. Run migration verification: `python scripts/migrate_documents_to_uploads.py`
