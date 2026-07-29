# Entity Relationship Diagram (ERD)

## Complete Schema Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ORGANIZATION (1)                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │ id (UUID, PK)                                                        │  │
│  │ name (String)                                                        │  │
│  │ domain (String, unique)                                             │  │
│  │ subscription_plan (enterprise, pro, starter)                        │  │
│  │ created_at, updated_at                                              │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┬─────────────────┘
                     │ (1:N)                                  │ (1:N)
                     │                                        │
        ┌────────────▼──────────────┐         ┌──────────────▼────────────────┐
        │         USERS (N)         │         │   KNOWLEDGE_BASES (N)        │
        │ ┌──────────────────────┐  │         │ ┌──────────────────────────┐ │
        │ │ id (UUID, PK)        │  │         │ │ id (UUID, PK)            │ │
        │ │ org_id (FK)          │  │         │ │ org_id (FK)              │ │
        │ │ name                 │  │         │ │ user_id (FK)             │ │
        │ │ email (unique)       │  │         │ │ name ("Sales_2026")      │ │
        │ │ password_hash        │  │         │ │ display_name             │ │
        │ │ department           │  │         │ │ description              │ │
        │ │ last_login           │  │         │ │ status (active/archived) │ │
        │ │ created_at           │  │         │ │ query_count              │ │
        │ └──────────────────────┘  │         │ │ last_queried_at          │ │
        └────────────┬───────────────┘         │ │ created_at, updated_at   │ │
                     │ (1:N)                   │ └──────────────────────────┘ │
                     │                         │             │ (1:N)
                     │                         │             │
                     │                         │    ┌────────▼──────────────────┐
                     │                         │    │      UPLOADS (N)         │
                     │                         │    │ ┌────────────────────┐    │
                     │                         │    │ │ id (UUID, PK)      │    │
                     │                         │    │ │ kb_id (FK)         │    │
                     │                         │    │ │ org_id (FK)        │    │
                     │                         │    │ │ user_id (FK)       │    │
                     │                         │    │ │ filename           │    │
                     │                         │    │ │ file_type (pdf)    │    │
                     │                         │    │ │ file_size_bytes    │    │
                     │                         │    │ │ storage_path       │    │
                     │                         │    │ │ page_count         │    │
                     │                         │    │ │ chunk_count        │    │
                     │                         │    │ │ total_vectors      │    │
                     │                         │    │ │ embedding_model    │    │
                     │                         │    │ │ embedding_dim      │    │
                     │                         │    │ │ processing_status  │    │
                     │                         │    │ │ processing_time_ms │    │
                     │                         │    │ │ error_message      │    │
                     │                         │    │ │ created_at         │    │
                     │                         │    │ └────────────────────┘    │
                     │                         │    │          │ (1:1)
                     │                         │    │          │
                     │                         │    │    ┌─────▼──────────────┐
                     │                         │    │    │EMBEDDING_COLL (1)│
                     │                         │    │    │ ┌────────────────┤
                     │                         │    │    │ │ id (UUID)      │
                     │                         │    │    │ │ kb_id (FK)     │
                     │                         │    │    │ │ upload_id (FK) │
                     │                         │    │    │ │ collection_name│
                     │                         │    │    │ │ vector_count   │
                     │                         │    │    │ │ created_at     │
                     │                         │    │    │ └────────────────┘
                     │                         │    └────────────────────────────┘
                     │                         └───────────────────────────────────┘
                     │
        ┌────────────▼──────────────────────┐
        │    CHAT_SESSIONS (N)              │
        │ ┌───────────────────────────────┐ │
        │ │ id (UUID, PK)                 │ │
        │ │ user_id (FK)                  │ │
        │ │ org_id (FK)                   │ │
        │ │ kb_id (FK, nullable)          │ │
        │ │ title                         │ │
        │ │ created_at, updated_at        │ │
        │ └───────────────────────────────┘ │
        │           │ (1:N)
        │           │
        │    ┌──────▼─────────────────┐
        │    │  CHAT_MESSAGES (N)     │
        │    │ ┌────────────────────┐ │
        │    │ │ id (UUID, PK)      │ │
        │    │ │ session_id (FK)    │ │
        │    │ │ role (user/asst)   │ │
        │    │ │ content            │ │
        │    │ │ tokens_used        │ │
        │    │ │ created_at         │ │
        │    │ └────────────────────┘ │
        │    └────────────────────────┘
        └───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  Additional Supporting Tables                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  QUERY_LOGS (for analytics)                    VECTOR_METADATA (cached)    │
