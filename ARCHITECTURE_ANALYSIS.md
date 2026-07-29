# Enterprise RAG Backend: Architecture Analysis & Redesign

## 1. CURRENT ARCHITECTURE REVIEW

### 1.1 Existing API Routes

| Route | Method | Purpose | Status |
|-------|--------|---------|--------|
| `/api/v1/health` | GET | Service health check | ✅ Keep |
| `/api/v1/ready` | GET | Readiness probe | ✅ Keep |
| `/api/v1/auth/send-otp` | POST | Send OTP to email | ✅ Keep |
| `/api/v1/auth/verify-otp` | POST | Verify OTP, login | ✅ Keep |
| `/api/v1/auth/google` | POST | Google OAuth2 auth | ✅ Keep |
| `/api/v1/auth/register` | POST | Register new user | ✅ Keep |
| `/api/v1/auth/login` | POST | Email/password login | ✅ Keep |
| `/api/v1/auth/me` | GET | Get current user | ✅ Keep |
| `/api/v1/documents/upload` | POST | Upload document | 🔄 **RENAME → `/knowledge/upload`** |
| `/api/v1/documents` | GET | List documents | 🔄 **RENAME → `/knowledge`** |
| `/api/v1/documents/{id}` | GET | Get document details | 🔄 **RENAME → `/knowledge/{id}`** |
| `/api/v1/documents/{id}` | DELETE | Delete document | 🔄 **RENAME → `/knowledge/{id}`** |
| `/api/v1/documents/{id}/reindex` | POST | Reindex document | 🔄 **RENAME → `/knowledge/{id}/reindex`** |
| `/api/v1/chat` | POST | Chat query | ✅ Keep |
| `/api/v1/search` | POST | Hybrid search | ✅ Keep |

### 1.2 New Routes to Add

```
POST   /api/v1/knowledge/upload              Create knowledge base + upload document
GET    /api/v1/knowledge                     List user's knowledge bases
GET    /api/v1/knowledge/{kb_id}             Get knowledge base details
DELETE /api/v1/knowledge/{kb_id}             Delete entire knowledge base
POST   /api/v1/knowledge/{kb_id}/upload      Add document to existing knowledge base
POST   /api/v1/knowledge/{kb_id}/reindex     Reindex single knowledge base
GET    /api/v1/knowledge/{kb_id}/history     Get upload history for KB
GET    /api/v1/knowledge/{kb_id}/statistics  Get KB statistics (pages, chunks, vectors)
GET    /api/v1/chat/sessions                 List chat sessions
GET    /api/v1/chat/{session_id}             Get session messages
GET    /api/v1/dashboard                     Get dashboard summary data
GET    /api/v1/analytics/queries             Query analytics
GET    /api/v1/analytics/usage               Usage analytics
```

---

## 2. PROBLEMS IN CURRENT DESIGN

### 2.1 Missing Multi-Upload Tracking
- **Problem**: No way to track which upload a vector came from
- **Impact**: Cannot retrieve by upload date or filter across multiple uploads
- **Current**: Vectors have `document_id` but no upload session tracking
- **Need**: Separate upload metadata table

### 2.2 Original PDF Not Persistent
- **Problem**: PDF deleted after ingestion, only vectors remain
- **Impact**: Cannot re-parse, inspect original, or extract additional data
- **Current**: `storage_path` exists but documents deleted
- **Need**: Optional permanent storage with versioning

### 2.3 No Knowledge Base Concept
- **Problem**: All documents grouped at organization level only
- **Impact**: No logical separation of knowledge domains
- **Current**: Single organization → N documents (flat)
- **Need**: Organization → Knowledge Base → Uploads → Vectors (hierarchical)

### 2.4 Document Model Confusion
- **Problem**: `Document` table mixes file metadata with upload metadata
- **Impact**: Schema is too generic, doesn't capture upload-specific data
- **Current**: One table, multiple purposes
- **Need**: Split into `Document` (metadata) + `Upload` (file history)

### 2.5 Missing Dashboard Metrics
- **Problem**: No tables for computing dashboard statistics
- **Impact**: Dashboard queries will be slow/complex
- **Current**: Must join 5+ tables to compute KB statistics
- **Need**: Denormalized metrics table or materialized view

### 2.6 Chat Filtering Not Supported
- **Problem**: Chat queries retrieve from ALL vectors across ALL uploads
- **Impact**: Cannot ask "Compare July sales with August sales"
- **Current**: No way to filter by upload_id or upload_date
- **Need**: Metadata filters in Qdrant + query parameters

