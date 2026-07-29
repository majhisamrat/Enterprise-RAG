# Enterprise RAG Redesign Summary

## Executive Summary

Transform from **Document Storage System** → **Embedding Knowledge Platform**

The current system treats uploads as individual documents with vectors stored globally. The redesigned system organizes knowledge into hierarchical **Knowledge Bases**, each containing **multiple uploads**, with full metadata tracking for analytics and retrieval filtering.

---

## What Changes

### Before (Current)
```
Organization
└── Document 1 (vectors for this doc)
└── Document 2 (vectors for this doc)
└── Document 3 (vectors for this doc)

Problem: Can't filter by upload date or retrieve specific uploads
```

### After (Proposed)
```
Organization
├── Knowledge Base: Sales_2026
│   ├── Upload: sales_book.pdf (2026-07-25) → 128 vectors
│   ├── Upload: loss_book.pdf (2026-08-20) → 128 vectors
│   └── Upload: revenue_book.pdf (2026-09-15) → 128 vectors
├── Knowledge Base: Expenses_2026
│   ├── Upload: q1_expenses.pdf → 64 vectors
│   └── Upload: q2_expenses.pdf → 64 vectors
└── Knowledge Base: HR_2026
    └── Upload: handbook_2026.pdf → 256 vectors

Benefits: 
✓ Can compare July vs August ("sales across uploads")
✓ Can archive KB when no longer needed
✓ Can reindex single KB without affecting others
✓ Dashboard shows upload history
✓ Chat can filter by specific KB
```

---

## Key Improvements

### 1. Multi-Upload Retrieval ⭐
**Problem**: All vectors grouped at org level  
**Solution**: Vectors tagged with `upload_id`, `upload_date`, `document_name`

**Use Case**: User asks "Compare July and August sales"
- Retriever finds chunks from July upload + August upload
- Sources clearly show which file each chunk came from

### 2. Knowledge Base Hierarchy ⭐
**Problem**: No way to organize documents  
**Solution**: Create KBs for different domains/projects

**Use Case**: Organization has:
- Sales_2026 (sales documents)
- Expenses_2026 (expense documents)
- HR_Policies (HR handbook)

Can chat within specific KB or across all.

### 3. Upload Metadata Tracking ⭐
**Problem**: No record of upload time, pages, processing time  
**Solution**: New `Upload` table tracks all metadata

**Dashboard Shows**:
```
Sales_2026 KB
├── loss_book.pdf - Uploaded 2026-08-20 - 44 pages - 2.5s processing
├── sales_book.pdf - Uploaded 2026-07-25 - 45 pages - 2.4s processing
└── revenue_book.pdf - Uploaded 2026-09-15 - 38 pages - 2.1s processing

Stats:
- Total Vectors: 310
- Total Pages: 127
- Average Processing Time: 2.3s
- Last Queried: Today 2:30 PM
- Query Count: 156
```

### 4. Filtered Chat Queries ⭐
**Problem**: Chat always retrieves from all vectors  
**Solution**: Optional `knowledge_base_id` parameter in chat API

**Use Cases**:
```
# Chat across all KBs
POST /api/v1/chat
{
  "query": "What are all our expenses?",
  "session_id": "..."
}
→ Searches: Sales_2026 + Expenses_2026 + HR_2026

# Chat in specific KB
POST /api/v1/chat
{
  "query": "What were July sales?",
  "session_id": "...",
  "knowledge_base_id": "kb_uuid_001"  ← NEW
}
→ Searches only Sales_2026 KB
```

### 5. Per-KB Reindexing ⭐
**Problem**: Reindexing affects entire system  
**Solution**: Reindex single KB in isolation

```
POST /api/v1/knowledge/kb_uuid_001/reindex

Only Sales_2026 KB reindexed:
├── Re-fetch July upload file
├── Re-parse, re-chunk, re-embed
├── Delete old vectors for July upload
├── Insert new vectors for July upload
└── Complete (Expenses_2026 unaffected)
```

