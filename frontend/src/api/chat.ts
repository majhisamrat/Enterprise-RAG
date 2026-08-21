import { apiClient } from '@/lib/api-client';
import type { ChatRequest, ChatResponse } from '@/types/chat';

export interface KBRequirement {
  kb_count: number;
  require_kb_selection: boolean;
  message: string;
  kbs: Array<{
    id: string;
    name: string;
    display_name: string;
    description?: string;
  }>;
}

export const chatApi = {
  send: (data: ChatRequest) =>
    apiClient.post<ChatResponse>('/chat', data).then((r) => r.data),

  getKbRequirements: () =>
    apiClient.get<KBRequirement>('/chat/kb-requirements').then((r) => r.data),
};
