import { useChatStore } from '../store/chatStore';

export function useChat() {
  const {
    sessions,
    activeSessionId,
    attachedDoc,
    isGenerating,
    setAttachedDoc,
    createSession,
    setActiveSession,
    addMessage,
    updateMessage,
    deleteSession,
    renameSession,
    clearActiveChat,
    setIsGenerating,
  } = useChatStore();

  const activeSession = sessions.find((s) => s.id === activeSessionId) || sessions[0];

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMsg = {
      id: 'msg-' + Date.now(),
      sender: 'user' as const,
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      attachedDoc: attachedDoc ? { name: attachedDoc.name, size: attachedDoc.size } : undefined,
    };

    addMessage(userMsg);
    setAttachedDoc(null);
    setIsGenerating(true);

    setTimeout(() => {
      const assistantMsg = {
        id: 'msg-' + (Date.now() + 1),
        sender: 'assistant' as const,
        content: `Based on your internal enterprise knowledge base, here is the answer:

**Key Takeaways:**
- **Indexed Content:** Verified against attached document sources.
- **Hybrid Search Score:** Combined dense vector embeddings with BM25 keyword matching for high precision.
- **Performance:** Retained context window within 2048 output tokens.

Would you like me to analyze any additional sections or extract table metrics?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: [
          {
            id: 's1',
            title: userMsg.attachedDoc?.name || 'Enterprise_Docs.pdf',
            score: 0.96,
            snippet: 'Relevant context retrieved from chunk #14...',
            pageNumber: 2,
          },
        ],
        tokensUsed: 284,
        latencyMs: 142,
      };

      addMessage(assistantMsg);
      setIsGenerating(false);
    }, 1200);
  };

  return {
    sessions,
    activeSession,
    activeSessionId,
    attachedDoc,
    isGenerating,
    sendMessage,
    createSession,
    setActiveSession,
    deleteSession,
    renameSession,
    clearActiveChat,
    setAttachedDoc,
  };
}
