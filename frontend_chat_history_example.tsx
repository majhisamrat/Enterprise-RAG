// ChatHistory.tsx - React component for chat history functionality

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  MessageSquare, 
  Trash2, 
  Calendar,
  Search,
  X 
} from 'lucide-react';

interface ChatSession {
  session_id: string;
  title: string;
  knowledge_base_id?: string;
  knowledge_base_name: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatMessage {
  id: string;
  sender_role: 'user' | 'assistant';
  content: string;
  created_at: string;
  sources?: Array<{
    document_id?: string;
    page_number: number;
    relevance_score: number;
    text_snippet: string;
  }>;
}

interface ChatHistoryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession: (sessionId: string) => void;
  currentSessionId?: string;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ 
  isOpen, 
  onClose, 
  onSelectSession, 
  currentSessionId 
}) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [sessionMessages, setSessionMessages] = useState<ChatMessage[]>([]);

  // Fetch chat history
  const fetchChatHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/chat/history', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch specific session messages
  const fetchSessionMessages = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/v1/chat/history/${sessionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionMessages(data.messages);
        setSelectedSession(sessionId);
      }
    } catch (error) {
      console.error('Failed to fetch session messages:', error);
    }
  };

  // Delete session
  const deleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this chat session?')) return;
    
    try {
      const response = await fetch(`/api/v1/chat/history/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        setSessions(prev => prev.filter(s => s.session_id !== sessionId));
        if (selectedSession === sessionId) {
          setSelectedSession(null);
          setSessionMessages([]);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  // Filter sessions based on search
  const filteredSessions = sessions.filter(session => 
    session.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    session.knowledge_base_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  useEffect(() => {
    if (isOpen) {
      fetchChatHistory();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-full max-h-[80vh] flex overflow-hidden">
        
        {/* Left Sidebar - Session List */}
        <div className="w-1/3 border-r border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Chat History
              </h2>
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Search */}
            <div className="mt-3 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search conversations..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          
          {/* Session List */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">Loading...</div>
            ) : filteredSessions.length === 0 ? (
              <div className="p-4 text-center text-gray-500">No chat sessions found</div>
            ) : (
              filteredSessions.map((session) => (
                <div
                  key={session.session_id}
                  className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                    currentSessionId === session.session_id ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                  onClick={() => fetchSessionMessages(session.session_id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {session.title}
                      </h3>
                      <p className="text-xs text-gray-500 mt-1">
                        {session.knowledge_base_name}
                      </p>
                      <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
                        <MessageSquare className="w-3 h-3" />
                        <span>{session.message_count} messages</span>
                        <Calendar className="w-3 h-3 ml-2" />
                        <span>{formatDate(session.updated_at)}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-1 ml-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectSession(session.session_id);
                          onClose();
                        }}
                        className="p-1 hover:bg-blue-100 rounded text-blue-600"
                        title="Load this conversation"
                      >
                        <MessageSquare className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.session_id);
                        }}
                        className="p-1 hover:bg-red-100 rounded text-red-600"
                        title="Delete conversation"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Right Panel - Message View */}
        <div className="flex-1 flex flex-col">
          {selectedSession ? (
            <>
              <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Conversation Messages</h3>
              </div>
              
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {sessionMessages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender_role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        message.sender_role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="text-sm">{message.content}</div>
                      
                      {/* Sources for assistant messages */}
                      {message.sender_role === 'assistant' && message.sources && message.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <div className="text-xs text-gray-600 mb-1">Sources:</div>
                          {message.sources.map((source, idx) => (
                            <div key={idx} className="text-xs text-gray-500 mb-1">
                              📄 Page {source.page_number} (Score: {source.relevance_score.toFixed(2)})
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <div className="text-xs opacity-70 mt-1">
                        {formatDate(message.created_at)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a conversation to view messages</p>
              </div>
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
};

// ChatHistoryIcon.tsx - Icon component for navbar

interface ChatHistoryIconProps {
  onClick: () => void;
  className?: string;
}

export const ChatHistoryIcon: React.FC<ChatHistoryIconProps> = ({ onClick, className = "" }) => {
  return (
    <button
      onClick={onClick}
      className={`p-2 rounded-lg hover:bg-gray-100 transition-colors ${className}`}
      title="Chat History"
    >
      <Clock className="w-5 h-5 text-gray-600" />
    </button>
  );
};

// Usage Example in your main chat component:

export const ChatContainer: React.FC = () => {
  const [showHistory, setShowHistory] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
    // Load the selected session in your chat interface
    loadChatSession(sessionId);
  };

  const loadChatSession = async (sessionId: string) => {
    // Your logic to load and display the selected chat session
    console.log('Loading session:', sessionId);
  };

  return (
    <div className="chat-container">
      {/* Your navbar */}
      <div className="navbar flex items-center justify-between p-4">
        <div className="flex items-center gap-4">
          <h1>Chat Assistant</h1>
          
          {/* Add the chat history icon here */}
          <ChatHistoryIcon 
            onClick={() => setShowHistory(true)}
            className="ml-4"
          />
        </div>
        
        <div className="flex items-center gap-2">
          {/* Knowledge Base Selector */}
          <select className="kb-selector">
            <option value="">All Knowledge Bases</option>
            {/* Your KB options */}
          </select>
          
          <button className="new-chat-btn">+ New Chat</button>
        </div>
      </div>
      
      {/* Your chat interface */}
      <div className="chat-messages">
        {/* Your chat messages */}
      </div>
      
      {/* Chat History Modal */}
      <ChatHistory
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        onSelectSession={handleSelectSession}
        currentSessionId={currentSessionId}
      />
    </div>
  );
};