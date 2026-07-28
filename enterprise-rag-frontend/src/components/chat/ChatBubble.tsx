import { useState } from 'react';
import { ChatMessage } from '../../types/chat';
import { MarkdownRenderer } from './MarkdownRenderer';
import { SourceCard } from './SourceCard';

interface ChatBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

export function ChatBubble({ message, onRetry }: ChatBubbleProps) {
  const [liked, setLiked] = useState(message.liked || false);
  const [disliked, setDisliked] = useState(message.disliked || false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="msg-row user">
        {message.attachedDoc && (
          <div className="doc-chip-attachment">
            <div className="doc-chip-icon">📂</div>
            <div>
              <strong>{message.attachedDoc.name}</strong>
              <div style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: 400 }}>
                {message.attachedDoc.size || 'Attached Document'}
              </div>
            </div>
          </div>
        )}
        <div className="user-text-bubble">{message.content}</div>
        <span style={{ fontSize: '10px', color: '#90a49e', paddingRight: '4px' }}>{message.timestamp}</span>
      </div>
    );
  }

  return (
    <div className="msg-row assistant">
      <div className="ai-response-card">
        <div className="ai-header">
          <div className="ai-hexagon-icon">⬡</div>
          <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--cyan-dark)' }}>Rag Assistant</span>
        </div>

        <MarkdownRenderer content={message.content} />

        {/* Source Citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="sources" style={{ marginTop: '16px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--muted)' }}>Retrieved Sources:</span>
            {message.sources.map((src) => (
              <SourceCard key={src.id} source={src} />
            ))}
          </div>
        )}

        {/* Action Toolbar Below AI Response */}
        <div className="ai-action-toolbar">
          <button
            className={`ai-action-btn ${liked ? 'active' : ''}`}
            onClick={() => {
              setLiked(!liked);
              if (disliked) setDisliked(false);
            }}
            title="Helpful response"
          >
            👍
          </button>
          <button
            className={`ai-action-btn ${disliked ? 'active' : ''}`}
            onClick={() => {
              setDisliked(!disliked);
              if (liked) setLiked(false);
            }}
            title="Not helpful"
          >
            👎
          </button>
          <button
            className="ai-action-btn"
            onClick={() => alert(`Share link copied for session!`)}
            title="Share response"
          >
            🔗
          </button>
          <button className="ai-action-btn" onClick={handleCopy} title="Copy text">
            {copied ? '✓ Copied' : '📋'}
          </button>
          <button className="ai-action-btn" onClick={onRetry} title="Regenerate answer">
            🔄
          </button>
        </div>
      </div>
      <span style={{ fontSize: '10px', color: '#90a49e', paddingLeft: '4px' }}>{message.timestamp}</span>
    </div>
  );
}
