import { useChat } from '../../hooks/useChat';
import { useUpload } from '../../hooks/useUpload';
import { UploadBox } from '../upload/UploadBox';
import { UploadProgress } from '../upload/UploadProgress';
import { ChatBubble } from './ChatBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import { motion } from 'framer-motion';

export function ChatWindow() {
  const { activeSession, isGenerating, sendMessage, setAttachedDoc } = useChat();
  const { uploadFile, uploading, progress } = useUpload();

  const handleFileUpload = (file: File) => {
    uploadFile(file);
  };

  const hasMessages = activeSession && activeSession.messages.length > 0;

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-lg overflow-hidden">
      {uploading && <UploadProgress progress={progress} filename="Document" />}

      {!hasMessages ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex-1 flex flex-col items-center justify-center px-8 py-12 text-center"
        >
          <h2 className="text-5xl font-bold text-brand-ink mb-6 leading-tight">
            Please Upload Your Documents<br />
            <span className="text-brand-cyan">Before You Ask</span>
          </h2>
          <p className="text-brand-muted max-w-md mb-12">
            Start by uploading your PDFs, documents, or knowledge base. Our system will analyze them and provide intelligent responses.
          </p>
          <UploadBox onFileSelect={handleFileUpload} />
        </motion.div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {activeSession.messages.map((msg, idx) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
              >
                <ChatBubble
                  message={msg}
                  onRetry={() => sendMessage(msg.content)}
                />
              </motion.div>
            ))}
            {isGenerating && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <TypingIndicator />
              </motion.div>
            )}
          </div>

          <div className="border-t border-brand-line p-6 bg-white">
            <ChatInput
              onSendMessage={sendMessage}
              onAttachFile={(file) => {
                uploadFile(file);
                setAttachedDoc({ name: file.name, size: (file.size / (1024 * 1024)).toFixed(1) + ' MB' });
              }}
              disabled={isGenerating || uploading}
            />
          </div>
        </>
      )}
    </div>
  );
}
