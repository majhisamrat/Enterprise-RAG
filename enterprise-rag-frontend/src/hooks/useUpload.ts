import { useState } from 'react';
import { useDocumentStore } from '../store/documentStore';
import { useChatStore } from '../store/chatStore';

export function useUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const addDocument = useDocumentStore((s) => s.addDocument);
  const setAttachedDoc = useChatStore((s) => s.setAttachedDoc);

  const uploadFile = async (file: File) => {
    setUploading(true);
    setProgress(20);

    const interval = setInterval(() => {
      setProgress((p) => {
        if (p >= 90) {
          clearInterval(interval);
          return 90;
        }
        return p + 25;
      });
    }, 200);

    setTimeout(() => {
      clearInterval(interval);
      setProgress(100);
      setUploading(false);

      const newDoc = {
        id: 'doc-' + Date.now(),
        name: file.name,
        size: (file.size / (1024 * 1024)).toFixed(1) + ' MB',
        type: file.name.split('.').pop() || 'file',
        pageCount: Math.floor(Math.random() * 15) + 1,
        chunkCount: Math.floor(Math.random() * 60) + 12,
        status: 'indexed' as const,
        uploadedAt: 'Just now',
        ocrEnabled: true,
      };

      addDocument(newDoc);
      setAttachedDoc({ name: file.name, size: newDoc.size });
    }, 1000);
  };

  return { uploadFile, uploading, progress };
}