│  ┌────────────────────────────┐               ┌────────────────────────┐  │
│  │ id (UUID, PK)              │               │ id (UUID, PK)          │  │
│  │ user_id (FK)               │               │ kb_id (FK)             │  │
│  │ org_id (FK)                │               │ upload_id (FK)         │  │
│  │ kb_id (FK, nullable)       │               │ page_count (cached)    │  │
│  │ query_text                 │               │ chunk_count (cached)   │  │
│  │ retrieved_count            │               │ total_vectors (cached) │  │
│  │ latency_ms                 │               │ embedding_model        │  │
│  │ used_upload_ids (array)    │               │ query_count            │  │
│  │ created_at                 │               │ last_queried_at        │  │
│  └────────────────────────────┘               │ created_at             │  │
│                                               └────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Relationship Summary

```
Organization (1) ──────────┬──> (N) Users
                           ├──> (N) KnowledgeBases
                           └──> (N) QueryLogs

User (1) ──────────┬──> (N) KnowledgeBases (owner)
                   └──> (N) ChatSessions

KnowledgeBase (1) ──┬──> (N) Uploads
                    ├──> (N) ChatSessions
                    └──> (N) QueryLogs

Upload (1) ──┬──> (1) EmbeddingCollection
             ├──> (N) QueryLogs (via used_upload_ids)
             └──> (1) VectorMetadata

ChatSession (1) ──> (N) ChatMessages
```

## Key Cardinality Notes

- **Organization : User** = 1:N (one org can have many users)
- **Organization : KnowledgeBase** = 1:N (but see User → KB for ownership)
- **KnowledgeBase : Upload** = 1:N (one KB receives multiple document uploads)
- **Upload : EmbeddingCollection** = 1:1 (each upload creates one collection in Qdrant)
- **User : ChatSession** = 1:N (user can have multiple chat sessions)
- **KnowledgeBase : ChatSession** = 1:N (optional - filter chats by KB)
- **ChatSession : ChatMessage** = 1:N (session contains many messages)

## Foreign Key Constraints

All FK constraints use:
```
FOREIGN KEY (column) REFERENCES parent_table(id) 
  ON DELETE CASCADE 
  ON UPDATE CASCADE
```

This ensures:
- Deleting an upload cascades to delete vectors, metadata, query logs
- Deleting a KB cascades to delete all uploads + vectors + chats
- Deleting a user cascades to delete sessions and messages
- Deleting organization cascades to delete everything (hard delete)

## Indexes for Performance

```sql
-- Org/User queries
CREATE INDEX idx_users_org_id ON users(organization_id);
CREATE INDEX idx_users_email ON users(email);

-- KB queries
CREATE INDEX idx_kbs_org_id ON knowledge_bases(organization_id);
CREATE INDEX idx_kbs_user_id ON knowledge_bases(user_id);
CREATE INDEX idx_kbs_status ON knowledge_bases(status);

-- Upload queries
CREATE INDEX idx_uploads_kb_id ON uploads(knowledge_base_id);
CREATE INDEX idx_uploads_status ON uploads(processing_status);
CREATE INDEX idx_uploads_created_at ON uploads(created_at);

-- Chat queries
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_kb_id ON chat_sessions(knowledge_base_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);

-- Query logs
CREATE INDEX idx_query_logs_user_id ON query_logs(user_id);
CREATE INDEX idx_query_logs_kb_id ON query_logs(knowledge_base_id);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at);

-- Vector metadata
CREATE INDEX idx_vector_meta_kb_id ON vector_metadata(knowledge_base_id);
CREATE INDEX idx_vector_meta_upload_id ON vector_metadata(upload_id);
```

---

End of ERD Documentation
