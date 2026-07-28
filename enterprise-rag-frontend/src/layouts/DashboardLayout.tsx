import { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, LogOut, Settings, HelpCircle } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

interface NavItem {
  label: string;
  path: string;
  icon: string;
}

const navItems: NavItem[] = [
  { label: 'Chat', path: '/chat', icon: '💬' },
  { label: 'Documents', path: '/documents', icon: '📄' },
  { label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { label: 'Blog', path: '/blog', icon: '📝' },
  { label: 'Analytics', path: '/analytics', icon: '📈' },
];

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 0 }}
        transition={{ duration: 0.3 }}
        className="fixed md:relative h-screen bg-dark-sidebar border-r border-dark-sidebar-border overflow-hidden"
      >
        <div className="w-80 h-full flex flex-col p-5">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8 px-2">
            <div className="w-8 h-8 bg-brand-cyan rounded-lg flex items-center justify-center text-white font-bold text-sm">
              ◇
            </div>
            <span className="text-lg font-bold text-white">Enterprise RAG</span>
          </div>

          {/* New Chat Button */}
          <button className="w-full bg-brand-cyan hover:bg-brand-cyan-dark text-white font-semibold py-3 rounded-lg mb-6 flex items-center justify-center gap-2 transition-colors shadow-cyan">
            <span>+</span> New Chat
          </button>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                  location.pathname === item.path
                    ? 'bg-dark-sidebar-active text-white'
                    : 'text-gray-400 hover:text-white hover:bg-dark-sidebar-hover'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span className="text-sm font-medium">{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="border-t border-dark-sidebar-border pt-4 space-y-2">
            <button className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-400 hover:text-white hover:bg-dark-sidebar-hover rounded-lg transition-all text-sm">
              <Settings size={16} />
              Settings
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-400 hover:text-white hover:bg-dark-sidebar-hover rounded-lg transition-all text-sm">
              <HelpCircle size={16} />
              Help
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2.5 text-gray-400 hover:text-red-400 hover:bg-dark-sidebar-hover rounded-lg transition-all text-sm">
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-brand-line px-6 py-4 flex items-center justify-between glass-effect sticky top-0 z-40">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 hover:bg-brand-soft rounded-lg text-brand-ink"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <div className="flex-1 px-4">
            <h1 className="text-2xl font-bold text-brand-ink">Enterprise RAG System</h1>
          </div>

          <button className="px-4 py-2 bg-brand-cyan text-white rounded-lg hover:bg-brand-cyan-dark transition-colors font-semibold text-sm shadow-cyan">
            Give feedback
          </button>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-8 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
