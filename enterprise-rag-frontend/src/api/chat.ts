import { api } from './axios'; import type { ChatResponse } from '../types/chat';
export const askChat = async (query: string, sessionId?: string, topK = 5) => (await api.post<ChatResponse>('/chat/', { query, session_id: sessionId, top_k: topK })).data;
