"""
Dashboard and Analytics API endpoints.

Provides statistics, metrics, and analytics for knowledge bases, uploads, and queries.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import (
    KnowledgeBase, Upload, QueryLog, ChatMessage, ChatSession, User
)
from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.db.repositories.upload_repository import UploadRepository
from app.db.session import get_db
from app.utils.logger import app_logger

router = APIRouter(prefix="/analytics", tags=["Analytics & Dashboard"])


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard Summary Endpoint
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive dashboard summary with KBs, uploads, and statistics.
    
    Returns aggregated metrics across all knowledge bases.
    """
    try:
        kb_repo = KnowledgeBaseRepository(db)
        
        # Get all KBs for org
        kbs = await kb_repo.get_by_organization(
            organization_id=tenant_context.organization_id,
            skip=0,
            limit=1000
        )

        kb_summaries = []
        total_uploads = 0
        total_pages = 0
        total_chunks = 0
        total_vectors = 0
        total_queries = 0

        for kb in kbs:
            # Get KB statistics
            stats = await kb_repo.get_statistics(kb.id)
            
            # Get latest uploads
            upload_repo = UploadRepository(db)
            latest_uploads = await upload_repo.get_latest_by_kb(kb.id, limit=3)

            kb_info = {
                "id": str(kb.id),
                "name": kb.name,
                "display_name": kb.display_name,
                "status": kb.status,
                "created_at": kb.created_at.isoformat(),
                "last_queried_at": kb.last_queried_at.isoformat() if kb.last_queried_at else None,
                "statistics": stats,
                "latest_uploads": [
                    {
                        "id": str(u.id),
                        "filename": u.original_filename,
                        "display_name": u.display_name,
                        "upload_date": u.created_at.isoformat(),
                        "pages": u.page_count,
                        "chunks": u.chunk_count,
                        "vectors": u.total_vectors,
                        "status": u.processing_status,
                    }
                    for u in latest_uploads
                ],
            }
            kb_summaries.append(kb_info)

            # Accumulate totals
            total_uploads += stats["total_uploads"]
            total_pages += stats["total_pages"]
            total_chunks += stats["total_chunks"]
            total_vectors += stats["total_vectors"]
            total_queries += stats["query_count"]

        return {
            "organization_id": str(tenant_context.organization_id),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_knowledge_bases": len(kbs),
                "total_uploads": total_uploads,
                "total_pages": total_pages,
                "total_chunks": total_chunks,
                "total_vectors": total_vectors,
                "total_queries": total_queries,
            },
            "knowledge_bases": kb_summaries,
        }
    except Exception as e:
        app_logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")