### 2.7 Reindexing All Documents
- **Problem**: Reindex endpoint reindexes entire system
- **Impact**: Slow, expensive, affects other knowledge bases
- **Current**: No granular reindex support
- **Need**: Reindex by knowledge base only

---

## 3. DATABASE REDESIGN

### 3.1 Current Schema Problems
- `Document` stores both file metadata AND upload metadata mixed
- No separate `UploadHistory` table
- No `KnowledgeBase` concept
- No upload session tracking in vectors

### 3.2 Proposed New Schema

```
ORGANIZATIONS
  ├── id (UUID, PK)
  ├── name
  ├── domain
  └── subscription_plan

USERS
  ├── id (UUID, PK)
  ├── organization_id (FK)
  ├── name, email, password_hash
  ├── department, designation
  └── last_login

KNOWLEDGE_BASES
  ├── id (UUID, PK)
  ├── organization_id (FK)
  ├── user_id (FK, who created)
  ├── name (e.g., "Sales_2026")
  ├── display_name (e.g., "Sales Q1-Q4 2026")
  ├── description
  ├── status (active, archived, deleted)
  ├── created_at
  ├── updated_at
  ├── last_queried_at
  └── query_count

UPLOADS
  ├── id (UUID, PK)
  ├── knowledge_base_id (FK)
  ├── organization_id (FK)
  ├── user_id (FK, who uploaded)
  ├── original_filename (e.g., "sales_book.pdf")
  ├── display_name (user-specified)
  ├── file_type (pdf, docx, txt)
  ├── file_size_bytes
  ├── storage_path (nullable - may be deleted)
  ├── page_count
  ├── chunk_count
  ├── embedding_model (e.g., "BAAI/bge-small-en-v1.5")
  ├── embedding_dimension (384)
  ├── total_vectors
  ├── processing_status (pending, processing, completed, failed)
  ├── processing_start_at
  ├── processing_end_at
  ├── processing_duration_ms
  ├── error_message (if failed)
  ├── vector_collection_name (e.g., "kb_uuid_0")
  ├── qdrant_index_name
  ├── elasticsearch_index_name
  ├── created_at
  ├── updated_at
  └── tags (array)

EMBEDDING_COLLECTIONS
  ├── id (UUID, PK)
  ├── knowledge_base_id (FK)
  ├── upload_id (FK)
  ├── collection_name (Qdrant collection name)
  ├── index_name (Elasticsearch index)
  ├── vector_count
  ├── created_at

CHAT_SESSIONS
  ├── id (UUID, PK)
  ├── user_id (FK)
  ├── organization_id (FK)
  ├── knowledge_base_id (FK, nullable - can chat across all KBs)
  ├── title
  ├── created_at
  └── updated_at

CHAT_MESSAGES
  ├── id (UUID, PK)
  ├── session_id (FK)
  ├── role (user, assistant, system)
  ├── content
  ├── tokens_used
  ├── created_at

QUERY_LOGS
  ├── id (UUID, PK)
  ├── user_id (FK)
  ├── organization_id (FK)
  ├── knowledge_base_id (FK, nullable)
  ├── query_text
  ├── retrieved_count
  ├── latency_ms
  ├── used_upload_ids (array of upload_ids used)
  ├── created_at

VECTOR_METADATA (denormalized for fast dashboard queries)
  ├── id (UUID, PK)
  ├── knowledge_base_id (FK)
  ├── upload_id (FK)
  ├── organization_id (FK)
  ├── page_count (cached from upload)
  ├── chunk_count (cached from upload)
  ├── total_vectors (cached from upload)
  ├── embedding_model
  ├── last_queried_at
  ├── query_count
  └── created_at
```

---

## 4. ENTITY RELATIONSHIP DIAGRAM (ERD)

```
Organization (1) ──┬──> (N) Users
                   ├──> (N) KnowledgeBases
                   └──> (N) QueryLogs

KnowledgeBase (1) ──┬──> (N) Uploads
                    └──> (N) ChatSessions

Upload (1) ──┬──> (1) EmbeddingCollection
             ├──> (N) QueryLogs
             └──> (N) VectorMetadata

ChatSession (1) ──> (N) ChatMessages

User (1) ──┬──> (N) KnowledgeBases
           ├──> (N) ChatSessions
           └──> (N) QueryLogs
```

