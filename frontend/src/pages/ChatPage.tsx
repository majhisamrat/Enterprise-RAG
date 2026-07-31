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
import { Send, Brain, User, Loader2, BookOpen, Plus, ArrowUpRight, Sparkles, MessageSquare } from 'lucide-react';
import type { ChatMessageDisplay } from '@/types/chat';
import { FadeIn } from '@/components/shared/motion';

const promptSuggestions = [
  'Summarize the key takeaways from the latest uploaded reports',
  'What are the compliance requirements outlined in the documents?',
  'Extract financial metrics and revenue figures from Q1 reports',
  'List all action items mentioned in meeting transcripts',
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageDisplay[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedKb, setSelectedKb] = useState<string>('');
  const chatMutation = useChat();
  const { data: kbs } = useKnowledgeBases();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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


      if (res.session_id && !sessionId) {
        setSessionId(res.session_id);
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
    <div className="flex-1 flex flex-col items-center justify-center py-2 h-[calc(100vh-7rem)] w-full">
      {/* ─── FLOATING CARD-STYLE CHAT CONTAINER ─── */}
      <div className="w-full max-w-5xl h-full flex flex-col bg-card/90 backdrop-blur-2xl border border-border/80 rounded-3xl shadow-2xl overflow-hidden relative glow-sm">
        
        {/* Floating Card Header Bar */}
        <div className="px-7 py-4.5 border-b border-border/70 bg-muted/30 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3.5">
            <div className="relative flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-primary via-blue-600 to-indigo-600 shadow-md shadow-primary/20">
              <Brain className="h-6 w-6 text-white" />
              <Sparkles className="absolute -top-1 -right-1 h-4 w-4 text-sky-300 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h2 className="font-black text-lg tracking-tight text-foreground">
                  Chat Assistant
                </h2>
                <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              </div>
              <p className="text-xs text-muted-foreground font-bold">
                Enterprise RAG Reranker Active
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Knowledge Base Filter */}
            <Select value={selectedKb} onValueChange={setSelectedKb}>
              <SelectTrigger className="w-[210px] sm:w-[250px] h-11 text-xs font-extrabold rounded-xl bg-background/80 border-border">
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
                onClick={() => { setMessages([]); setSessionId(null); }}
                className="gap-2 h-11 text-xs font-bold rounded-xl border-border hover:bg-muted px-4"
              >
                <Plus className="h-4 w-4" />
                New Chat
              </Button>
            )}
          </div>
        </div>

        {/* Floating Card Body / Message Stream Area */}
        <div className="flex-1 overflow-y-auto p-7 space-y-7">
          {messages.length === 0 ? (
            <FadeIn className="h-full flex flex-col justify-center items-center py-8 space-y-8 text-center max-w-2xl mx-auto">
              <div className="p-5 rounded-3xl bg-primary/10 border border-primary/20 shadow-lg glow-sm">
                <MessageSquare className="h-11 w-11 text-primary" />
              </div>
              <div>
                <h3 className="text-3xl font-black tracking-tight text-foreground">
                  Ask Your Knowledge Base
                </h3>
                <p className="text-base font-semibold text-muted-foreground mt-3 max-w-lg leading-relaxed">
                  Query documents, extract key insights, and synthesize answers using hybrid vector search & reranking.
                </p>
              </div>

              {/* Prompt Suggestions */}
              <div className="w-full space-y-4 pt-2">
                <p className="text-xs font-extrabold uppercase tracking-wider text-muted-foreground">
                  Suggested Prompts
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {promptSuggestions.map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(suggestion)}
                      className="p-4 text-left rounded-2xl border border-border/80 bg-background/60 hover:bg-muted hover:border-primary/40 transition-all duration-200 text-sm font-semibold text-muted-foreground hover:text-foreground group flex items-start justify-between gap-3 shadow-sm"
                    >
                      <span className="leading-relaxed">{suggestion}</span>
                      <ArrowUpRight className="h-4 w-4 shrink-0 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  ))}
                </div>
              </div>
            </FadeIn>
          ) : (
            messages.map((msg) => (
              <FadeIn key={msg.id} direction="up" duration={0.3} className="space-y-3.5">
                <div className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <Avatar className="h-10 w-10 mt-1 shrink-0 shadow-md shadow-primary/20">
                      <AvatarFallback className="bg-gradient-to-br from-primary via-blue-600 to-indigo-600 text-white font-bold text-sm">
                        <Brain className="h-5 w-5" />
                      </AvatarFallback>
                    </Avatar>
                  )}

                  <div className={`max-w-[85%] space-y-3 ${msg.role === 'user' ? 'order-first' : ''}`}>
                    {/* Larger Text Message Card */}
                    <Card
                      className={`p-6 rounded-2xl text-base sm:text-lg leading-relaxed font-semibold ${
                        msg.role === 'user'
                          ? 'bg-primary text-primary-foreground border-transparent shadow-md shadow-primary/25'
                          : 'bg-background/90 text-foreground border border-border/80 shadow-sm'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </Card>

                    {/* Referenced Sources Section */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="p-4 rounded-2xl bg-muted/40 border border-border/60 space-y-2.5 text-xs">
                        <p className="text-muted-foreground font-extrabold flex items-center gap-2 text-xs uppercase tracking-wider">
                          <BookOpen className="h-4 w-4 text-primary" />
                          Referenced Sources ({msg.sources.length})
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {msg.sources.slice(0, 6).map((src, i) => (
                            <Badge key={i} variant="outline" className="text-xs font-bold py-1 px-3 gap-1.5 bg-card/80 border-border">
                              <span className="font-mono font-black text-primary text-xs">{src.citation_key}</span>
                              <span>&mdash;</span>
                              <span className="truncate max-w-[220px]">{src.document_name || src.title}</span>
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Token & Latency Metadata Row */}
                    {msg.metadata && (
                      <p className="text-xs text-muted-foreground font-mono px-1 font-bold">
                        {msg.metadata.total_tokens} tokens &middot; {msg.metadata.latency_ms.toFixed(0)}ms
                        {msg.metadata.kb_filtered && ' &middot; KB filtered'}
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
            <FadeIn className="flex items-center gap-3.5">
              <Avatar className="h-10 w-10 shadow-md shadow-primary/20">
                <AvatarFallback className="bg-gradient-to-br from-primary via-blue-600 to-indigo-600 text-white">
                  <Brain className="h-5 w-5 animate-spin-slow" />
                </AvatarFallback>
              </Avatar>
              <Card className="p-4.5 rounded-2xl bg-background/90 border border-border flex items-center gap-3 text-sm font-bold text-muted-foreground">
                <Loader2 className="h-4.5 w-4.5 text-primary animate-spin" />
                <span className="animate-pulse">Retrieving document chunks & synthesizing answer...</span>
              </Card>
            </FadeIn>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating Input Dock at Bottom of Floating Card */}
        <div className="p-5 border-t border-border/70 bg-muted/20 shrink-0">
          <div className="relative rounded-2xl border border-border/80 bg-background/90 shadow-lg p-3 focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20 transition-all">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                selectedKb && selectedKb !== 'all'
                  ? `Ask about ${kbs?.find((k) => k.id === selectedKb)?.display_name}...`
                  : 'Ask anything across your knowledge bases...'
              }
              className="min-h-[60px] max-h-[140px] border-0 bg-transparent shadow-none focus-visible:ring-0 focus-visible:bg-transparent resize-none py-2 px-3 text-base sm:text-lg font-semibold placeholder:text-muted-foreground/60"
              rows={1}
            />

            <div className="flex items-center justify-between px-2 pt-2 border-t border-border/40">
              <span className="text-xs text-muted-foreground font-semibold">
                Press <kbd className="px-2 py-0.5 rounded bg-muted font-mono text-xs font-bold">Enter</kbd> to send, <kbd className="px-2 py-0.5 rounded bg-muted font-mono text-xs font-bold">Shift+Enter</kbd> for line break
              </span>

              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || chatMutation.isPending}
                size="default"
                className="gap-2 shadow-lg shadow-primary/25 px-6 h-11 font-black text-sm rounded-xl"
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
  );
}
