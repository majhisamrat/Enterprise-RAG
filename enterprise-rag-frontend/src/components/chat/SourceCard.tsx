import { SourceDocument } from '../../types/chat';

export function SourceCard({ source }: { source: SourceDocument }) {
  return (
    <div className="source-card">
      <b>
        📄 {source.title} {source.pageNumber && `(Page ${source.pageNumber})`}
      </b>
      <span>Score: {(source.score * 100).toFixed(0)}% match</span>
      <p>{source.snippet}</p>
    </div>
  );
}
