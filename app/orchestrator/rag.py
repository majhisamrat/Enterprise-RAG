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
        department: Optional[str] = None,
        session_id: Optional[uuid.UUID] = None,
        top_k: int = 10,
        db_session: Optional[AsyncSession] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        start = time.perf_counter()
        logger.info(f"Starting RAG chat workflow for query: '{query}' (Org: {organization_id})")

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

        # 2. Perform Hybrid Retrieval (Dense + Sparse + RRF + Cross-Encoder Rerank)
        retrieved_docs = self.retriever.retrieve(
            query=query,
            limit=top_k,
            organization_id=organization_id,
            department=department,
        )

        logger.info(f"Hybrid retrieval and reranking produced {len(retrieved_docs)} final context documents.")

        # 3. Construct Prompt
        prompt = self.prompt_builder.build(
            query=query,
            documents=retrieved_docs,
            conversation_history=conversation_history,
        )

        # 4. Generate LLM Answer via Gemini 2.5 Flash
        llm_resp = self.llm.generate(prompt)

        latency_ms = (time.perf_counter() - start) * 1000.0

        # Format sources & citations
        citations = []
        for idx, doc in enumerate(retrieved_docs, start=1):
            citations.append({
                "citation_key": f"[Source {idx}]",
                "document_id": doc.get("document_id"),
                "title": doc.get("title") or doc.get("document", "Document"),
                "page_number": doc.get("page_number") or doc.get("page", 1),
                "text_snippet": doc.get("text", "")[:200] + "...",
                "relevance_score": doc.get("rerank_score") or doc.get("rrf_score") or doc.get("score", 0.0),
            })

        # 5. Persist Chat Messages in Database if session available
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

        logger.success(f"RAG chat workflow completed in {latency_ms:.2f}ms")

        return {
            "answer": llm_resp.answer,
            "session_id": str(session_id) if session_id else None,
            "sources": citations,
            "metadata": {
                "model": llm_resp.model_name,
                "prompt_tokens": llm_resp.prompt_tokens,
                "completion_tokens": llm_resp.completion_tokens,
                "total_tokens": llm_resp.total_tokens,
                "latency_ms": round(latency_ms, 2),
                "context_documents": len(retrieved_docs),
            },
        }