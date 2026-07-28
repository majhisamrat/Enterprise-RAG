import { FormEvent, useState, ChangeEvent } from 'react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  onAttachFile?: (file: File) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, onAttachFile, disabled }: ChatInputProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && onAttachFile) {
      onAttachFile(e.target.files[0]);
    }
  };

  return (
    <form className="chat-input-wrapper" onSubmit={handleSubmit}>
      <div className="chat-input-bar">
        <label className="attach-btn" style={{ cursor: 'pointer' }} title="Attach file">
          📎
          <input
            type="file"
            accept=".pdf,.docx,.txt,.csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </label>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message to Rag..."
          disabled={disabled}
        />
        <button className="send-circle-btn" type="submit" disabled={disabled || !text.trim()} title="Send message">
          ➤
        </button>
      </div>
    </form>
  );
}
