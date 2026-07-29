import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { useKnowledgeBases } from '@/hooks/useKnowledge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { PageHeader } from '@/components/shared/PageHeader';
import { EmptyState } from '@/components/shared/EmptyState';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Send, Brain, User, Loader2, BookOpen, MessageSquare } from 'lucide-react';
import type { ChatMessageDisplay, ChatSource } from '@/types/chat';

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

  const handleSend = async () => {
    const query = input.trim();
    if (!query || chatMutation.isPending) return;

    const userMsg: ChatMessageDisplay = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');

    try {
      const res = await chatMutation.mutateAsync({
        query,
        session_id: sessionId || undefined,
        knowledge_base_id: selectedKb || undefined,
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
      // Error is handled by the API interceptor
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <PageHeader title="Chat" description="Ask questions about your documents">
        <Select value={selectedKb} onValueChange={setSelectedKb}>
          <SelectTrigger className="w-[220px]">
            <SelectValue placeholder="All Knowledge Bases" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Knowledge Bases</SelectItem>
            {kbs?.map((kb) => (
              <SelectItem key={kb.id} value={kb.id}>{kb.display_name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {sessionId && (
          <Button variant="ghost" size="sm" onClick={() => { setMessages([]); setSessionId(null); }}>
            New Chat
          </Button>
        )}
      </PageHeader>

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 ? (
          <EmptyState
            title="Start a conversation"
            description="Ask questions about your uploaded documents. You can filter by a specific knowledge base."
            className="py-16"
          />
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className="animate-fade-in">
              <div className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <Avatar className="h-8 w-8 mt-1">
                    <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                      <Brain className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
                <div className={`max-w-[75%] ${msg.role === 'user' ? 'order-first' : ''}`}>
                  <Card className={`p-4 ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card'}`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </Card>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <BookOpen className="h-3 w-3" />
                        Sources ({msg.sources.length})
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {msg.sources.slice(0, 5).map((src, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {src.citation_key} &mdash; {src.document_name || src.title}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {msg.metadata && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {msg.metadata.total_tokens} tokens &middot; {msg.metadata.latency_ms.toFixed(0)}ms
                      {msg.metadata.kb_filtered && ' &middot; KB filtered'}
                    </p>
                  )}
                </div>
                {msg.role === 'user' && (
                  <Avatar className="h-8 w-8 mt-1">
                    <AvatarFallback className="bg-secondary text-secondary-foreground text-xs">
                      <User className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t bg-card p-4 rounded-lg">
        <div className="flex gap-3">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={selectedKb ? `Ask about ${kbs?.find((k) => k.id === selectedKb)?.display_name}...` : 'Ask about your documents...'}
            className="min-h-[44px] max-h-[120px] resize-none"
            rows={1}
          />
          <Button onClick={handleSend} disabled={!input.trim() || chatMutation.isPending} className="shrink-0 self-end">
            {chatMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
