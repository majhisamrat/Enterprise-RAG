import { Loader } from '../common/Loader';

export function TypingIndicator() {
  return (
    <div className="msg-row assistant">
      <div className="ai-response-card" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className="ai-hexagon-icon">⬡</div>
        <span style={{ fontSize: '13px', color: 'var(--muted)', fontWeight: 600 }}>Rag is processing context</span>
        <Loader />
      </div>
    </div>
  );
}
