import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { useKnowledgeBases } from '@/hooks/useKnowledge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowUpRight, BookOpen, Brain, ChevronLeft, ChevronsLeft, ChevronsRight, FileText, Loader2, MessageSquare, PanelLeftOpen, Plus, Send, Sparkles, Trash2, User } from 'lucide-react';
import type { ChatMessageDisplay } from '@/types/chat';
import { FadeIn } from '@/components/shared/motion';
import { cn } from '@/lib/utils';

const promptSuggestions = [
  { title: 'Summarize a report', text: 'Summarize the key takeaways from the latest uploaded reports', icon: FileText },
  { title: 'Find action items', text: 'List all action items mentioned in meeting transcripts', icon: MessageSquare },
  { title: 'Analyze metrics', text: 'Extract financial metrics and revenue figures from Q1 reports', icon: Sparkles },
  { title: 'Review compliance', text: 'What are the compliance requirements outlined in the documents?', icon: BookOpen },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageDisplay[]>([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedKb, setSelectedKb] = useState('all');
  const [chatHistoryData, setChatHistoryData] = useState<any[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [currentSessionTitle, setCurrentSessionTitle] = useState('');
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [desktopHistoryCollapsed, setDesktopHistoryCollapsed] = useState(false);
  const chatMutation = useChat();
  const { data: kbs } = useKnowledgeBases();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);
  useEffect(() => { void fetchChatHistory(); }, []);

  const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('access_token');
    if (token && token !== 'null' && token !== 'undefined') headers.Authorization = `Bearer ${token}`;
    return headers;
  };
  async function fetchChatHistory() {
    setLoadingHistory(true);
    try { const response = await fetch('/api/v1/chat/history', { headers: getAuthHeaders() }); if (response.ok) { const data = await response.json(); setChatHistoryData(data.sessions || []); } } catch (error) { console.error('Error fetching chat history:', error); } finally { setLoadingHistory(false); }
  }
  async function loadChatSession(id: string) {
    if (id === sessionId) return;
    setLoadingSession(true);
    try {
      const response = await fetch(`/api/v1/chat/history/${id}`, { headers: getAuthHeaders() });
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages.map((msg: any) => ({ id: msg.id, role: msg.sender_role, content: msg.content, sources: msg.sources, timestamp: new Date(msg.created_at) })));
        setSessionId(id); setCurrentSessionTitle(data.session.title || 'Untitled chat'); setSelectedKb(data.session.knowledge_base_id || 'all'); setHistoryExpanded(false);
      }
    } catch (error) { console.error('Error loading chat session:', error); } finally { setLoadingSession(false); }
  }
  async function deleteChatSession(id: string, event: React.MouseEvent) {
    event.stopPropagation();
    if (!confirm('Delete this chat session? This action cannot be undone.')) return;
    try { const response = await fetch(`/api/v1/chat/history/${id}`, { method: 'DELETE', headers: getAuthHeaders() }); if (response.ok) { await fetchChatHistory(); if (sessionId === id) startNewChat(); } } catch (error) { console.error('Error deleting chat session:', error); }
  }
  function startNewChat() { setMessages([]); setSessionId(null); setCurrentSessionTitle(''); setSelectedKb('all'); setHistoryExpanded(false); }
  async function handleSend(customQuery?: string) {
    const query = (customQuery || input).trim(); if (!query || chatMutation.isPending) return;
    setMessages(prev => [...prev, { id: `user-${Date.now()}`, role: 'user', content: query, timestamp: new Date() }]); if (!customQuery) setInput('');
    try {
      const res = await chatMutation.mutateAsync({ query, session_id: sessionId || undefined, knowledge_base_id: selectedKb !== 'all' ? selectedKb : undefined, top_k: 10 });
      if (res.session_id) { setSessionId(res.session_id); if (!currentSessionTitle) setCurrentSessionTitle(`${query.slice(0, 50)}${query.length > 50 ? '...' : ''}`); }
      setMessages(prev => [...prev, { id: `assistant-${Date.now()}`, role: 'assistant', content: res.answer, sources: res.sources, metadata: res.metadata, timestamp: new Date() }]); setTimeout(fetchChatHistory, 300);
    } catch { /* API interceptor handles the error */ }
  }
  function handleKeyDown(event: React.KeyboardEvent) { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void handleSend(); } }

  const historyRail = <aside className="flex h-full w-full shrink-0 flex-col border-r border-sky-100 bg-white/75 backdrop-blur-xl lg:w-72">
    <div className="border-b border-sky-100 p-5"><div className="flex items-center justify-between"><div><p className="app-kicker">Workspace</p><h2 className="mt-1 text-lg font-black text-[#082c67]">Conversations</h2></div><Button onClick={startNewChat} size="sm" className="h-10 rounded-xl bg-[#1246a7] px-3 text-sm hover:bg-[#0d398a]"><Plus className="mr-1 h-4 w-4" />New</Button></div></div>
    <div className="flex-1 overflow-y-auto p-3">
      <p className="px-2 pb-2 pt-1 text-xs font-black uppercase tracking-[.14em] text-[#7190b7]">Recent</p>
      {loadingHistory ? <div className="grid place-items-center py-10"><Loader2 className="h-5 w-5 animate-spin text-[#1f61b9]" /></div> : chatHistoryData.length === 0 ? <div className="px-3 py-8 text-center"><MessageSquare className="mx-auto h-7 w-7 text-sky-200" /><p className="mt-3 text-sm font-semibold text-[#7287a5]">Your conversations will appear here.</p></div> : <div className="space-y-2">{chatHistoryData.map(session => <button key={session.session_id} onClick={() => void loadChatSession(session.session_id)} className={cn('group relative w-full rounded-xl border p-3.5 pr-8 text-left transition', sessionId === session.session_id ? 'border-sky-200 bg-sky-50 shadow-sm' : 'border-transparent hover:border-sky-100 hover:bg-white')}><p className="truncate text-sm font-bold text-[#173a72]">{session.title || 'Untitled chat'}</p><div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-[#7790af]"><BookOpen className="h-3.5 w-3.5" /><span className="truncate">{session.knowledge_base_name || 'All knowledge'}</span></div><div className="mt-1.5 flex justify-between text-xs text-[#91a4bd]"><span>{session.message_count} messages</span><span>{new Date(session.created_at).toLocaleDateString()}</span></div><span onClick={event => void deleteChatSession(session.session_id, event)} className="absolute right-2 top-2 grid h-7 w-7 cursor-pointer place-items-center rounded-md text-rose-400 opacity-0 transition hover:bg-rose-50 group-hover:opacity-100"><Trash2 className="h-3.5 w-3.5" /></span></button>)}</div>}
    </div>
    <div className="m-3 rounded-xl bg-[#edf7ff] p-3"><p className="text-xs font-bold text-[#2865a9]">Grounded answers</p><p className="mt-1 text-xs leading-5 text-[#6483a9]">Atlas cites the knowledge behind every response.</p></div>
  </aside>;

  return <div className="chat-workspace app-aurora relative -m-5 flex min-h-[calc(100vh-4rem)] overflow-hidden bg-[radial-gradient(circle_at_16%_14%,rgba(255,174,68,.72),transparent_23%),radial-gradient(circle_at_89%_10%,rgba(233,83,151,.70),transparent_28%),radial-gradient(circle_at_48%_94%,rgba(120,62,227,.58),transparent_45%),linear-gradient(135deg,#7563ed_0%,#b949c5_48%,#fc6a76_100%)] md:-m-8 md:min-h-[calc(100vh-5rem)] lg:-m-10 lg:min-h-screen">
    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_18%_82%,rgba(32,20,116,.36),transparent_34%),radial-gradient(circle_at_72%_35%,rgba(249,137,42,.38),transparent_22%)]" /><div className="pointer-events-none absolute inset-0 opacity-30 dot-grid-pattern" />
    <div className="relative z-10 mx-auto flex w-full max-w-[1720px] p-4 md:p-7 lg:p-10"><div className="flex min-h-[calc(100vh-5rem)] w-full overflow-hidden rounded-[1.75rem] border border-white bg-white/80 shadow-[0_30px_90px_-42px_rgba(10,55,116,.48)] backdrop-blur-xl md:min-h-[calc(100vh-8.5rem)]">
      <div className={cn('relative hidden shrink-0 transition-[width] duration-300 lg:block', desktopHistoryCollapsed ? 'w-0' : 'w-72')}>
        {!desktopHistoryCollapsed && historyRail}
        <button onClick={() => setDesktopHistoryCollapsed(!desktopHistoryCollapsed)} title={desktopHistoryCollapsed ? 'Show conversations' : 'Hide conversations'} className="absolute top-1/2 z-20 grid h-12 w-7 -translate-y-1/2 place-items-center rounded-r-2xl border border-l-0 border-sky-200 bg-gradient-to-b from-[#4eb7f7] to-[#0878d1] text-white shadow-lg shadow-blue-900/25 transition hover:w-9" style={{ left: desktopHistoryCollapsed ? 0 : '100%' }}>
          {desktopHistoryCollapsed ? <ChevronsRight className="h-5 w-5" /> : <ChevronsLeft className="h-5 w-5" />}
        </button>
      </div>
      <section className="flex min-w-0 flex-1 flex-col bg-[#fbfdff]/75">
        <header className="flex min-h-[76px] items-center justify-between border-b border-sky-100 bg-white/70 px-4 sm:px-6"><div className="flex min-w-0 items-center gap-3"><button onClick={() => setHistoryExpanded(true)} className="grid h-9 w-9 place-items-center rounded-xl border border-sky-100 text-[#1d5eae] lg:hidden"><PanelLeftOpen className="h-4 w-4" /></button><span className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-[#103d88] text-white shadow-md shadow-blue-900/15"><Brain className="h-5 w-5" /></span><div className="min-w-0"><div className="flex items-center gap-2"><h1 className="truncate text-sm font-black text-[#082c67]">{currentSessionTitle || 'Atlas Assistant'}</h1>{loadingSession && <Loader2 className="h-3.5 w-3.5 animate-spin text-[#1f61b9]" />}<span className="h-2 w-2 rounded-full bg-emerald-400" /></div><p className="text-[10px] font-bold uppercase tracking-[.12em] text-[#7590b4]">Source-grounded intelligence</p></div></div><Select value={selectedKb} onValueChange={setSelectedKb}><SelectTrigger className="h-10 w-[160px] rounded-xl border-sky-200 bg-white text-xs font-bold text-[#24518d] sm:w-[210px]"><SelectValue placeholder="All knowledge" /></SelectTrigger><SelectContent><SelectItem value="all">All Knowledge Bases</SelectItem>{kbs?.map(kb => <SelectItem key={kb.id} value={kb.id}>{kb.display_name}</SelectItem>)}</SelectContent></Select></header>
        <div className="flex min-h-0 flex-1 flex-col overflow-y-auto"><div className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 py-8 sm:px-8">{messages.length === 0 ? <FadeIn className="my-auto py-8"><div className="mx-auto max-w-2xl text-center"><span className="mx-auto grid h-16 w-16 place-items-center rounded-[1.3rem] bg-[#e0f2ff] text-[#1858aa] shadow-[0_12px_28px_-16px_rgba(20,84,173,.55)]"><MessageSquare className="h-7 w-7" /></span><p className="app-kicker mt-7">Atlas intelligence</p><h2 className="font-display mt-2 text-3xl font-black text-[#082c67] sm:text-4xl">What can we make clear today?</h2><p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-[#667e9f]">Ask across your company knowledge and get a precise answer with its supporting sources.</p><div className="mt-8 grid gap-3 text-left sm:grid-cols-2">{promptSuggestions.map(({ title, text, icon: Icon }) => <button key={title} onClick={() => void handleSend(text)} className="group rounded-2xl border border-sky-100 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-sky-300 hover:shadow-md"><span className="flex items-center justify-between"><Icon className="h-4 w-4 text-[#2465bd]" /><ArrowUpRight className="h-4 w-4 text-sky-300 transition group-hover:text-[#2465bd]" /></span><p className="mt-5 text-sm font-bold text-[#173a72]">{title}</p><p className="mt-1 line-clamp-2 text-xs leading-5 text-[#7187a6]">{text}</p></button>)}</div></div></FadeIn> : <div className="space-y-7">{messages.map(msg => <FadeIn key={msg.id} direction="up" duration={.25} className={cn('flex gap-3 sm:gap-4', msg.role === 'user' ? 'justify-end' : 'justify-start')}><Avatar className={cn('mt-1 h-9 w-9 shrink-0', msg.role === 'user' && 'order-2')}><AvatarFallback className={msg.role === 'user' ? 'bg-[#e7ddff] text-[#60439d]' : 'bg-[#103d88] text-white'}>{msg.role === 'user' ? <User className="h-4 w-4" /> : <Brain className="h-4 w-4" />}</AvatarFallback></Avatar><div className={cn('max-w-[87%] space-y-3 sm:max-w-[78%]', msg.role === 'user' && 'order-1')}><Card className={cn('rounded-2xl p-4 text-sm leading-7 shadow-sm', msg.role === 'user' ? 'border-[#1246a7] bg-[#1246a7] text-white' : 'border-sky-100 bg-white text-[#173a72]')}><p className="whitespace-pre-wrap">{msg.content}</p></Card>{msg.sources?.length ? <div className="rounded-xl border border-sky-100 bg-[#f2f9ff] p-3"><p className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-[.12em] text-[#3e71a9]"><BookOpen className="h-3.5 w-3.5" />Sources · {msg.sources.length}</p><div className="mt-2 flex flex-wrap gap-1.5">{msg.sources.slice(0, 5).map((src, index) => <Badge key={index} variant="outline" className="max-w-[220px] border-sky-200 bg-white py-1 text-[10px] font-semibold text-[#35649c]"><span className="truncate">{src.document_name || src.title}</span></Badge>)}</div></div> : null}{msg.metadata && <p className="px-1 text-[10px] font-medium text-[#859bb8]">{msg.metadata.total_tokens} tokens · {msg.metadata.latency_ms.toFixed(0)}ms {msg.metadata.kb_filtered ? '· Filtered' : ''}</p>}</div></FadeIn>)}{chatMutation.isPending && <div className="flex items-center gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-[#103d88] text-white"><Brain className="h-4 w-4 animate-spin-slow" /></span><span className="rounded-2xl border border-sky-100 bg-white px-4 py-3 text-xs font-semibold text-[#6881a2]"><Loader2 className="mr-2 inline h-3.5 w-3.5 animate-spin text-[#2465bd]" />Looking through your knowledge…</span></div>}<div ref={messagesEndRef} /></div>}</div></div>
        <footer className="border-t border-sky-100 bg-white/85 px-4 py-4 sm:px-8 sm:py-5"><div className="mx-auto max-w-5xl rounded-[1.3rem] border border-sky-200 bg-white p-3 shadow-[0_14px_30px_-22px_rgba(13,57,113,.45)] focus-within:border-[#4b86d9] focus-within:ring-4 focus-within:ring-sky-100"><Textarea value={input} onChange={event => setInput(event.target.value)} onKeyDown={handleKeyDown} placeholder={selectedKb !== 'all' ? `Ask about ${kbs?.find(k => k.id === selectedKb)?.display_name || 'this knowledge base'}...` : 'Ask anything across your knowledge bases…'} className="min-h-[52px] max-h-[130px] resize-none border-0 bg-transparent px-2 py-1.5 text-sm text-[#173a72] shadow-none placeholder:text-[#9aaac0] focus-visible:ring-0" rows={1} /><div className="flex items-center justify-between border-t border-sky-50 px-1 pt-2"><span className="text-[10px] font-medium text-[#8499b5]">Enter to send · Shift + Enter for a new line</span><Button onClick={() => void handleSend()} disabled={!input.trim() || chatMutation.isPending} size="sm" className="chat-send-button h-9 rounded-xl bg-[#c9fff2] px-4 text-xs text-[#0a5a51] shadow-md shadow-emerald-300/25 hover:bg-[#aef5e4] hover:text-[#06443d]">{chatMutation.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <><span>Send</span><Send className="ml-1.5 h-3.5 w-3.5" /></>}</Button></div></div></footer>
      </section>
      {historyExpanded && <div className="absolute inset-y-0 left-0 z-30 w-[min(19rem,88vw)] shadow-2xl lg:hidden"><button onClick={() => setHistoryExpanded(false)} className="absolute right-3 top-4 z-10 grid h-8 w-8 place-items-center rounded-lg bg-white text-[#1d5eae] shadow"><ChevronLeft className="h-4 w-4" /></button>{historyRail}</div>}
    </div></div>
  </div>;
}
