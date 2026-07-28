import { useUpload } from '../hooks/useUpload';
import { useDocuments } from '../hooks/useDocuments';
import { UploadBox } from '../components/upload/UploadBox';
import { UploadProgress } from '../components/upload/UploadProgress';
import { FileCard } from '../components/upload/FileCard';

export function Upload() {
  const { uploadFile, uploading, progress } = useUpload();
  const { documents } = useDocuments();

  return (
    <div className="upload-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">INGESTION PIPELINE</p>
          <h2>Upload Documents</h2>
          <p>Drag and drop PDF, DOCX, PPTX, XLSX, Markdown, or CSV files to index into Qdrant vector storage.</p>
        </div>
      </div>

      <UploadBox onFileSelect={uploadFile} title="Upload Documents to Enterprise RAG" />

      {uploading && <UploadProgress progress={progress} filename="Uploading file" />}

      <div style={{ marginTop: '30px' }}>
        <h3 style={{ fontSize: '16px', letterSpacing: '-0.03em', marginBottom: '14px' }}>Indexed Documents ({documents.length})</h3>
        <div className="upload-list">
          {documents.map((doc) => (
            <FileCard key={doc.id} document={doc} />
          ))}
        </div>
      </div>
    </div>
  );
}
