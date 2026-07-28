import { Link } from 'react-router-dom';
import { DocumentItem } from '../../types/document';

export function RecentDocuments({ documents }: { documents: DocumentItem[] }) {
  return (
    <div className="card">
      <div className="card-heading">
        <h3>Recent documents</h3>
        <Link to="/documents">View all</Link>
      </div>

      {documents.slice(0, 5).map((doc) => (
        <div key={doc.id} className="row">
          <span style={{ fontSize: '14px' }}>📄</span>
          <span>
            <strong>{doc.name}</strong>
            <small style={{ background: 'transparent', padding: 0, color: 'var(--muted)', fontWeight: 400 }}>
              {doc.size} • {doc.chunkCount} chunks
            </small>
          </span>
          <small>{doc.status}</small>
        </div>
      ))}
    </div>
  );
}
