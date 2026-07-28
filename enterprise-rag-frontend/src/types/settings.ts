export interface SettingsState {
  llmProvider: 'groq' | 'cerebras' | 'gemini' | 'openai';
  modelName: string;
  embeddingModel: string;
  chunkSize: number;
  chunkOverlap: number;
  topK: number;
  temperature: number;
  maxTokens: number;
  enableReranker: boolean;
  theme: 'light' | 'dark';
}
