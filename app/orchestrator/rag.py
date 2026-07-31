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

        # 1. Fetch conversation history if session_id provided
        conversation_history = []
        if session_id and db_session:
            chat_repo = ChatRepository(db_session)
            session_obj = await chat_repo.get_session_with_messages(session_id)
            if session_obj:
                for msg in session_obj.messages[-6:]:  # Last 6 messages context window
                    conversation_history.append({
                        "role": msg.sender_role,
                        "content": msg.content,
                    })

        kb_name: Optional[str] = None
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

        # 2. Perform Hybrid Retrieval with KB filtering
        retrieved_docs = self.retriever.retrieve(
            query=query,
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
                content=query,
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

        return {
            "answer": llm_resp.answer,
            "session_id": str(session_id) if session_id else None,
            "knowledge_base_id": str(knowledge_base_id) if knowledge_base_id else None,  # NEW
            "sources": citations,
            "metadata": {
                "model": llm_resp.model_name,
                "prompt_tokens": llm_resp.prompt_tokens,
                "completion_tokens": llm_resp.completion_tokens,
                "total_tokens": llm_resp.total_tokens,
                "latency_ms": round(latency_ms, 2),
                "context_documents": len(retrieved_docs),
                "kb_filtered": knowledge_base_id is not None,  # NEW: show if filtered
                "used_uploads": list(used_upload_ids),  # NEW: show which uploads
            },
        }