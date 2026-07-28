import { FormEvent, useState, ChangeEvent, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Paperclip } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  onAttachFile?: (file: File) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, onAttachFile, disabled }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    
    // Set height based on scrollHeight, with min and max constraints
    const newHeight = Math.min(Math.max(textarea.scrollHeight, 36), 192);
    textarea.style.height = `${newHeight}px`;
  }, [text]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    
    onSendMessage(text.trim());
    setText('');
    
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && onAttachFile) {
      onAttachFile(e.target.files[0]);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const canSend = text.trim().length > 0 && !disabled;

  return (
    <div className="chat-input-area">
      <form onSubmit={handleSubmit} className="chat-input-container">
        <div className={`chat-input-wrapper ${disabled ? 'disabled' : ''}`}>
          {/* Attach File Button */}
          <button
            type="button"
            className="attach-button"
            onClick={handleAttachClick}
            disabled={disabled}
            title="Attach file"
            aria-label="Attach file"
          >
            <Paperclip size={18} />
          </button>
          
          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.csv,.md"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            aria-label="File upload input"
          />
          
          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask RAG a question..."
            disabled={disabled}
            className="chat-textarea"
            rows={1}
            aria-label="Message input"
          />
          
          {/* Send Button */}
          <button
            type="submit"
            className="send-button"
            disabled={!canSend}
            title={canSend ? 'Send message' : 'Type a message to send'}
            aria-label="Send message"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}
