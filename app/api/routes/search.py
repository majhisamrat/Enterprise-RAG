from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import User
from app.utils.logger import app_logger

router = APIRouter(prefix="/search", tags=["Search"])

_retriever = None


def get_retriever():
    global _retriever
    if _retriever is None:
        from app.retrieval.hybrid import HybridRetriever
        _retriever = HybridRetriever()
    return _retriever


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    department: Optional[str] = None


@router.post("/")
async def search(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
):
    try:
        app_logger.info(f"Hybrid Search Query: '{request.query}'")
        target_department = request.department or tenant_context.department

        retriever_instance = get_retriever()
        results = retriever_instance.retrieve(
            query=request.query,
            limit=request.top_k,
            organization_id=tenant_context.organization_id,
            department=target_department,
        )

        return {
            "query": request.query,
            "organization_id": str(tenant_context.organization_id),
            "department": target_department,
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        app_logger.exception(f"Search endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))