---

## 5. API FLOW DIAGRAMS

### 5.1 Upload Flow

```
User Click "Upload" 
  ↓
POST /api/v1/knowledge/upload (with KB ID)
  ├─ Validate file (size, type)
  ├─ Save file to disk/S3
  ├─ Create Upload record → PENDING
  ├─ Trigger IngestionService (async via Celery)
  │  ├─ Parse PDF
  │  ├─ Chunk (recursive)
  │  ├─ Embed (BAAI/bge-small-en-v1.5)
  │  ├─ Create Qdrant collection (unique per upload)
  │  ├─ Upsert vectors with upload_id metadata
  │  ├─ Index in Elasticsearch
  │  └─ Update Upload record → COMPLETED
  ├─ Increment KnowledgeBase.query_count
  └─ Return Upload metadata to client
```

### 5.2 Chat Flow with KB Filtering

```
User sends message
  ↓
POST /api/v1/chat
  ├─ Parse knowledge_base_id (optional filter)
  ├─ Call HybridRetriever
  │  ├─ Build Qdrant filter:
  │  │  └─ knowledge_base_id == requested_kb_id
  │  ├─ Build Elasticsearch filter (same)
  │  ├─ Dense search (filtered)
  │  ├─ Sparse search (filtered)
  │  ├─ RRF fusion
  │  └─ Cross-encoder rerank
  ├─ Call LLM with context
  ├─ Create QueryLog with used_upload_ids
  ├─ Save ChatMessage
  ├─ Return answer + sources with upload_id
  └─ Update KnowledgeBase.last_queried_at
```

### 5.3 Retrieval Flow with Multi-Upload Support

```
Query: "Compare July and August sales"
  ↓
HybridRetriever.retrieve()
  ├─ Filter by knowledge_base_id (if specified)
  ├─ Qdrant vector search (dense)
  │  └─ Filter: knowledge_base_id + upload_id 
  ├─ Elasticsearch BM25 search (sparse)
  │  └─ Filter: knowledge_base_id + upload_id
  ├─ RRF fusion with upload_id preservation
  ├─ Cross-encoder rerank
  └─ Return results with upload_id per chunk
```

---

## 6. DASHBOARD-READY DATA STRUCTURE

### 6.1 Dashboard Requirements Met

Dashboard needs to display:

```
Knowledge Bases View:
├─ KB Name
├─ Created Date
├─ Last Queried
├─ Total Uploads
├─ Total Pages (sum across uploads)
├─ Total Chunks (sum across uploads)
├─ Total Vectors (sum across uploads)
├─ Query Count
└─ Uploads List:
    ├─ Filename
    ├─ Upload Date
    ├─ Pages
    ├─ Chunks
    ├─ Vectors
    ├─ Embedding Model
    ├─ Processing Time
    ├─ Status
    └─ Action (view, delete, reindex)
```

### 6.2 SQL for Dashboard Query

```sql
SELECT 
  kb.id,
  kb.name,
  kb.display_name,
  kb.created_at,
  kb.last_queried_at,
  kb.query_count,
  COUNT(DISTINCT u.id) AS total_uploads,
  COALESCE(SUM(u.page_count), 0) AS total_pages,
  COALESCE(SUM(u.chunk_count), 0) AS total_chunks,
  COALESCE(SUM(u.total_vectors), 0) AS total_vectors,
  json_agg(json_build_object(
    'id', u.id,
    'filename', u.original_filename,
    'upload_date', u.created_at,
    'pages', u.page_count,
    'chunks', u.chunk_count,
    'vectors', u.total_vectors,
    'status', u.processing_status,
    'duration_ms', u.processing_duration_ms
  )) AS uploads
FROM knowledge_bases kb
LEFT JOIN uploads u ON kb.id = u.knowledge_base_id
WHERE kb.organization_id = $1
GROUP BY kb.id
ORDER BY kb.last_queried_at DESC;
```

---

## 7. VECTOR METADATA IN QDRANT

Every vector stored in Qdrant must include:

```json
{
  "chunk_id": "uuid",
  "upload_id": "uuid",
  "knowledge_base_id": "uuid",
  "organization_id": "uuid",
  "user_id": "uuid",
  "document_name": "sales_book.pdf",
  "upload_date": "2026-07-25T10:30:00Z",
  "page_number": 5,
  "chunk_number": 12,
  "chunk_text": "...",
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "created_at": "2026-07-25T10:35:00Z",
  "metadata": {
    "source": "upload_uuid",
    "processing_batch": "batch_001"
  }
}
```

