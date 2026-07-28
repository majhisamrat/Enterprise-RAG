import { api } from './axios'; import type { DocumentItem } from '../types/document';
export const getDocuments = async () => (await api.get<DocumentItem[]>('/documents/')).data;
export const deleteDocument = async (id: string) => api.delete(`/documents/${id}`);
export const reindexDocument = async (id: string) => (await api.post(`/documents/${id}/reindex`)).data;
