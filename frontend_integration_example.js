// Frontend Integration Example for Chat History
// Add this to your navbar component

import React, { useState, useEffect } from 'react';

const ChatHistoryIcon = () => {
    const [sessions, setSessions] = useState([]);
    const [showHistory, setShowHistory] = useState(false);

    // Fetch chat history from your new backend endpoints
    const fetchChatHistory = async () => {
        try {
            const response = await fetch('/api/v1/chat/history', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                setSessions(data.sessions || []);
            }
        } catch (error) {
            console.error('Error fetching chat history:', error);
        }
    };

    // Load specific chat session
    const loadChatSession = async (sessionId) => {
        try {
            const response = await fetch(`/api/v1/chat/history/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                // Load messages into chat interface
                // You'll need to implement this based on your chat component
                console.log('Loaded session:', data.session);
                console.log('Messages:', data.messages);
            }
        } catch (error) {
            console.error('Error loading session:', error);
        }
    };

    // Delete chat session
    const deleteSession = async (sessionId) => {
        if (!confirm('Delete this chat session?')) return;
        
        try {
            const response = await fetch(`/api/v1/chat/history/${sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (response.ok) {
                // Refresh history
                fetchChatHistory();
            }
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    };

    useEffect(() => {
        if (showHistory) {
            fetchChatHistory();
        }
    }, [showHistory]);

    return (
        <div className="chat-history-container">
            {/* History Icon Button */}
            <button 
                className="chat-history-icon"
                onClick={() => setShowHistory(!showHistory)}
                title="Chat History"
            >
                📋 {/* or use an icon library like Lucide/Heroicons */}
            </button>

            {/* History Dropdown/Sidebar */}
            {showHistory && (
                <div className="chat-history-dropdown">
                    <h3>Chat History</h3>
                    
                    {sessions.length === 0 ? (
                        <p>No chat sessions found</p>
                    ) : (
                        <ul className="sessions-list">
                            {sessions.map(session => (
                                <li key={session.session_id} className="session-item">
                                    <div 
                                        className="session-info"
                                        onClick={() => loadChatSession(session.session_id)}
                                    >
                                        <div className="session-title">
                                            {session.title || 'Untitled Chat'}
                                        </div>
                                        <div className="session-meta">
                                            <small>{session.knowledge_base_name}</small>
                                            <small>{session.message_count} messages</small>
                                            <small>{new Date(session.created_at).toLocaleDateString()}</small>
                                        </div>
                                    </div>
                                    
                                    <button 
                                        className="delete-session"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteSession(session.session_id);
                                        }}
                                    >
                                        🗑️
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatHistoryIcon;

/* CSS Styles - Add to your stylesheet */
/*
.chat-history-container {
    position: relative;
    display: inline-block;
}

.chat-history-icon {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
}

.chat-history-icon:hover {
    background-color: rgba(0, 0, 0, 0.1);
}

.chat-history-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #ccc;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    width: 320px;
    max-height: 400px;
    overflow-y: auto;
    z-index: 1000;
    padding: 16px;
}

.sessions-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.session-item {
    display: flex;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
}

.session-item:hover {
    background-color: #f5f5f5;
}

.session-info {
    flex: 1;
}

.session-title {
    font-weight: 600;
    margin-bottom: 4px;
}

.session-meta {
    display: flex;
    gap: 8px;
    font-size: 0.8rem;
    color: #666;
}

.delete-session {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
    opacity: 0.6;
}

.delete-session:hover {
    opacity: 1;
    color: red;
}
*/