### 6. Dashboard Analytics ⭐
**Problem**: Dashboard queries complex and slow  
**Solution**: Dedicated tables for metrics + caching

**New Features**:
```
Dashboard can show:
✓ Upload history with dates
✓ Processing time trends
✓ Vector count by upload
✓ Query frequency by KB
✓ User activity timeline
✓ Most accessed documents
```

---

## Database Design

### New Tables (5 Core)

```
1. KNOWLEDGE_BASES
   - Organize uploads into logical groups
   - Track KB metadata (created_at, last_queried_at, query_count)

2. UPLOADS
   - Track each file upload separately
   - Store metadata: pages, chunks, vectors, processing_time
   - Link to knowledge_base_id

3. EMBEDDING_COLLECTIONS
   - Track Qdrant collection per upload
   - Track Elasticsearch index per upload
   - Vector count per upload

4. QUERY_LOGS
   - Track which uploads were used per query
   - Analytics: query count, latency, users
   - Timestamp every query

5. VECTOR_METADATA
   - Denormalized cache for dashboard
   - Fast dashboard queries
```

### Key Relationships

```
Organization (1) ─── (N) KnowledgeBase
                      (1) ─── (N) Upload
                                 (1) ─── (1) EmbeddingCollection
```

---

## API Changes

### Renamed Endpoints (Semantic Clarity)

```
OLD                              NEW
/api/v1/documents/upload    →    /api/v1/knowledge/upload
/api/v1/documents           →    /api/v1/knowledge
/api/v1/documents/{id}      →    /api/v1/knowledge/{id}
/api/v1/documents/{id}/reindex → /api/v1/knowledge/{id}/reindex
```

### New Endpoints (10+)

```
Knowledge Base Management:
POST   /api/v1/knowledge                 Create new KB
GET    /api/v1/knowledge                 List user's KBs
GET    /api/v1/knowledge/{kb_id}         Get KB details
DELETE /api/v1/knowledge/{kb_id}         Delete KB (cascade)

Upload Management:
POST   /api/v1/knowledge/{kb_id}/upload           Add file to KB
GET    /api/v1/knowledge/{kb_id}/history          List uploads
POST   /api/v1/knowledge/{kb_id}/reindex          Reindex KB
GET    /api/v1/knowledge/{kb_id}/statistics       KB stats

Chat Filtering:
POST   /api/v1/chat                      (add knowledge_base_id param)

Analytics:
GET    /api/v1/dashboard                 Dashboard summary
GET    /api/v1/analytics/queries         Query analytics
GET    /api/v1/analytics/usage           Usage analytics
```

### Enhanced Existing Endpoints

```
POST /api/v1/chat
{
  "query": "...",
  "session_id": "...",
  "knowledge_base_id": "kb_uuid_001"  ← NEW OPTIONAL PARAM
}

Filters retrieval to single KB (or null = all KBs)
```

---

## Vector Metadata Structure

Every vector in Qdrant now includes:

```json
{
  "chunk_id": "abc123",
  "upload_id": "upload_uuid_001",        ← NEW
  "knowledge_base_id": "kb_uuid_001",    ← NEW
  "organization_id": "org_uuid_001",
  "user_id": "user_uuid_001",
  "document_name": "sales_book.pdf",
  "upload_date": "2026-07-25",           ← NEW
  "page_number": 5,
  "chunk_number": 12,
  "chunk_text": "...",
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "created_at": "2026-07-25T10:35:00Z"
}
```

Enables filtering by:
- `upload_id` → Single upload
- `knowledge_base_id` → Single KB
- `upload_date` → Date range
- `document_name` → Filename

---

## Use Case Examples

### Example 1: Multi-Upload Comparison

```
User uploads:
  - July sales report (2026-07-25)
  - August sales report (2026-08-20)

To Sales_2026 KB

User asks: "Compare July and August sales"

System retrieves:
  ✓ Chunks from July report (upload_uuid_001)
  ✓ Chunks from August report (upload_uuid_002)
  ✓ LLM compares using both sources
  ✓ Response shows which file each stat came from
```

