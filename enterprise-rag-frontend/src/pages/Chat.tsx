import { ChatWindow } from '../components/chat/ChatWindow';

export function Chat() {
  return (
    <div className="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        <ChatWindow />
      </div>
    </div>
  );
}
