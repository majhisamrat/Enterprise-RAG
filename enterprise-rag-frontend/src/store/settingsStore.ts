import { create } from 'zustand';
import { SettingsState } from '../types/settings';

interface SettingsStore {
  settings: SettingsState;
  updateSettings: (updates: Partial<SettingsState>) => void;
}

export const useSettingsStore = create<SettingsStore>((set) => ({
  settings: {
    llmProvider: 'groq',
    modelName: 'llama-3.3-70b-versatile',
    embeddingModel: 'BAAI/bge-small-en-v1.5',
    chunkSize: 512,
    chunkOverlap: 64,
    topK: 5,
    temperature: 0.2,
    maxTokens: 2048,
    enableReranker: true,
    theme: 'light',
  },
  updateSettings: (updates) =>
    set((state) => ({
      settings: { ...state.settings, ...updates },
    })),
}));
