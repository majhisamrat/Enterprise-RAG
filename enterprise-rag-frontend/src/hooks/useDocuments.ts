import { useDocumentStore } from '../store/documentStore';

export function useDocuments() {
  const { documents, loading, addDocument, removeDocument } = useDocumentStore();

  return {
    documents,
    loading,
    addDocument,
    removeDocument,
  };
}
