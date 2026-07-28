export interface DocumentItem {
  id: string;
  name: string;
  size: string;
  type: string;
  pageCount: number;
  chunkCount: number;
  status: 'indexed' | 'processing' | 'failed';
  uploadedAt: string;
  ocrEnabled?: boolean;
}

export interface UploadProgressItem {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface UploadResult {
  document_id: string;
  filename: string;
  chunk_count: number;
  status: string;
}