# ──────────────────────────────────────────────────────────────────────────────
# Query Analytics Endpoint
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/queries", response_model=Dict[str, Any])
async def get_query_analytics(
    days: int = Query(7, ge=1, le=90),
    kb_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get query analytics for specified time period.
    
    - **days**: Number of days to analyze (1-90)
    - **kb_id**: Optional KB filter
    - **limit**: Max number of queries to return
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Build query
        stmt = (
            select(QueryLog)
            .where(
                and_(
                    QueryLog.organization_id == tenant_context.organization_id,
                    QueryLog.created_at >= start_date,
                )
            )
            .order_by(QueryLog.created_at.desc())
            .limit(limit)
        )

        # Filter by KB if specified
        if kb_id:
            try:
                kb_uuid = uuid.UUID(kb_id)
                stmt = stmt.where(QueryLog.knowledge_base_id == kb_uuid)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid KB UUID")

        res = await db.execute(stmt)
        queries = list(res.scalars().all())

        # Calculate statistics
        total_queries = len(queries)
        avg_latency = (
            sum(q.latency_ms for q in queries) / total_queries
            if queries
            else 0
        )
        total_retrieved = sum(q.retrieved_count for q in queries)
        avg_retrieved = total_retrieved / total_queries if queries else 0

        # Group by KB
        kb_stats = {}
        for query in queries:
            kb_key = str(query.knowledge_base_id) if query.knowledge_base_id else "all"
            if kb_key not in kb_stats:
                kb_stats[kb_key] = {
                    "count": 0,
                    "total_latency_ms": 0,
                    "total_retrieved": 0,
                }
            kb_stats[kb_key]["count"] += 1
            kb_stats[kb_key]["total_latency_ms"] += query.latency_ms
            kb_stats[kb_key]["total_retrieved"] += query.retrieved_count

        kb_summary = {
            kb_id: {
                "query_count": stats["count"],
                "avg_latency_ms": round(
                    stats["total_latency_ms"] / stats["count"], 2
                ),
                "avg_retrieved": round(
                    stats["total_retrieved"] / stats["count"], 2
                ),
            }
            for kb_id, stats in kb_stats.items()
        }

        return {
            "organization_id": str(tenant_context.organization_id),
            "period_days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_queries": total_queries,
                "avg_latency_ms": round(avg_latency, 2),
                "avg_retrieved_chunks": round(avg_retrieved, 2),
                "total_retrieved_chunks": total_retrieved,
            },
            "by_knowledge_base": kb_summary,
            "recent_queries": [
                {
                    "id": str(q.id),
                    "query": q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text,
                    "knowledge_base_id": str(q.knowledge_base_id) if q.knowledge_base_id else None,
                    "retrieved_count": q.retrieved_count,
                    "latency_ms": round(q.latency_ms, 2),
                    "used_uploads": q.used_upload_ids or [],
                    "created_at": q.created_at.isoformat(),
                }
                for q in queries[:20]
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting query analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve query analytics")


# ──────────────────────────────────────────────────────────────────────────────
# Usage Analytics Endpoint
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/usage", response_model=Dict[str, Any])
async def get_usage_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get usage analytics for organization.
    
    - **days**: Number of days to analyze (1-365)
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get query logs for period
        stmt = (
            select(QueryLog)
            .where(
                and_(
                    QueryLog.organization_id == tenant_context.organization_id,
                    QueryLog.created_at >= start_date,
                )
            )
        )
        res = await db.execute(stmt)
        queries = list(res.scalars().all())

        # Get chat message counts
        chat_stmt = (
            select(ChatMessage)
            .join(ChatSession)
            .where(
                and_(
                    ChatSession.organization_id == tenant_context.organization_id,
                    ChatMessage.created_at >= start_date,
                )
            )
        )
        chat_res = await db.execute(chat_stmt)
        chat_messages = list(chat_res.scalars().all())

        # Get uploads
        upload_stmt = (
            select(Upload)
            .where(
                and_(
                    Upload.organization_id == tenant_context.organization_id,
                    Upload.created_at >= start_date,
                )
            )
        )
        upload_res = await db.execute(upload_stmt)
        uploads = list(upload_res.scalars().all())

        # Calculate statistics
        total_queries = len(queries)
        total_chat_messages = len(chat_messages)
        total_uploads = len(uploads)
        total_pages = sum(u.page_count for u in uploads)
        total_vectors = sum(u.total_vectors for u in uploads)
        avg_processing_time = (
            sum(u.processing_duration_ms for u in uploads) / len(uploads)
            if uploads
            else 0
        )

        # Daily breakdown
        daily_stats = {}
        for query in queries:
            day_key = query.created_at.date().isoformat()
            if day_key not in daily_stats:
                daily_stats[day_key] = {"queries": 0, "retrieved": 0, "latency": 0}
            daily_stats[day_key]["queries"] += 1
            daily_stats[day_key]["retrieved"] += query.retrieved_count
            daily_stats[day_key]["latency"] += query.latency_ms

        return {
            "organization_id": str(tenant_context.organization_id),
            "period_days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_queries": total_queries,
                "total_chat_messages": total_chat_messages,
                "total_uploads": total_uploads,
                "total_pages_indexed": total_pages,
                "total_vectors": total_vectors,
                "avg_upload_processing_time_ms": round(avg_processing_time, 2),
                "queries_per_day": round(total_queries / max(days, 1), 2),
                "messages_per_day": round(total_chat_messages / max(days, 1), 2),
            },
            "daily_breakdown": [
                {
                    "date": day,
                    "query_count": stats["queries"],
                    "retrieved_chunks": stats["retrieved"],
                    "avg_latency_ms": round(stats["latency"] / stats["queries"], 2)
                    if stats["queries"] > 0
                    else 0,
                }
                for day, stats in sorted(daily_stats.items(), reverse=True)
            ],
        }
    except Exception as e:
        app_logger.error(f"Error getting usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve usage analytics")


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge Base Statistics Endpoint
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/knowledge-bases/{kb_id}/detailed", response_model=Dict[str, Any])
async def get_kb_detailed_statistics(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed statistics for a specific knowledge base.
    
    Includes upload breakdown, query patterns, and performance metrics.
    """
    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid KB UUID")

    try:
        kb_repo = KnowledgeBaseRepository(db)
        kb = await kb_repo.get_by_id(kb_uuid)

        if not kb or kb.organization_id != tenant_context.organization_id:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get uploads
        upload_repo = UploadRepository(db)
        uploads = await upload_repo.get_by_kb(kb_uuid, skip=0, limit=1000)

        # Get query statistics
        query_stmt = (
            select(QueryLog)
            .where(QueryLog.knowledge_base_id == kb_uuid)
            .order_by(QueryLog.created_at.desc())
        )
        query_res = await db.execute(query_stmt)
        queries = list(query_res.scalars().all())

        # Calculate metrics
        total_upload_time = sum(u.processing_duration_ms for u in uploads)
        avg_upload_time = (
            total_upload_time / len(uploads) if uploads else 0
        )
        failed_uploads = len([u for u in uploads if u.processing_status == "failed"])
        total_latency = sum(q.latency_ms for q in queries)
        avg_query_latency = (
            total_latency / len(queries) if queries else 0
        )

        return {
            "kb_id": str(kb.id),
            "kb_name": kb.name,
            "kb_display_name": kb.display_name,
            "created_at": kb.created_at.isoformat(),
            "last_queried_at": kb.last_queried_at.isoformat() if kb.last_queried_at else None,
            "status": kb.status,
            "statistics": {
                "total_uploads": len(uploads),
                "completed_uploads": len([u for u in uploads if u.processing_status == "completed"]),
                "failed_uploads": failed_uploads,
                "total_pages": sum(u.page_count for u in uploads),
                "total_chunks": sum(u.chunk_count for u in uploads),
                "total_vectors": sum(u.total_vectors for u in uploads),
                "total_queries": len(queries),
                "avg_upload_time_ms": round(avg_upload_time, 2),
                "avg_query_latency_ms": round(avg_query_latency, 2),
            },
            "uploads": [
                {
                    "id": str(u.id),
                    "filename": u.original_filename,
                    "display_name": u.display_name,
                    "file_type": u.file_type,
                    "file_size_bytes": u.file_size_bytes,
                    "pages": u.page_count,
                    "chunks": u.chunk_count,
                    "vectors": u.total_vectors,
                    "embedding_model": u.embedding_model,
                    "status": u.processing_status,
                    "processing_time_ms": u.processing_duration_ms,
                    "error": u.error_message,
                    "created_at": u.created_at.isoformat(),
                    "tags": u.tags,
                }
                for u in uploads
            ],
            "recent_queries": [
                {
                    "query": q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text,
                    "retrieved_count": q.retrieved_count,
                    "latency_ms": round(q.latency_ms, 2),
                    "created_at": q.created_at.isoformat(),
                }
                for q in queries[:10]
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Error getting KB detailed statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve KB statistics")


# ──────────────────────────────────────────────────────────────────────────────
# Performance Metrics Endpoint
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    """
    Get performance metrics and health indicators.
    
    - **days**: Time period for analysis (1-90)
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get query logs
        stmt = (
            select(QueryLog)
            .where(
                and_(
                    QueryLog.organization_id == tenant_context.organization_id,
                    QueryLog.created_at >= start_date,
                )
            )
        )
        res = await db.execute(stmt)
        queries = list(res.scalars().all())

        if not queries:
            return {
                "organization_id": str(tenant_context.organization_id),
                "period_days": days,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "No queries found in this period",
                "metrics": {
                    "total_queries": 0,
                    "avg_latency_ms": 0,
                    "p50_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "p99_latency_ms": 0,
                },
            }

        # Calculate latency percentiles
        latencies = sorted([q.latency_ms for q in queries])
        p50 = latencies[len(latencies) // 2]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg = sum(latencies) / len(latencies)

        # Get upload stats
        upload_stmt = (
            select(Upload)
            .where(
                and_(
                    Upload.organization_id == tenant_context.organization_id,
                    Upload.created_at >= start_date,
                )
            )
        )
        upload_res = await db.execute(upload_stmt)
        uploads = list(upload_res.scalars().all())

        upload_times = sorted(
            [u.processing_duration_ms for u in uploads if u.processing_duration_ms > 0]
        )
        upload_p50 = upload_times[len(upload_times) // 2] if upload_times else 0
        upload_p95 = upload_times[int(len(upload_times) * 0.95)] if upload_times else 0

        return {
            "organization_id": str(tenant_context.organization_id),
            "period_days": days,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_metrics": {
                "total_queries": len(queries),
                "avg_latency_ms": round(avg, 2),
                "p50_latency_ms": round(p50, 2),
                "p95_latency_ms": round(p95, 2),
                "p99_latency_ms": round(p99, 2),
                "avg_retrieved_chunks": round(
                    sum(q.retrieved_count for q in queries) / len(queries), 2
                ),
            },
            "upload_metrics": {
                "total_uploads": len(uploads),
                "avg_processing_time_ms": round(
                    sum(u.processing_duration_ms for u in uploads) / len(uploads)
                    if uploads
                    else 0,
                    2,
                ),
                "p50_processing_time_ms": round(upload_p50, 2),
                "p95_processing_time_ms": round(upload_p95, 2),
                "failed_uploads": len([u for u in uploads if u.processing_status == "failed"]),
            },
        }
    except Exception as e:
        app_logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")
