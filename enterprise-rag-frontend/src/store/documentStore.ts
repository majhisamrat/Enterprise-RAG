import { create } from 'zustand';
import { DocumentItem } from '../types/document';

interface DocumentStore {
  documents: DocumentItem[];
  loading: boolean;
  addDocument: (doc: DocumentItem) => void;
  removeDocument: (id: string) => void;
  setDocuments: (docs: DocumentItem[]) => void;
}

const initialDocuments: DocumentItem[] = [
  {
    id: 'doc-1',
    name: 'Marketing.pdf',
    size: '2.4 MB',
    type: 'pdf',
    pageCount: 12,
    chunkCount: 48,
    status: 'indexed',
    uploadedAt: '12:00 pm today',
    ocrEnabled: true,
  },
  {
    id: 'doc-2',
    name: 'Enterprise_Architecture_Overview.pdf',
    size: '4.1 MB',
    type: 'pdf',
    pageCount: 28,
    chunkCount: 112,
    status: 'indexed',
    uploadedAt: 'Yesterday',
    ocrEnabled: false,
  },
  {
    id: 'doc-3',
    name: 'Q3_Financial_Analysis.xlsx',
    size: '1.8 MB',
    type: 'xlsx',
    pageCount: 5,
    chunkCount: 35,
    status: 'indexed',
    uploadedAt: '3 days ago',
    ocrEnabled: false,
  },
  {
    id: 'doc-4',
    name: 'Samrat_work_2026.pdf',
    size: '3.2 MB',
    type: 'pdf',
    pageCount: 14,
    chunkCount: 56,
    status: 'indexed',
    uploadedAt: 'Just now',
    ocrEnabled: true,
  },
];

export const useDocumentStore = create<DocumentStore>((set) => ({
  documents: initialDocuments,
  loading: false,
  addDocument: (doc) => set((state) => ({ documents: [doc, ...state.documents] })),
  removeDocument: (id) => set((state) => ({ documents: state.documents.filter((d) => d.id !== id) })),
  setDocuments: (docs) => set({ documents: docs }),
}));
