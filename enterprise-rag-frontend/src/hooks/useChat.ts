import { useChatStore } from '../store/chatStore';
import { askChat } from '../api/chat';

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

    try {
      // Call the actual backend API
      const response = await askChat(text, activeSession?.id, 5);

      const assistantMsg = {
        id: 'msg-' + (Date.now() + 1),
        sender: 'assistant' as const,
        content: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: response.sources?.map((src: any, idx: number) => ({
          id: `s${idx + 1}`,
          title: src.document_name || src.title || 'Document',
          score: src.score || 0,
          snippet: src.chunk_text || src.snippet || '',
          pageNumber: src.page_number || src.pageNumber,
        })) || [],
        tokensUsed: response.metadata?.tokens_used,
        latencyMs: response.metadata?.latency_ms,
      };

      addMessage(assistantMsg);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMsg = {
        id: 'msg-' + (Date.now() + 1),
        sender: 'assistant' as const,
        content: '❌ Failed to get response from the server. Please make sure the backend is running and try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      
      addMessage(errorMsg);
    } finally {
      setIsGenerating(false);
    }
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
