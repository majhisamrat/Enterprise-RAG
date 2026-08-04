import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { useKnowledgeBases } from '@/hooks/useKnowledge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Send, Brain, User, Loader2, BookOpen, Plus, ArrowUpRight, ChevronLeft, ChevronRight, Sparkles, MessageSquare, Trash2 } from 'lucide-react';
import type { ChatMessageDisplay } from '@/types/chat';
import { FadeIn } from '@/components/shared/motion';
import { cn } from '@/lib/utils';

const promptSuggestions = [
  'Summarize the key takeaways from the latest uploaded reports',
  'What are the compliance requirements outlined in the documents?',
  'Extract financial metrics and revenue figures from Q1 reports',
  'List all action items mentioned in meeting transcripts',
];

const getAuthToken = () => localStorage.getItem('access_token') ?? localStorage.getItem('token') ?? '';

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageDisplay[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const [chatHistoryData, setChatHistoryData] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [currentSessionTitle, setCurrentSessionTitle] = useState<string>('');
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const chatMutation = useChat();
  const { data: kbs } = useKnowledgeBases();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch chat history on component mount
  useEffect(() => {
    fetchChatHistory();
  }, []);

  // Fetch chat history
  const fetchChatHistory = async () => {
    setLoadingHistory(true);
    try {
      const token = getAuthToken();
      const response = await fetch('/api/v1/chat/history', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setChatHistoryData(data.sessions || []);
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  // Load specific chat session
  const loadChatSession = async (sessionIdToLoad: string) => {
    if (sessionIdToLoad === sessionId) return; // Already loaded
    
    setLoadingSession(true);
    try {
      const token = getAuthToken();
      const response = await fetch(`/api/v1/chat/history/${sessionIdToLoad}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Convert messages to display format
        const convertedMessages: ChatMessageDisplay[] = data.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.sender_role,
          content: msg.content,
          sources: msg.sources,
          timestamp: new Date(msg.created_at),
        }));
        
        setMessages(convertedMessages);
        setSessionId(sessionIdToLoad);
        setCurrentSessionTitle(data.session.title || 'Untitled Chat');
        
        // Set KB if session has one
        if (data.session.knowledge_base_id) {
          setSelectedKb(data.session.knowledge_base_id);
        } else {
          setSelectedKb('all');
        }
        
        // Close history after loading
        setHistoryExpanded(false);
      }
    } catch (error) {
      console.error('Error loading chat session:', error);
    } finally {
      setLoadingSession(false);
    }
  };

  // Delete chat session
  const deleteChatSession = async (sessionIdToDelete: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent session from loading when delete is clicked
    
    if (!confirm('Delete this chat session? This action cannot be undone.')) return;
    
    try {
      const token = getAuthToken();
      const response = await fetch(`/api/v1/chat/history/${sessionIdToDelete}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        // Refresh history and clear current chat if it was deleted
        await fetchChatHistory();
        if (sessionId === sessionIdToDelete) {
          startNewChat();
        }
      }
    } catch (error) {
      console.error('Error deleting chat session:', error);
    }
  };

  // Start new chat
  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setCurrentSessionTitle('');
    setSelectedKb('all');
  };

  const handleSend = async (customQuery?: string) => {
    const query = (customQuery || input).trim();
    if (!query || chatMutation.isPending) return;

    const userMsg: ChatMessageDisplay = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!customQuery) setInput('');

    try {
      const res = await chatMutation.mutateAsync({
        query,
        session_id: sessionId || undefined,
        knowledge_base_id: selectedKb && selectedKb !== 'all' ? selectedKb : undefined,
        top_k: 10,
      });

      // Update session ID if new session was created
      if (res.session_id && !sessionId) {
        setSessionId(res.session_id);
        setCurrentSessionTitle(query.slice(0, 50) + (query.length > 50 ? '...' : '')); // Auto-generate title from first message
        // Refresh history to show the new session
        setTimeout(fetchChatHistory, 500);
      }

      const assistantMsg: ChatMessageDisplay = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        sources: res.sources,
        metadata: res.metadata,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      // Error handled by API interceptor
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center py-2 w-full">
      {/* ─── FIXED CHAT CONTAINER (LARGER HEIGHT) ─── */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-6xl h-[90vh] max-h-[1200px] min-h-[800px] flex flex-col bg-card/90 backdrop-blur-2xl border border-border/80 rounded-3xl shadow-2xl overflow-hidden glow-sm z-10">

        {/* ─── EDGE TOGGLE ARROW (LEFT EDGE OF FIXED CARD) ─── */}
        {!historyExpanded && (
          <button
            onClick={() => {
              setHistoryExpanded(true);
              if (chatHistoryData.length === 0) {
                fetchChatHistory();
              }
            }}
            title="Open chat history"
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 z-50 flex items-center justify-center w-7 h-14 rounded-r-xl rounded-l-md bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-lg shadow-slate-900/30 hover:from-primary hover:to-blue-700 hover:shadow-primary/30 transition-all duration-300 group border border-white/10"
          >
            <ChevronRight className="h-4 w-4 group-hover:translate-x-0.5 transition-transform" />
          </button>
        )}
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-border/70 bg-muted/30 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-md shadow-primary/20">
              <Brain className="h-5 w-5 text-white" />
              <Sparkles className="absolute -top-1 -right-1 h-3 w-3 text-sky-300 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-base tracking-tight text-foreground">
                  {currentSessionTitle || 'Atlas Assistant'}
                </h2>
                {loadingSession && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              {currentSessionTitle && (
                <p className="text-xs text-muted-foreground font-semibold">
                  Atlas Assistant
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Knowledge Base Filter */}
            <Select value={selectedKb} onValueChange={setSelectedKb}>
              <SelectTrigger className="w-[200px] h-10 text-xs font-bold rounded-xl bg-background/80 border-border">
                <SelectValue placeholder="All Knowledge Bases" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Knowledge Bases</SelectItem>
                {kbs?.map((kb) => (
                  <SelectItem key={kb.id} value={kb.id}>{kb.display_name}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* New Chat Button */}
            {sessionId && (
              <Button
                variant="outline"
                size="sm"
                onClick={startNewChat}
                className="gap-2 h-10 text-xs font-bold rounded-xl border-border hover:bg-muted px-4"
              >
                <Plus className="h-4 w-4" />
                New Chat
              </Button>
            )}
          </div>
        </div>

        {/* ─── MESSAGES AREA (TALLER CONTAINER) ─── */}
        <div className="flex-1 min-h-0 overflow-y-auto p-8 lg:p-10 bg-background/50">
          <div className="max-w-5xl mx-auto space-y-8 h-full">
            {messages.length === 0 ? (
              <FadeIn className="h-full flex flex-col justify-center items-center py-12 space-y-8 text-center">
                <div className="p-6 rounded-3xl bg-primary/10 border border-primary/20 shadow-lg glow-sm">
                  <MessageSquare className="h-12 w-12 text-primary" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold tracking-tight text-foreground">
                    Start a New Conversation
                  </h3>
                  <p className="text-base text-muted-foreground mt-2 max-w-lg leading-relaxed">
                    Ask questions about your knowledge base documents and get AI-powered insights.
                  </p>
                </div>

                {/* Prompt Suggestions */}
                <div className="w-full space-y-4">
                  <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Suggested Prompts
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
                    {promptSuggestions.map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(suggestion)}
                        className="p-5 text-left rounded-xl border border-border/80 bg-card/60 hover:bg-muted hover:border-primary/40 transition-all duration-200 text-base sm:text-lg font-semibold text-muted-foreground hover:text-foreground group flex items-start justify-between gap-3 shadow-sm"
                      >
                        <span className="leading-relaxed">{suggestion}</span>
                        <ArrowUpRight className="h-5 w-5 shrink-0 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                      </button>
                    ))}
                  </div>
                </div>
              </FadeIn>
            ) : (
              messages.map((msg) => (
                <FadeIn key={msg.id} direction="up" duration={0.3} className="space-y-3">
                  <div className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    {msg.role === 'assistant' && (
                      <Avatar className="h-10 w-10 mt-1 shrink-0 shadow-md shadow-primary/20">
                        <AvatarFallback className="bg-gradient-to-br from-primary via-blue-600 to-indigo-600 text-white font-bold text-sm">
                          <Brain className="h-5 w-5" />
                        </AvatarFallback>
                      </Avatar>
                    )}

                    <div className={`max-w-[80%] space-y-3 ${msg.role === 'user' ? 'order-first' : ''}`}>
                      {/* Message Card (LARGER IN TALLER CONTAINER) */}
                      <Card
                        className={`p-6 lg:p-8 rounded-2xl text-lg lg:text-xl leading-relaxed font-medium ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white border-transparent shadow-md shadow-purple-500/25'
                            : 'bg-card text-foreground border border-border/80 shadow-sm'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                      </Card>

                      {/* Sources */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="p-4 rounded-xl bg-muted/40 border border-border/60 space-y-2 text-xs">
                          <p className="text-muted-foreground font-bold flex items-center gap-2 text-xs uppercase tracking-wider">
                            <BookOpen className="h-4 w-4 text-primary" />
                            Sources ({msg.sources.length})
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {msg.sources.slice(0, 6).map((src, i) => (
                              <Badge key={i} variant="outline" className="text-xs font-semibold py-1 px-3 gap-1 bg-card/80 border-border">
                                <span className="font-mono text-primary text-xs">{src.citation_key}</span>
                                <span>-</span>
                                <span className="truncate max-w-[200px]">{src.document_name || src.title}</span>
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Metadata */}
                      {msg.metadata && (
                        <p className="text-xs text-muted-foreground font-mono px-1 font-semibold">
                          {msg.metadata.total_tokens} tokens • {msg.metadata.latency_ms.toFixed(0)}ms
                          {msg.metadata.kb_filtered && ' • KB filtered'}
                        </p>
                      )}
                    </div>

                    {msg.role === 'user' && (
                      <Avatar className="h-10 w-10 mt-1 shrink-0">
                        <AvatarFallback className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 text-purple-600 font-bold text-sm">
                          <User className="h-5 w-5" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                </FadeIn>
              ))
            )}

            {chatMutation.isPending && (
              <FadeIn className="flex items-center gap-4">
                <Avatar className="h-10 w-10 shadow-md shadow-primary/20">
                  <AvatarFallback className="bg-gradient-to-br from-primary via-blue-600 to-indigo-600 text-white">
                    <Brain className="h-5 w-5 animate-spin-slow" />
                  </AvatarFallback>
                </Avatar>
                <Card className="p-4 rounded-xl bg-card border border-border flex items-center gap-3 text-sm font-semibold text-muted-foreground">
                  <Loader2 className="h-4 w-4 text-primary animate-spin" />
                  <span className="animate-pulse">Thinking...</span>
                </Card>
              </FadeIn>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* ─── INPUT AREA ─── */}
        <div className="border-t border-border/70 bg-muted/20 shrink-0">
          {/* Input Box (SMALLER) */}
          <div className="p-4 relative">
            <div className="max-w-5xl mx-auto relative">

              <div className="relative rounded-2xl border border-border/80 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 shadow-lg p-4 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all">
                <Textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    selectedKb && selectedKb !== 'all'
                      ? `Ask about ${kbs?.find((k) => k.id === selectedKb)?.display_name}...`
                      : 'Ask anything across your knowledge bases...'
                  }
                  className="min-h-[60px] max-h-[160px] border-0 bg-transparent shadow-none focus-visible:ring-0 resize-none py-2 px-4 text-base font-medium placeholder:text-white/70 text-white"
                  rows={1}
                />

                <div className="flex items-center justify-between px-3 pt-2 border-t border-blue-500/30">
                  <span className="text-xs font-medium text-white">
                    Press <kbd className="px-1.5 py-0.5 rounded bg-white/30 font-mono text-xs font-bold text-white">Enter</kbd> to send
                  </span>

                  <Button
                    onClick={() => handleSend()}
                    disabled={!input.trim() || chatMutation.isPending}
                    size="default"
                    className="gap-2 shadow-lg shadow-primary/25 px-5 h-9 font-bold text-sm rounded-xl"
                  >
                    {chatMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <span>Send</span>
                        <Send className="h-4 w-4" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ─── SLIDE-IN HISTORY PANEL ─── */}
        {historyExpanded && (
          <div className="absolute inset-y-0 left-0 w-80 border-r border-border/40 bg-card/95 backdrop-blur-sm z-30 animate-in slide-in-from-left-full duration-300 rounded-l-3xl">

            {/* ─── EDGE TOGGLE ARROW (RIGHT EDGE OF SIDEBAR - shown when sidebar is OPEN) ─── */}
            <button
              onClick={() => setHistoryExpanded(false)}
              title="Close chat history"
              className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-50 flex items-center justify-center w-7 h-14 rounded-r-xl rounded-l-md bg-gradient-to-r from-slate-800 to-slate-900 text-white shadow-lg shadow-slate-900/30 hover:from-red-600 hover:to-red-700 hover:shadow-red-500/30 transition-all duration-300 group border border-white/10"
            >
              <ChevronLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
            </button>

            <div className="h-full overflow-y-auto">
              <div className="p-6">
                <div className="max-w-4xl mx-auto">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-base text-foreground">Recent Conversations</h3>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={startNewChat}
                      className="gap-2 h-9 text-xs font-bold rounded-lg border-border hover:bg-muted"
                    >
                      <Plus className="h-3 w-3" />
                      New Chat
                    </Button>
                  </div>
                  
                  {loadingHistory ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                  ) : chatHistoryData.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="h-8 w-8 mx-auto mb-3 opacity-50" />
                      <p className="text-sm font-medium">No conversations yet</p>
                      <p className="text-xs mt-1">Start chatting to see your history here</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 gap-3">
                      {chatHistoryData.map((session) => (
                        <div
                          key={session.session_id}
                          className={cn(
                            "group relative p-4 rounded-xl cursor-pointer transition-all duration-200 border bg-background/80 hover:shadow-md",
                            sessionId === session.session_id 
                              ? "border-primary/50 shadow-sm ring-2 ring-primary/20 bg-primary/5" 
                              : "border-border/60 hover:bg-muted/30 hover:border-border"
                          )}
                          onClick={() => loadChatSession(session.session_id)}
                        >
                          {/* Session Content */}
                          <div className="pr-8">
                            <div className="font-semibold text-sm text-foreground truncate mb-2">
                              {session.title || 'Untitled Chat'}
                            </div>
                            <div className="space-y-2 text-xs text-muted-foreground">
                              <div className="flex items-center gap-2">
                                <BookOpen className="h-3 w-3 flex-shrink-0" />
                                <span className="truncate">{session.knowledge_base_name}</span>
                              </div>
                              <div className="flex items-center justify-between">
                                <span className="flex items-center gap-1">
                                  <MessageSquare className="h-3 w-3" />
                                  {session.message_count} messages
                                </span>
                                <span>{new Date(session.created_at).toLocaleDateString()}</span>
                              </div>
                            </div>
                          </div>

                          {/* Delete Button */}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => deleteChatSession(session.session_id, e)}
                            className="absolute top-3 right-3 h-7 w-7 p-0 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 opacity-60 group-hover:opacity-100 transition-all"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
