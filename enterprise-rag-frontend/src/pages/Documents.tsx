import { useDocuments } from '../hooks/useDocuments';

export function Documents() {
  const { documents, removeDocument } = useDocuments();

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="eyebrow">MANAGEMENT</p>
          <h2>Knowledge Base Documents</h2>
          <p>View, inspect chunk status, re-index, or delete document vectors from your enterprise store.</p>
        </div>
      </div>

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>DOCUMENT NAME</th>
              <th>TYPE</th>
              <th>PAGES</th>
              <th>CHUNKS</th>
              <th>STATUS</th>
              <th>UPLOADED</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td>
                  <strong>📄 {doc.name}</strong>
                  <small>{doc.size}</small>
                </td>
                <td>{doc.type.toUpperCase()}</td>
                <td>{doc.pageCount}</td>
                <td>{doc.chunkCount}</td>
                <td>
                  <span className="badge success">{doc.status}</span>
                </td>
                <td>{doc.uploadedAt}</td>
                <td>
                  <button
                    className="table-action"
                    onClick={() => alert(`Re-indexing ${doc.name}...`)}
                    title="Re-index document"
                  >
                    🔄
                  </button>
                  <button
                    className="table-action danger"
                    onClick={() => removeDocument(doc.id)}
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