This allows filtering by:
- `upload_id` → retrieve from specific upload
- `knowledge_base_id` → retrieve from specific KB
- `upload_date` → retrieve by date range
- `document_name` → retrieve by filename

---

## 8. API REDESIGN SUMMARY

### 8.1 Routes to Keep (No Changes)
✅ Authentication routes (`/auth/*`)  
✅ Health/Ready probes  
✅ Chat endpoint  
✅ Search endpoint (with new filtering)

### 8.2 Routes to Rename
| Old | New | Reason |
|-----|-----|--------|
| `/documents/upload` | `/knowledge/upload` | Semantic clarity |
| `/documents` | `/knowledge` | Semantic clarity |
| `/documents/{id}` | `/knowledge/{id}` | Semantic clarity |
| `/documents/{id}/reindex` | `/knowledge/{id}/reindex` | Semantic clarity |

### 8.3 Routes to Deprecate
❌ `/documents/{id}/versions` → Not needed (use Upload history)

---

## 9. DELETE CASCADE BEHAVIOR

When deleting a KnowledgeBase:

```
DELETE from knowledge_bases WHERE id = $1
  ├─ Cascade: DELETE from uploads
  │  ├─ Cascade: DELETE from embedding_collections
  │  ├─ Cascade: DELETE vectors in Qdrant (via collection)
  │  ├─ Cascade: DELETE vectors in Elasticsearch (via index)
  │  └─ Cascade: UPDATE query_logs SET kb_id = NULL
  ├─ Cascade: DELETE from chat_sessions
  │  └─ Cascade: DELETE from chat_messages
  ├─ Cascade: DELETE from query_logs
  └─ Cascade: DELETE from vector_metadata
```

Other KBs/Uploads unaffected → ✅

---

## 10. REINDEX BEHAVIOR

### Current Problem
Reindexing one document rebuilds embeddings for **entire system**

### Proposed Solution
```
POST /api/v1/knowledge/{kb_id}/reindex
  ├─ Retrieve all uploads for KB
  ├─ For each upload:
  │  ├─ Fetch original file (if stored)
  │  ├─ Re-parse, re-chunk, re-embed
  │  ├─ Delete old vectors (Qdrant collection)
  │  ├─ Upsert new vectors
  │  └─ Update Upload record
  └─ Return reindex summary
```

Only affected KB reindexed → ✅

---

## 11. IMPLEMENTATION ROADMAP

### Phase 1: Database Migration (1 day)
- [ ] Create new tables (KnowledgeBase, Upload, EmbeddingCollection)
- [ ] Create migration script (alembic)
- [ ] Backfill existing Document data → Upload table

### Phase 2: API Redesign (1 day)
- [ ] Rename routes `/documents` → `/knowledge`
- [ ] Create KB management endpoints
- [ ] Add upload history endpoint

### Phase 3: Vector Metadata Enhancement (0.5 day)
- [ ] Update Qdrant payload to include upload_id, KB ID
- [ ] Add filtering logic to HybridRetriever

### Phase 4: Chat Filtering (0.5 day)
- [ ] Add knowledge_base_id parameter to `/chat`
- [ ] Pass filters to retriever

### Phase 5: Dashboard Queries (0.5 day)
- [ ] Create analytics endpoints
- [ ] Implement statistics queries

---

## 12. SUMMARY OF CHANGES

| Aspect | Current | Proposed | Impact |
|--------|---------|----------|--------|
| Document Storage | PDF persisted | Optional | Reduces storage |
| KB Organization | Flat | Hierarchical | Better UX |
| Multi-Upload Support | No | Yes | Core feature |
| Chat Filtering | No | Yes | Core feature |
| Reindex Scope | Global | Per-KB | Performance |
| Dashboard Ready | No | Yes | Future-proof |
| Metadata Tracking | Limited | Rich | Analytics-ready |

---

## APPROVAL CHECKPOINT

✋ **STOP HERE** - Awaiting your approval before implementation begins.

**Questions for you:**

1. **Approve this database schema?** (13 tables)
2. **Keep optional file storage or always delete PDFs after ingestion?**
3. **Should Knowledge Bases be organization-level or user-level?**
4. **Reindex: rebuild all vectors or just update embeddings model?**
5. **Priority: Which feature first? KB management, filtering, or dashboard?**
