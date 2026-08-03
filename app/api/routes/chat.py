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
    force_new_session: Optional[bool] = False  # NEW: frontend can force new session
    top_k: int = 10


class ChatResponse(BaseModel):
    answer: str
    session_id: Optional[str]
    knowledge_base_id: Optional[str]
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    session_changed: Optional[bool] = False  # NEW: indicates if session was auto-created


# 📋 CHAT HISTORY ENDPOINTS

@router.get("/history")
async def get_user_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    📜 Get user's chat history (list of chat sessions).
    
    Returns a list of chat sessions with basic info for the sidebar.
    """
    try:
        user_id = getattr(current_user, "id", None)
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        chat_repo = ChatRepository(db)
        sessions = await chat_repo.get_user_sessions(user_id, limit)
        
        # Format sessions for frontend
        formatted_sessions = []
        for session in sessions:
            kb_name = "All Knowledge Bases"
            if session.knowledge_base_id:
                try:
                    from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
                    kb_repo = KnowledgeBaseRepository(db)
                    kb = await kb_repo.get_by_id(session.knowledge_base_id)
                    if kb:
                        kb_name = kb.display_name
                except Exception:
                    kb_name = "Unknown KB"
            
            # Count messages if available
            message_count = 0
            if hasattr(session, 'messages') and session.messages:
                message_count = len(session.messages)
            
            formatted_sessions.append({
                "session_id": str(session.id),
                "title": session.title or "Untitled Chat",
                "knowledge_base_id": str(session.knowledge_base_id) if session.knowledge_base_id else None,
                "knowledge_base_name": kb_name,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "message_count": message_count,
            })
        
        app_logger.info(f"Retrieved {len(formatted_sessions)} chat sessions for user {user_id}")
        
        return {
            "sessions": formatted_sessions,
            "total": len(formatted_sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.get("/history/{session_id}")
async def get_chat_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    💬 Get full conversation history for a specific chat session.
    
    Returns all messages in the session with sources and metadata.
    """
    try:
        user_id = getattr(current_user, "id", None)
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        sess_uuid = uuid.UUID(session_id)
        chat_repo = ChatRepository(db)
        session = await chat_repo.get_session_with_messages(sess_uuid)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
        # Verify session belongs to user
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this chat session")
        
        # Get KB info
        kb_name = "All Knowledge Bases" 
        if session.knowledge_base_id:
            try:
                from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
                kb_repo = KnowledgeBaseRepository(db)
                kb = await kb_repo.get_by_id(session.knowledge_base_id)
                if kb:
                    kb_name = kb.display_name
            except Exception:
                pass
        
        # Format messages
        formatted_messages = []
        if hasattr(session, 'messages') and session.messages:
            for message in session.messages:
                # Format sources for this message
                sources = []
                if hasattr(message, 'retrieved_sources') and message.retrieved_sources:
                    for source in message.retrieved_sources:
                        sources.append({
                            "document_id": str(source.document_id) if source.document_id else None,
                            "chunk_id": source.chunk_id,
                            "page_number": source.page_number,
                            "relevance_score": float(source.relevance_score) if source.relevance_score else 0.0,
                            "text_snippet": source.text_snippet,
                        })
                
                formatted_messages.append({
                    "id": str(message.id),
                    "sender_role": message.sender_role,
                    "content": message.content,
                    "tokens_used": message.tokens_used,
                    "created_at": message.created_at.isoformat() if message.created_at else None,
                    "sources": sources,
                })
        
        app_logger.info(f"Retrieved session {session_id} with {len(formatted_messages)} messages")
        
        return {
            "session": {
                "id": str(session.id),
                "title": session.title,
                "knowledge_base_id": str(session.knowledge_base_id) if session.knowledge_base_id else None,
                "knowledge_base_name": kb_name,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            },
            "messages": formatted_messages,
            "total_messages": len(formatted_messages)
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session messages")


@router.delete("/history/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    🗑️ Delete a specific chat session and all its messages.
    """
    try:
        user_id = getattr(current_user, "id", None)
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        sess_uuid = uuid.UUID(session_id)
        chat_repo = ChatRepository(db)
        session = await chat_repo.get_session_by_id(sess_uuid)
        
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
        # Verify session belongs to user
        if session.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this chat session")
        
        # Delete the session (cascades to messages and sources)
        await chat_repo.delete(session)
        await db.commit()
        
        app_logger.info(f"Deleted chat session {session_id} for user {user_id}")
        
        return {"success": True, "message": "Chat session deleted successfully"}
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")





@router.get("/session/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Debug endpoint to check session information."""
    try:
        sess_uuid = uuid.UUID(session_id)
        chat_repo = ChatRepository(db)
        session = await chat_repo.get_session_by_id(sess_uuid)
        
        if session:
            return {
                "session_id": str(session.id),
                "knowledge_base_id": str(session.knowledge_base_id) if session.knowledge_base_id else None,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "user_id": str(session.user_id),
                "organization_id": str(session.organization_id),
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    except Exception as e:
        app_logger.exception(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
            f"(KB: {request.knowledge_base_id}, Session: {request.session_id})"
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

        # 🎯 NEW: Auto-create new session logic when KB changes
        sess_uuid = None
        create_new_session = False
        session_change_reason = None
        
        # Force new session if requested by frontend
        if request.force_new_session:
            session_change_reason = "Frontend requested new session"
            create_new_session = True
            app_logger.info(f"🔄 {session_change_reason}")
        elif request.session_id:
            try:
                sess_uuid = uuid.UUID(request.session_id)
                
                # Check if session exists and get its KB
                chat_repo = ChatRepository(db)
                existing_session = await chat_repo.get_session_by_id(sess_uuid)
                
                if existing_session:
                    # 🔄 Check if KB has changed - if so, create new session
                    session_kb_id = existing_session.knowledge_base_id
                    current_kb_id = kb_uuid
                    
                    # Convert to strings for comparison to handle None values properly
                    session_kb_str = str(session_kb_id) if session_kb_id else None
                    current_kb_str = str(current_kb_id) if current_kb_id else None
                    
                    if session_kb_str != current_kb_str:
                        session_change_reason = f"KB changed: {session_kb_str} → {current_kb_str}"
                        app_logger.info(f"🔄 {session_change_reason}")
                        create_new_session = True
                        sess_uuid = None
                    else:
                        app_logger.info(f"✅ Continuing session {sess_uuid} for same KB {current_kb_str}")
                else:
                    # Session doesn't exist, create new one
                    session_change_reason = "Session not found"
                    create_new_session = True
                    sess_uuid = None
                    
            except ValueError:
                session_change_reason = "Invalid session ID"
                create_new_session = True
                sess_uuid = None
        else:
            # No session provided, create new one
            session_change_reason = "No session provided"
            create_new_session = True

        # Create new session if needed
        if create_new_session or sess_uuid is None:
            chat_repo = ChatRepository(db)
            kb_name = ""
            if kb_uuid:
                from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
                kb_repo = KnowledgeBaseRepository(db)
                kb = await kb_repo.get_by_id(kb_uuid)
                if kb:
                    kb_name = f" | {kb.display_name}"
            
            # Generate a more descriptive title
            session_title = f"{request.query[:30]}...{kb_name}"
            
            new_session = ChatSession(
                organization_id=org_id,
                user_id=usr_id,
                knowledge_base_id=kb_uuid,  # Associate with current KB
                title=session_title,
            )
            await chat_repo.create(new_session)
            sess_uuid = new_session.id
            
            app_logger.info(
                f"✨ Created NEW session {sess_uuid} for KB {kb_uuid} "
                f"(Reason: {session_change_reason})"
            )

        orchestrator_instance = get_orchestrator()
        response = await orchestrator_instance.chat(
            query=request.query,
            organization_id=tenant_context.organization_id,
            knowledge_base_id=kb_uuid,  # Pass KB filter to retriever
            department=tenant_context.department,
            session_id=sess_uuid,
            top_k=request.top_k,
            db_session=db,
        )

        return ChatResponse(
            answer=response["answer"],
            session_id=str(sess_uuid) if sess_uuid else None,
            knowledge_base_id=str(kb_uuid) if kb_uuid else None,
            sources=response["sources"],
            metadata=response["metadata"],
            session_changed=create_new_session,  # NEW: tell frontend if session changed
        )
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))