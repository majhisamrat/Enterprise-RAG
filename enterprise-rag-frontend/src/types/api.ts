export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string;
}

export interface SystemHealth {
  status: string;
  version: string;
  redis: boolean;
  vectorstore: boolean;
  embedding_model: string;
  reranker_enabled: boolean;
}

export type HealthResponse = SystemHealth;
