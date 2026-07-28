import { useState } from 'react';
import { ChatMessage } from '../../types/chat';
import { MarkdownRenderer } from './MarkdownRenderer';
import { SourceCard } from './SourceCard';
import { Copy, ThumbsUp, ThumbsDown, Share2, RefreshCw, Check, FileText } from 'lucide-react';

interface ChatBubbleProps {
  message: ChatMessage;
  onRetry?: () => void;
}

export function ChatBubble({ message, onRetry }: ChatBubbleProps) {
  const [liked, setLiked] = useState(message.liked || false);
  const [disliked, setDisliked] = useState(message.disliked || false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleShare = () => {
    // Placeholder for share functionality
    alert('Share functionality - Copy link to this message');
  };

  const handleLike = () => {
    setLiked(!liked);
    if (disliked) setDisliked(false);
  };

  const handleDislike = () => {
    setDisliked(!disliked);
    if (liked) setLiked(false);
  };

  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="message-row message-user">
        {message.attachedDoc && (
          <div className="attached-doc-chip">
            <FileText className="attached-doc-icon" size={20} />
            <div className="attached-doc-info">
              <span className="attached-doc-name">{message.attachedDoc.name}</span>
              <span className="attached-doc-size">{message.attachedDoc.size || 'Attached'}</span>
            </div>
          </div>
        )}
        
        <div className="message-bubble">
          <div className="message-content">{message.content}</div>
        </div>
        
        <div className="message-meta">
          <span>{message.timestamp}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="message-row message-assistant">
      <div className="message-bubble">
        {/* Assistant Header */}
        <div className="message-assistant-header">
          <div className="assistant-icon">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 0L8.5 5.5L14 7L8.5 8.5L7 14L5.5 8.5L0 7L5.5 5.5L7 0Z" fill="currentColor"/>
            </svg>
          </div>
          <span className="assistant-label">RAG Assistant</span>
        </div>

        {/* Message Content */}
        <div className="message-content">
          <MarkdownRenderer content={message.content} />
        </div>

        {/* Source Citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <span className="sources-label">Retrieved Sources</span>
            <div className="flex flex-col gap-2">
              {message.sources.map((src) => (
                <SourceCard key={src.id} source={src} />
              ))}
            </div>
          </div>
        )}

        {/* Action Toolbar - Hidden by default, shown on hover */}
        <div className="message-actions">
          <button
            className={`message-action-btn ${liked ? 'active' : ''}`}
            onClick={handleLike}
            title="Helpful response"
            aria-label="Mark as helpful"
          >
            <ThumbsUp size={14} />
          </button>
          
          <button
            className={`message-action-btn ${disliked ? 'active' : ''}`}
            onClick={handleDislike}
            title="Not helpful"
            aria-label="Mark as not helpful"
          >
            <ThumbsDown size={14} />
          </button>
          
          <button
            className="message-action-btn"
            onClick={handleCopy}
            title={copied ? 'Copied!' : 'Copy text'}
            aria-label="Copy message text"
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
          </button>
          
          <button
            className="message-action-btn"
            onClick={handleShare}
            title="Share response"
            aria-label="Share this message"
          >
            <Share2 size={14} />
          </button>
          
          {onRetry && (
            <button
              className="message-action-btn"
              onClick={onRetry}
              title="Regenerate answer"
              aria-label="Regenerate response"
            >
              <RefreshCw size={14} />
            </button>
          )}
        </div>
      </div>
      
      <div className="message-meta">
        <span>{message.timestamp}</span>
      </div>
    </div>
  );
}
