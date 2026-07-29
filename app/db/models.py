import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, TimestampMixin, UUIDMixin

# Many-to-Many join table for Roles and Permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", GUID(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", GUID(), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), default="enterprise", nullable=False)
    storage_limit: Mapped[int] = mapped_column(Integer, default=107374182400, nullable=False)  # 100 GB in bytes

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="organization", cascade="all, delete-orphan")
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="organization", cascade="all, delete-orphan")
    knowledge_bases: Mapped[List["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="organization", cascade="all, delete-orphan")
    query_logs: Mapped[List["QueryLog"]] = relationship("QueryLog", back_populates="organization", cascade="all, delete-orphan")


class Role(Base, UUIDMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[List["Permission"]] = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base, UUIDMixin):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    roles: Mapped[List[Role]] = relationship("Role", secondary=role_permissions, back_populates="permissions")


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False)  # local, google, oidc
    google_sub: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, inactive, suspended
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    role: Mapped[Optional[Role]] = relationship("Role", back_populates="users")
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="owner")


class UserSession(Base, UUIDMixin):
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="sessions")


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    parser_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="uploaded", nullable=False, index=True)  # uploaded, processing, indexed, failed

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="documents")
    owner: Mapped[User] = relationship("User", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    permissions: Mapped[List["DocumentPermission"]] = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")
    doc_metadata: Mapped[List["DocumentMetadata"]] = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base, UUIDMixin):
    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="versions")


class DocumentPermission(Base, UUIDMixin):
    __tablename__ = "document_permissions"

    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    can_read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="permissions")


class DocumentMetadata(Base, UUIDMixin):
    __tablename__ = "document_metadata"

    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="doc_metadata")


class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="New Conversation", nullable=False)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="chat_sessions")
    user: Mapped[User] = relationship("User")
    knowledge_base: Mapped[Optional["KnowledgeBase"]] = relationship("KnowledgeBase", back_populates="chat_sessions")
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base, UUIDMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    session: Mapped[ChatSession] = relationship("ChatSession", back_populates="messages")
    retrieved_sources: Mapped[List["RetrievedSource"]] = relationship("RetrievedSource", back_populates="message", cascade="all, delete-orphan")
    feedback: Mapped[Optional["Feedback"]] = relationship("Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan")


class SearchHistory(Base, UUIDMixin):
    __tablename__ = "search_history"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class RetrievedSource(Base, UUIDMixin):
    __tablename__ = "retrieved_sources"

    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=True, index=True)
    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[str] = mapped_column(String(100), nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text_snippet: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    message: Mapped[Optional[ChatMessage]] = relationship("ChatMessage", back_populates="retrieved_sources")


class Feedback(Base, UUIDMixin):
    __tablename__ = "feedback"

    message_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g., +1 or -1
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    message: Mapped[ChatMessage] = relationship("ChatMessage", back_populates="feedback")


class APIUsage(Base, UUIDMixin):
    __tablename__ = "api_usage"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(100), nullable=False)
    tokens_prompt: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_completion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_estimate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)


class BackgroundJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "background_jobs"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class KnowledgeBase(Base, UUIDMixin, TimestampMixin):
    """Knowledge Base for organizing uploads logically."""
    __tablename__ = "knowledge_bases"

    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Sales_2026"
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Sales Q1-Q4 2026"
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False, index=True)  # active, archived, deleted
    query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_queried_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="knowledge_bases")
    user: Mapped[User] = relationship("User")
    uploads: Mapped[List["Upload"]] = relationship("Upload", back_populates="knowledge_base", cascade="all, delete-orphan")
    chat_sessions: Mapped[List["ChatSession"]] = relationship("ChatSession", back_populates="knowledge_base")
    query_logs: Mapped[List["QueryLog"]] = relationship("QueryLog", back_populates="knowledge_base", cascade="all, delete-orphan")


class Upload(Base, UUIDMixin, TimestampMixin):
    """Track individual document uploads with metadata."""
    __tablename__ = "uploads"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, txt
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # nullable - may be deleted after ingestion
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(255), default="BAAI/bge-small-en-v1.5", nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, default=384, nullable=False)
    total_vectors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    processing_start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vector_collection_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Qdrant collection name
    qdrant_index_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    elasticsearch_index_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Relationships
    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase", back_populates="uploads")
    organization: Mapped[Organization] = relationship("Organization")
    user: Mapped[User] = relationship("User")
    embedding_collection: Mapped[Optional["EmbeddingCollection"]] = relationship("EmbeddingCollection", back_populates="upload", uselist=False, cascade="all, delete-orphan")
    query_logs: Mapped[List["QueryLog"]] = relationship("QueryLog", back_populates="upload")


class EmbeddingCollection(Base, UUIDMixin):
    """Track Qdrant/Elasticsearch collection per upload."""
    __tablename__ = "embedding_collections"

    upload_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    collection_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Qdrant collection name
    index_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Elasticsearch index
    vector_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    upload: Mapped[Upload] = relationship("Upload", back_populates="embedding_collection")
    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase")


class QueryLog(Base, UUIDMixin):
    """Track all queries for analytics."""
    __tablename__ = "query_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_base_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=True, index=True)
    upload_id: Mapped[Optional[uuid.UUID]] = mapped_column(GUID(), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=True, index=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    used_upload_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # Array of upload IDs used
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relationships
    user: Mapped[User] = relationship("User")
    organization: Mapped[Organization] = relationship("Organization", back_populates="query_logs")
    knowledge_base: Mapped[Optional[KnowledgeBase]] = relationship("KnowledgeBase", back_populates="query_logs")
    upload: Mapped[Optional[Upload]] = relationship("Upload", back_populates="query_logs")


class VectorMetadata(Base, UUIDMixin):
    """Denormalized metadata cache for fast dashboard queries."""
    __tablename__ = "vector_metadata"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    upload_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("uploads.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_vectors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False)
    query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_queried_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    knowledge_base: Mapped[KnowledgeBase] = relationship("KnowledgeBase")
    upload: Mapped[Upload] = relationship("Upload")
    organization: Mapped[Organization] = relationship("Organization")
