import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import TenantContext, get_current_user, get_tenant_context
from app.db.models import ChatSession, User
from app.db.repositories.chat_repository import ChatRepository
from app.db.session import get_db
from app.utils.logger import app_logger

router = APIRouter(prefix="/chat", tags=["Chat"])

_orchestrator_instance = None

def get_orchestrator():
    global _orchestrator_instance
    if _orchestrator_instance is None:
        from app.orchestrator.rag import RAGOrchestrator
        _orchestrator_instance = RAGOrchestrator()
    return _orchestrator_instance


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    knowledge_base_id: Optional[str] = None  # NEW: optional KB filter
    top_k: int = 10


class ChatResponse(BaseModel):
    answer: str
    session_id: Optional[str]
    knowledge_base_id: Optional[str]  # NEW: show which KB was used
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse, include_in_schema=False)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
):
    try:
        app_logger.info(
            f"Chat Request from user {current_user.id}: {request.query} "
            f"(KB: {request.knowledge_base_id})"
        )

        org_id = tenant_context.organization_id or getattr(current_user, "organization_id", None) or uuid.UUID("00000000-0000-0000-0000-000000000001")
        usr_id = getattr(current_user, "id", None) or uuid.UUID("00000000-0000-0000-0000-000000000001")

        # Parse KB ID if provided
        kb_uuid = None
        if request.knowledge_base_id:
            try:
                kb_uuid = uuid.UUID(request.knowledge_base_id)
                # Verify KB belongs to org
                from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
                kb_repo = KnowledgeBaseRepository(db)
                kb = await kb_repo.get_by_id(kb_uuid)
                if not kb or kb.organization_id != org_id:
                    raise HTTPException(
                        status_code=404,
                        detail="Knowledge base not found or does not belong to your organization"
                    )
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid knowledge_base_id UUID")

        sess_uuid = None
        if request.session_id:
            try:
                sess_uuid = uuid.UUID(request.session_id)
            except ValueError:
                pass
        else:
            chat_repo = ChatRepository(db)
            new_session = ChatSession(
                organization_id=org_id,
                user_id=usr_id,
                knowledge_base_id=kb_uuid,  # NEW: associate with KB
                title=request.query[:50],
            )
            await chat_repo.create(new_session)
            sess_uuid = new_session.id

        orchestrator_instance = get_orchestrator()
        response = await orchestrator_instance.chat(
            query=request.query,
            organization_id=tenant_context.organization_id,
            knowledge_base_id=kb_uuid,  # NEW: pass KB filter to retriever
            department=tenant_context.department,
            session_id=sess_uuid,
            top_k=request.top_k,
            db_session=db,
        )

        return ChatResponse(
            answer=response["answer"],
            session_id=str(sess_uuid) if sess_uuid else None,
            knowledge_base_id=str(kb_uuid) if kb_uuid else None,  # NEW: return KB info
            sources=response["sources"],
            metadata=response["metadata"],
        )
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))