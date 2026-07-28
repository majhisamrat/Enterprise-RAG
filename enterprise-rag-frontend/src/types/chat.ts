export interface SourceDocument {
  id: string;
  title: string;
  score: number;
  snippet: string;
  pageNumber?: number;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  attachedDoc?: {
    name: string;
    size?: string;
  };
  sources?: SourceDocument[];
  tokensUsed?: number;
  latencyMs?: number;
  liked?: boolean;
  disliked?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  group: 'TODAY' | 'YESTERDAY' | 'PREVIOUS_7_DAYS' | 'OLDER';
  timestamp: string;
  messages: ChatMessage[];
}

export interface ChatResponse {
  answer: string;
  sources: SourceDocument[];
  tokens_used?: number;
  latency_ms?: number;
}
