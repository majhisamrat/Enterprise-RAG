import time
import uuid
from typing import Any, Dict, List, Optional
from app.utils.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage, ChatSession, RetrievedSource
from app.db.repositories.chat_repository import ChatRepository
from app.llm.provider import LLMProvider
from app.orchestrator.base import BaseOrchestrator
from app.orchestrator.utils import build_metadata, execution_time
from app.prompt_builder.builder import PromptBuilder
from app.retrieval.hybrid import HybridRetriever
from app.storage.redis_client import redis_manager


class RAGOrchestrator(BaseOrchestrator):
    """Production-grade Enterprise RAG Orchestrator."""

    def __init__(self):
        self.retriever = HybridRetriever()
        self.prompt_builder = PromptBuilder()
        # Initialize memory service for multi-layer memory
        from app.memory import get_memory_service
        self.memory_service = get_memory_service()

    @property
    def llm(self):
        return LLMProvider.load()

    async def chat(
        self,
        query: str,
        organization_id: Optional[uuid.UUID] = None,
        knowledge_base_id: Optional[uuid.UUID] = None,  # NEW: KB filter
        department: Optional[str] = None,
        session_id: Optional[uuid.UUID] = None,
        top_k: int = 10,
        db_session: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        logger.info(
            f"Starting RAG chat workflow for query: '{query}' "
            f"(Org: {organization_id}, KB: {knowledge_base_id})"
        )

        session_id_str = str(session_id) if session_id else None
        user_id = None
        session_obj = None
        conversation_history = []
        memory_history = []

        # Initialize memory service and session if not already done
        if session_id and db_session:
            chat_repo = ChatRepository(db_session)
            session_obj = await chat_repo.get_session_with_messages(session_id)
            if session_obj:
                user_id = str(session_obj.user_id) if session_obj.user_id else None
                # Initialize session in memory service
                await self.memory_service.initialize_session(
                    session_id_str,
                    user_id=user_id,
                    organization_id=str(organization_id) if organization_id else None,
                )
                
                # Build conversation history for context
                for msg in session_obj.messages[-6:]:
                    conversation_history.append({
                        "role": msg.sender_role,
                        "content": msg.content,
                    })
                
                # Load conversation memory for rewriting
                from app.memory import get_memory_manager
                memory_manager = get_memory_manager()
                db_messages = [
                    {
                        "role": msg.sender_role,
                        "content": msg.content,
                        "timestamp": msg.created_at,
                    }
                    for msg in session_obj.messages
                ]
                memory_manager.load_from_db_messages(session_id_str, db_messages)
                memory_history = memory_manager.get_history(session_id_str)
        
        # 3. Rewrite query using conversation history
        # Get KB name to pass to rewriter for better context
        kb_name: Optional[str] = None
        rewritten_query = query
        rewrite_needed = False
        rewrite_type = None
        rewrite_result = {}
        
        if knowledge_base_id and db_session:
            from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
            kb_repo = KnowledgeBaseRepository(db_session)
            kb_obj = await kb_repo.get_by_id(knowledge_base_id)
            if kb_obj:
                kb_name = kb_obj.display_name
        
        # Perform query rewriting if we have history
        if memory_history:
            from app.memory import get_query_rewriter, get_session_manager
            query_rewriter = get_query_rewriter()
            session_mgr = get_session_manager()
            
            # Get current session state for document context
            session_state = session_mgr.get_session(session_id_str)
            current_document_name = None
            if session_state and session_state.current_document_name:
                current_document_name = session_state.current_document_name
            
            # Use enhanced rewriter that preserves document context
            rewrite_result = query_rewriter.rewrite_with_state(
                query=query,
                history=memory_history,
                knowledge_base_name=kb_name,
                document_name=current_document_name,
            )
            
            rewritten_query = rewrite_result.get("rewritten_query", query)
            rewrite_needed = rewrite_result.get("rewrite_needed", False)
            rewrite_type = rewrite_result.get("rewrite_type")
        
        # Log rewriting metrics
        logger.info(
            f"Query Rewriting: original='{query}' | rewritten='{rewritten_query}' | "
            f"needed={rewrite_needed} | type={rewrite_type} | "
            f"history_length={rewrite_result.get('history_length', 0)}"
        )

        allowed_file_names: Optional[set] = None

        if knowledge_base_id and db_session:
            from app.db.repositories.knowledge_base_repository import KnowledgeBaseRepository
            from app.db.repositories.upload_repository import UploadRepository
            from pathlib import Path

            kb_repo = KnowledgeBaseRepository(db_session)
            upload_repo = UploadRepository(db_session)

            kb_obj = await kb_repo.get_by_id(knowledge_base_id)
            if kb_obj:
                kb_name = kb_obj.display_name
                await kb_repo.update_last_queried(knowledge_base_id)

            kb_uploads = await upload_repo.get_by_kb(knowledge_base_id, skip=0, limit=1000)
            allowed_file_names = set()
            for u in kb_uploads:
                if u.original_filename:
                    allowed_file_names.add(u.original_filename.lower())
                if u.storage_path:
                    allowed_file_names.add(Path(u.storage_path).name.lower())

        # 4. Perform Hybrid Retrieval with KB filtering
        # Use rewritten query for retrieval, but keep original for display
        retrieved_docs = self.retriever.retrieve(
            query=rewritten_query,  # Use rewritten query for better context
            limit=top_k,
            organization_id=organization_id,
            knowledge_base_id=knowledge_base_id,
            allowed_file_names=allowed_file_names if knowledge_base_id else None,
            department=department,
        )

        logger.info(
            f"Hybrid retrieval and reranking produced {len(retrieved_docs)} final context documents "
            f"(KB filtered: {knowledge_base_id is not None})."
        )

        # Update session state with retrieved documents
        if session_id_str:
            from app.memory import get_session_manager
            session_mgr = get_session_manager()
            
            # Ensure session exists
            session_mgr.get_or_create_session(
                session_id_str,
                user_id=user_id,
                organization_id=str(organization_id) if organization_id else None,
            )
            
            # Update KB context
            if knowledge_base_id and kb_name:
                session_mgr.update_knowledge_base(
                    session_id_str,
                    str(knowledge_base_id),
                    kb_name,
                )
            
            # Update retrieved sources (includes document name)
            session_mgr.update_retrieved_sources(
                session_id_str,
                [
                    {
                        "document_id": doc.get("document_id"),
                        "document_name": doc.get("document_name"),
                        "chunk_id": doc.get("chunk_id", doc.get("document_id")),
                        "page_number": doc.get("page_number", 1),
                        "text_snippet": doc.get("text", "")[:200],
                        "relevance_score": doc.get("rerank_score", doc.get("score", 0.0)),
                    }
                    for doc in retrieved_docs[:10]
                ],
            )
            
            # Update interaction metadata
            session_mgr.update_interaction(
                session_id_str,
                user_question=query,
                rewritten_question=rewritten_query if rewrite_needed else None,
            )

        # Update session state with retrieved documents (OLD - remove)
        if session_id_str:
            session_context_update = {
                "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else None,
                "knowledge_base_name": kb_name,
            }
            await self.memory_service.update_session_context(
                session_id_str,
                knowledge_base_id=str(knowledge_base_id) if knowledge_base_id else None,
                knowledge_base_name=kb_name,
            )

        # 4. Construct Prompt
        prompt = self.prompt_builder.build(
            query=query,
            documents=retrieved_docs,
            conversation_history=conversation_history,
            selected_kb_name=kb_name if knowledge_base_id else None,
        )

        # 5. Generate LLM Answer via Gemini 2.5 Flash
        llm_resp = self.llm.generate(prompt)


        latency_ms = (time.perf_counter() - start) * 1000.0

        # Format sources & citations with upload info (NEW)
        citations = []
        used_upload_ids = set()
        for idx, doc in enumerate(retrieved_docs, start=1):
            upload_id = doc.get("upload_id")
            if upload_id:
                used_upload_ids.add(upload_id)
            
            citations.append({
                "citation_key": f"[Source {idx}]",
                "document_id": doc.get("document_id"),
                "upload_id": upload_id,  # NEW: track upload
                "document_name": doc.get("document_name"),  # NEW: show source file
                "upload_date": doc.get("upload_date"),  # NEW: show when uploaded
                "title": doc.get("title") or doc.get("document", "Document"),
                "page_number": doc.get("page_number") or doc.get("page", 1),
                "text_snippet": doc.get("text", "")[:200] + "...",
                "relevance_score": doc.get("rerank_score") or doc.get("rrf_score") or doc.get("score", 0.0),
            })

        # 6. Persist Chat Messages in Database if session available
        if session_id and db_session:
            chat_repo = ChatRepository(db_session)

            user_msg = ChatMessage(
                session_id=session_id,
                sender_role="user",
                content=query,  # Store original query for user clarity
                tokens_used=len(query.split()),
            )
            await chat_repo.add_message(user_msg)

            assistant_msg = ChatMessage(
                session_id=session_id,
                sender_role="assistant",
                content=llm_resp.answer,
                tokens_used=llm_resp.total_tokens,
            )
            await chat_repo.add_message(assistant_msg)
            
            # 7. Update comprehensive memory service
            if session_id_str:
                # Get last few messages for conversation history context
                conversation_history = []
                if session_obj and session_obj.messages:
                    for msg in session_obj.messages[-5:]:
                        conversation_history.append({
                            "role": msg.sender_role,
                            "content": msg.content,
                        })
                
                # Process interaction with memory service (multi-layer memory update)
                interaction_result = await self.memory_service.process_interaction(
                    session_id=session_id_str,
                    user_id=user_id,  # Pass user_id for Mem0 storage
                    user_question=query,
                    retrieved_documents=[
                        {
                            "document_id": doc.get("document_id"),
                            "document_name": doc.get("document_name"),
                            "chunk_id": doc.get("chunk_id", doc.get("document_id")),
                            "page_number": doc.get("page_number", 1),
                            "text_snippet": doc.get("text", "")[:200],
                            "relevance_score": doc.get("rerank_score", doc.get("score", 0.0)),
                        }
                        for doc in retrieved_docs[:10]
                    ],
                    answer=llm_resp.answer,
                    conversation_history=conversation_history,
                )
                
                # Log comprehensive interaction metrics
                logger.info(
                    f"Memory Update: topic={interaction_result.get('topic')} | "
                    f"rewrite={interaction_result.get('rewrite_needed')} | "
                    f"stored_in_mem0={interaction_result.get('stored_in_mem0')} | "
                    f"context=[{interaction_result.get('context_summary')}]"
                )

            # Persist citations
            for cit in citations:
                doc_id_raw = cit.get("document_id")
                if doc_id_raw:
                    try:
                        doc_uuid = uuid.UUID(str(doc_id_raw))
                        source_rec = RetrievedSource(
                            message_id=assistant_msg.id,
                            document_id=doc_uuid,
                            chunk_id=str(doc_id_raw),
                            relevance_score=float(cit.get("relevance_score") or 0.0),
                            page_number=int(cit.get("page_number") or 1),
                            text_snippet=str(cit.get("text_snippet") or ""),
                        )
                        db_session.add(source_rec)
                    except (ValueError, TypeError):
                        pass

            # Log query for analytics (NEW)
            from app.db.models import QueryLog
            query_log = QueryLog(
                user_id=session_obj.user_id if session_obj else None,
                organization_id=organization_id,
                knowledge_base_id=knowledge_base_id,
                query_text=query,
                retrieved_count=len(retrieved_docs),
                latency_ms=latency_ms,
                used_upload_ids=list(used_upload_ids),
            )
            db_session.add(query_log)
            await db_session.commit()

        logger.success(f"RAG chat workflow completed in {latency_ms:.2f}ms")

        # Build comprehensive response metadata
        response_metadata = {
            "model": llm_resp.model_name,
            "prompt_tokens": llm_resp.prompt_tokens,
            "completion_tokens": llm_resp.completion_tokens,
            "total_tokens": llm_resp.total_tokens,
            "latency_ms": round(latency_ms, 2),
            "context_documents": len(retrieved_docs),
            "kb_filtered": knowledge_base_id is not None,
            "used_uploads": list(used_upload_ids),
            # Query rewriting metadata
            "query_rewriting": {
                "original_query": query,
                "rewritten_query": rewritten_query if rewrite_needed else None,
                "rewrite_needed": rewrite_needed,
                "rewrite_type": rewrite_type,
                "conversation_memory_length": len(memory_history) if session_id_str else 0,
            },
        }
        
        # Add session context if available
        if session_id_str:
            session_context = self.memory_service.get_session_context(session_id_str)
            response_metadata["session_context"] = session_context
        
        return {
            "answer": llm_resp.answer,
            "session_id": str(session_id) if session_id else None,
            "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else None,
            "sources": citations,
            "metadata": response_metadata,
        }