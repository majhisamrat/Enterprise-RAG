import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useChatStore } from '../../store/chatStore';

export function Sidebar() {
  const navigate = useNavigate();
  const { sessions, activeSessionId, createSession, setActiveSession, deleteSession, renameSession } = useChatStore();
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const handleNewChat = () => {
    const newId = createSession();
    navigate('/chat');
    setActiveSession(newId);
  };

  const todaySessions = sessions.filter((s) => s.group === 'TODAY');
  const yesterdaySessions = sessions.filter((s) => s.group === 'YESTERDAY' || s.group === 'PREVIOUS_7_DAYS');

  const mainNavLinks = [
    { label: 'Dashboard', path: '/', icon: '▦' },
    { label: 'Upload', path: '/upload', icon: '↑' },
    { label: 'Documents', path: '/documents', icon: '▤' },
    { label: 'Chat with docs', path: '/chat', icon: '◇' },
    { label: 'Analytics', path: '/analytics', icon: '⌁' },
    { label: 'Blog & Docs', path: '/blog', icon: '📝' },
    { label: 'Settings', path: '/settings', icon: '⚙' },
  ];

  return (
    <aside className="sidebar">
      {/* App Logo */}
      <div className="sidebar-header">
        <div className="logo-icon">◇</div>
        <span>Rag chatbot</span>
      </div>

      {/* New Chat Action Button - Cyan */}
      <button className="new-chat-btn" onClick={handleNewChat}>
        <span>+</span> New Chat
      </button>

      {/* Main App Navigation */}
      <div className="sidebar-nav-section">
        <div className="sidebar-nav-title">WORKSPACE</div>
        <div className="sidebar-nav-list">
          {mainNavLinks.map((link) => (
            <NavLink key={link.path} to={link.path} className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}>
              <span>{link.icon}</span>
              <span>{link.label}</span>
            </NavLink>
          ))}
        </div>
      </div>

      {/* Chat History Group - TODAY */}
      {todaySessions.length > 0 && (
        <div className="sidebar-nav-section">
          <div className="sidebar-nav-title">TODAY</div>
          <div className="sidebar-nav-list">
            {todaySessions.map((session) => (
              <div key={session.id} style={{ position: 'relative' }}>
                <a
                  href="#chat"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveSession(session.id);
                    navigate('/chat');
                  }}
                  className={`sidebar-item ${activeSessionId === session.id ? 'active' : ''}`}
                >
                  <span style={{ fontSize: '12px' }}>💬</span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {session.title}
                  </span>
                  <button
                    className="options-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === session.id ? null : session.id);
                    }}
                  >
                    •••
                  </button>
                </a>

                {/* Dropdown Options Menu */}
                {openMenuId === session.id && (
                  <div className="options-menu">
                    <button
                      onClick={() => {
                        setOpenMenuId(null);
                        alert(`Share session: ${session.title}`);
                      }}
                    >
                      🔗 Share
                    </button>
                    <button
                      onClick={() => {
                        setOpenMenuId(null);
                        const val = prompt('Rename Chat:', session.title);
                        if (val) renameSession(session.id, val);
                      }}
                    >
                      ✏️ Rename
                    </button>
                    <button
                      className="danger"
                      onClick={() => {
                        setOpenMenuId(null);
                        deleteSession(session.id);
                      }}
                    >
                      🗑️ Delete Chat
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Chat History Group - YESTERDAY */}
      {yesterdaySessions.length > 0 && (
        <div className="sidebar-nav-section">
          <div className="sidebar-nav-title">YESTERDAY</div>
          <div className="sidebar-nav-list">
            {yesterdaySessions.map((session) => (
              <div key={session.id} style={{ position: 'relative' }}>
                <a
                  href="#chat"
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveSession(session.id);
                    navigate('/chat');
                  }}
                  className={`sidebar-item ${activeSessionId === session.id ? 'active' : ''}`}
                >
                  <span style={{ fontSize: '12px' }}>💬</span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {session.title}
                  </span>
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Profile Footer */}
      <div className="user-profile-footer">
        <div className="user-avatar">TM</div>
        <div className="user-info">
          <strong>Tran Mau Tri Tam</strong>
          <small>tam@ui8.net</small>
        </div>
      </div>
    </aside>
  );
}
