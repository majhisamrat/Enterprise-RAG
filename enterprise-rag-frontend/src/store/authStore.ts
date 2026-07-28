import { create } from 'zustand';
type AuthState = { token: string | null; setToken: (token: string) => void; logout: () => void };
export const useAuthStore = create<AuthState>((set) => ({ token: localStorage.getItem('enterprise_rag_token'), setToken: (token) => { localStorage.setItem('enterprise_rag_token', token); set({ token }); }, logout: () => { localStorage.removeItem('enterprise_rag_token'); set({ token: null }); } }));
