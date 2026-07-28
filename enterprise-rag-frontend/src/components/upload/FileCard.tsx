import { DocumentItem } from '../../types/document';

interface FileCardProps {
  document: DocumentItem;
  onDelete?: (id: string) => void;
}

export function FileCard({ document, onDelete }: FileCardProps) {
  return (
    <div className="file-card">
      <div className="doc-chip-icon">📄</div>
      <div style={{ flex: 1 }}>
        <strong>{document.name}</strong>
        <small>
          {document.size} • {document.pageCount} pages • {document.chunkCount} chunks • {document.status}
        </small>
      </div>
      {onDelete && (
        <button
          onClick={() => onDelete(document.id)}
          style={{ border: 0, background: 'transparent', color: 'var(--danger)', cursor: 'pointer', fontSize: '16px' }}
          title="Delete Document"
        >
          🗑️
        </button>
      )}
    </div>
  );
}
