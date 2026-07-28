export function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div className="typing-bubble">
        <div className="assistant-icon">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 0L8.5 5.5L14 7L8.5 8.5L7 14L5.5 8.5L0 7L5.5 5.5L7 0Z" fill="currentColor"/>
          </svg>
        </div>
        
        <span className="typing-text">RAG is thinking</span>
        
        <div className="typing-dots">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
      </div>
    </div>
  );
}
