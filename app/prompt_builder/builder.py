from typing import Any, Dict, List, Optional
from app.prompt_builder.base import BasePromptBuilder
from app.prompt_builder.context import SYSTEM_PROMPT


class PromptBuilder(BasePromptBuilder):
    """Production-grade Prompt Builder with strict citation formatting and context boundary control."""

    def __init__(self, system_instruction: Optional[str] = None):
        self.system_instruction = system_instruction or SYSTEM_PROMPT

    def build(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Construct prompt with system rules, formatted context sources, chat history, and user query."""
        context_blocks = []

        for idx, doc in enumerate(documents, start=1):
            doc_id = doc.get("document_id", "UnknownDoc")
            title = doc.get("title") or doc.get("document", "Document")
            page = doc.get("page_number") or doc.get("page", 1)
            text = doc.get("text", "").strip()

            block = (
                f"[Source {idx}] (Title: {title}, DocID: {doc_id}, Page: {page})\n"
                f"{text}\n"
            )
            context_blocks.append(block)

        context_str = "\n---\n".join(context_blocks) if context_blocks else "No relevant context found."

        history_str = ""
        if conversation_history:
            history_blocks = []
            for msg in conversation_history:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                history_blocks.append(f"{role}: {content}")
            history_str = f"\n\n=========================\nCONVERSATION HISTORY\n=========================\n" + "\n".join(history_blocks)

        prompt = f"""{self.system_instruction}

=========================
RETRIEVED CONTEXT DOCUMENTS
=========================
{context_str}{history_str}

=========================
USER QUESTION
=========================
{query}

=========================
ENTERPRISE ASSISTANT RESPONSE
=========================
"""
        return prompt.strip()