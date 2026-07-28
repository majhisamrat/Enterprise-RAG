import { ChangeEvent, DragEvent, useState } from 'react';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  title?: string;
  subtitle?: string;
}

export function UploadBox({
  onFileSelect,
  title = 'Please Upload the Documents Before you ask Rag',
  subtitle = 'Drag and Drop Or Browse File To Upload Document',
}: UploadBoxProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="chat-empty-upload-state">
      <h2>{title}</h2>

      <div
        className={`upload-drop-zone ${isDragOver ? 'drag-active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload-input')?.click()}
      >
        <div className="upload-circle-icon">↑</div>
        <p style={{ margin: 0, fontSize: '15px', color: '#334842', fontWeight: 600 }}>
          Drag and Drop Or
        </p>
        <span style={{ color: 'var(--cyan)', fontWeight: 700, fontSize: '14px', textDecoration: 'underline' }}>
          Browse File
        </span>
        <span style={{ fontSize: '13px', color: 'var(--muted)' }}>To Upload Document</span>

        <input
          id="file-upload-input"
          type="file"
          accept=".pdf,.docx,.pptx,.xlsx,.txt,.md,.csv"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  );
}