### Example 2: KB Isolation

```
User creates KB: "Q1_Financial_Review"
  └─ uploads 10 PDFs

Then creates KB: "Q2_Financial_Review"
  └─ uploads 8 PDFs

When user asks: "Show me Q1 trends"
  POST /api/v1/chat
  {
    "query": "Show me Q1 trends",
    "knowledge_base_id": "q1_kb_uuid"
  }

System only searches Q1 PDFs ✓
Q2 PDFs not searched ✓
```

### Example 3: Dashboard Analytics

```
Dashboard shows:
  
  Q1_Financial_Review
  ├─ 10 uploads
  ├─ 450 pages
  ├─ 1200 chunks
  ├─ 1200 vectors
  ├─ Last queried: 2 hours ago
  ├─ Total queries: 89
  └─ Latest uploads:
     ├─ April_Summary.pdf (2 days ago)
     ├─ March_Expenses.pdf (5 days ago)
     └─ Q1_Overview.pdf (1 week ago)
```

---

## Migration Path

### Phase 1: Database (Day 1)
- Create new tables (KnowledgeBase, Upload, etc.)
- Run alembic migration
- Backfill existing Document data → Upload table
- Test with sample data

### Phase 2: APIs (Day 2)
- Implement new `/knowledge/*` endpoints
- Keep old `/documents/*` endpoints (deprecated but working)
- Route both to new code

### Phase 3: Vector Metadata (Day 3)
- Re-embed existing documents with new metadata
- Add upload_id, kb_id to Qdrant vectors
- Update retrieval filters

### Phase 4: Chat Filtering (Day 3)
- Add knowledge_base_id to chat endpoint
- Test with/without filtering

### Phase 5: Dashboard (Day 3)
- Implement analytics endpoints
- Create dashboard queries

**Total: 3-4 days, zero downtime**

---

## Backward Compatibility

### Old Routes Still Work
```
POST /api/v1/documents/upload
  ↓
Routes to new /api/v1/knowledge/upload
  ↓
Creates default KB if needed
  ↓
Handles upload as before
```

### Deprecation Timeline
```
Week 1-2: Both old + new routes work (dual support)
Week 3-4: Old routes return deprecation warning
Week 5+: Old routes removed (give users time to migrate)
```

---

## What Stays the Same

✅ **Authentication** - No changes  
✅ **Chat endpoint** - Same interface (optional new param)  
✅ **Search endpoint** - Same interface (enhanced)  
✅ **LLM generation** - No changes  
✅ **Embedding model** - No changes  
✅ **Frontend** - FROZEN (no changes)  
✅ **Retrieval pipeline** - Enhanced but compatible  

---

## Risk Mitigation

### Risk 1: Data Loss During Migration
**Mitigation**: Backup before migration, dry-run on copy database

### Risk 2: Slow Reindexing
**Mitigation**: Run as background Celery job, don't block user

### Risk 3: Vector count explosion
**Mitigation**: Per-KB collections in Qdrant (already supported)

### Risk 4: Dashboard query performance
**Mitigation**: Indexes on all FK + created_at columns

### Risk 5: Breaking chat API
**Mitigation**: New param is optional, defaults to current behavior

---

## Success Metrics

After implementation, we should see:

✓ Users can upload multiple documents to same KB  
✓ Dashboard shows upload history  
✓ Chat can filter by KB  
✓ Reindexing doesn't affect other KBs  
✓ Query response time < 500ms  
✓ Dashboard queries complete < 1s  

---

## Next Steps

1. **Review** this summary
2. **Answer** 6 approval questions in `APPROVAL_CHECKLIST.md`
3. **Confirm** go-ahead
4. **Implementation** begins immediately

---

**Questions?** Review:
- `ARCHITECTURE_ANALYSIS.md` - Detailed analysis
- `ERD_DIAGRAM.md` - Database schema
- `API_FLOWS.md` - Step-by-step flows
- `APPROVAL_CHECKLIST.md` - Questions to answer

**Ready to proceed?** Let me know answers to the 6 questions! 🚀
