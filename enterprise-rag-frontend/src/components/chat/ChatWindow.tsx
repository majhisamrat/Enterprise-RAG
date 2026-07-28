import { useChat } from '../../hooks/useChat';
import { useUpload } from '../../hooks/useUpload';
import { useAutoScroll } from '../../hooks/useAutoScroll';
import { UploadBox } from '../upload/UploadBox';
import { UploadProgress } from '../upload/UploadProgress';
import { ChatBubble } from './ChatBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';

export function ChatWindow() {
  const { activeSession, isGenerating, sendMessage, setAttachedDoc } = useChat();
  const { uploadFile, uploading, progress } = useUpload();
  
  // Auto-scroll functionality
  const { scrollRef, isAtBottom, scrollToBottom } = useAutoScroll<HTMLDivElement>(
    [activeSession?.messages.length, isGenerating],
    { threshold: 100, smooth: true }
  );

  const handleFileUpload = (file: File) => {
    uploadFile(file);
  };

  const hasMessages = activeSession && activeSession.messages.length > 0;

  return (
    <div className="chat-container">
      {/* Upload Progress Bar */}
      <AnimatePresence>
        {uploading && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <UploadProgress progress={progress} filename="Document" />
          </motion.div>
        )}
      </AnimatePresence>

      {!hasMessages ? (
        /* Empty State - Before First Message */
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="chat-empty-state"
        >
          <h2 className="empty-state-title">
            Upload Your Documents
            <br />
            <span className="empty-state-highlight">To Get Started</span>
          </h2>
          <p className="empty-state-description">
            Start by uploading PDFs, documents, or knowledge base files. 
            Our system will analyze them and provide intelligent, contextual responses to your questions.
          </p>
          <UploadBox onFileSelect={handleFileUpload} />
        </motion.div>
      ) : (
        <>
          {/* Messages Area */}
          <div ref={scrollRef} className="chat-messages">
            <AnimatePresence initial={false}>
              {activeSession.messages.map((msg, idx) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ 
                    duration: 0.3, 
                    delay: idx * 0.03,
                    ease: 'easeOut'
                  }}
                >
                  <ChatBubble
                    message={msg}
                    onRetry={() => sendMessage(msg.content)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
            
            {/* Typing Indicator */}
            <AnimatePresence>
              {isGenerating && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <TypingIndicator />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Jump to Latest Button - Shows when scrolled up */}
          <AnimatePresence>
            {!isAtBottom && (
              <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.2 }}
                onClick={() => scrollToBottom(true)}
                className="jump-to-latest"
                aria-label="Scroll to latest message"
              >
                <span>New messages</span>
                <ChevronDown size={16} />
              </motion.button>
            )}
          </AnimatePresence>

          {/* Input Area */}
          <ChatInput
            onSendMessage={sendMessage}
            onAttachFile={(file) => {
              uploadFile(file);
              setAttachedDoc({ 
                name: file.name, 
                size: (file.size / (1024 * 1024)).toFixed(1) + ' MB' 
              });
            }}
            disabled={isGenerating || uploading}
          />
        </>
      )}
    </div>
  );
}
