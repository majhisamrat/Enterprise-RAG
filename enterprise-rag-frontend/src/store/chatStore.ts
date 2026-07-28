import { create } from 'zustand';
import { ChatMessage, ChatSession } from '../types/chat';

interface ChatStore {
  sessions: ChatSession[];
  activeSessionId: string | null;
  attachedDoc: { name: string; size?: string } | null;
  isGenerating: boolean;
  setAttachedDoc: (doc: { name: string; size?: string } | null) => void;
  createSession: () => string;
  setActiveSession: (id: string) => void;
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  deleteSession: (id: string) => void;
  renameSession: (id: string, newTitle: string) => void;
  clearActiveChat: () => void;
  setIsGenerating: (generating: boolean) => void;
}

const initialSessions: ChatSession[] = [
  {
    id: 's1',
    title: 'Chatbot Definition & Overview',
    group: 'TODAY',
    timestamp: 'Just now',
    messages: [
      {
        id: 'm1',
        sender: 'user',
        content: 'I uploaded the project update document.',
        timestamp: '12:00 pm',
        attachedDoc: { name: 'Marketing.pdf', size: '2.4 MB' },
      },
      {
        id: 'm2',
        sender: 'assistant',
        content: `Of course! I have extracted the relevant details from **Marketing.pdf**.

**The Latest Project Updates Include:**
- Project milestones achieved across Q3 engineering goals
- Team collaboration metrics and sprint velocity
- Key performance indicators (KPIs) for multi-channel engagement
- System search accuracy improvement of +34% using hybrid reranking

Is there anything specific you'd like more details on?`,
        timestamp: '12:00 pm',
        sources: [
          { id: 'doc-1', title: 'Marketing.pdf', score: 0.94, snippet: 'Q3 engineering goals and sprint velocity metrics...', pageNumber: 4 },
        ],
        tokensUsed: 342,
        latencyMs: 180,
      },
    ],
  },
  {
    id: 's2',
    title: 'UI/UX Design Service Docs',
    group: 'TODAY',
    timestamp: '1 hour ago',
    messages: [],
  },
  {
    id: 's3',
    title: 'How to use ChatGPT & RAG',
    group: 'TODAY',
    timestamp: '3 hours ago',
    messages: [],
  },
  {
    id: 's4',
    title: 'Architecture & Vector DBs',
    group: 'YESTERDAY',
    timestamp: 'Yesterday',
    messages: [],
  },
];

export const useChatStore = create<ChatStore>((set, get) => ({
  sessions: initialSessions,
  activeSessionId: 's1',
  attachedDoc: null,
  isGenerating: false,

  setAttachedDoc: (doc) => set({ attachedDoc: doc }),

  createSession: () => {
    const newId = 'session-' + Date.now();
    const newSession: ChatSession = {
      id: newId,
      title: 'New Chatbot Session',
      group: 'TODAY',
      timestamp: 'Just now',
      messages: [],
    };
    set((state) => ({
      sessions: [newSession, ...state.sessions],
      activeSessionId: newId,
    }));
    return newId;
  },

  setActiveSession: (id) => set({ activeSessionId: id }),

  addMessage: (message) => {
    set((state) => {
      const activeId = state.activeSessionId;
      if (!activeId) return state;
      return {
        sessions: state.sessions.map((s) => {
          if (s.id === activeId) {
            return {
              ...s,
              messages: [...s.messages, message],
              title: s.messages.length === 0 ? message.content.slice(0, 28) + '...' : s.title,
            };
          }
          return s;
        }),
      };
    });
  },

  updateMessage: (messageId, updates) => {
    set((state) => ({
      sessions: state.sessions.map((s) => ({
        ...s,
        messages: s.messages.map((m) => (m.id === messageId ? { ...m, ...updates } : m)),
      })),
    }));
  },

  deleteSession: (id) => {
    set((state) => {
      const filtered = state.sessions.filter((s) => s.id !== id);
      return {
        sessions: filtered,
        activeSessionId: state.activeSessionId === id ? (filtered[0]?.id || null) : state.activeSessionId,
      };
    });
  },

  renameSession: (id, newTitle) => {
    set((state) => ({
      sessions: state.sessions.map((s) => (s.id === id ? { ...s, title: newTitle } : s)),
    }));
  },

  clearActiveChat: () => {
    const activeId = get().activeSessionId;
    if (!activeId) return;
    set((state) => ({
      sessions: state.sessions.map((s) => (s.id === activeId ? { ...s, messages: [] } : s)),
    }));
  },

  setIsGenerating: (generating) => set({ isGenerating: generating }),
}));
