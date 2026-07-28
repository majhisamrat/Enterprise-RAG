import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { label: 'Features', href: '/#features' },
    { label: 'How it works', href: '/#how' },
    { label: 'Blog', href: '/blog' },
  ];

  const isActive = (href: string) => {
    if (href.includes('#')) {
      return location.pathname === '/' && location.hash === href.split('#')[1];
    }
    return location.pathname === href;
  };

  return (
    <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-md z-50 border-b border-gray-200/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-16 flex items-center justify-between">
          {/* Logo */}
          <motion.div
            className="flex-shrink-0 cursor-pointer"
            whileHover={{ scale: 1.05 }}
            onClick={() => navigate('/')}
          >
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">◆</span>
              </div>
              <span className="text-lg font-semibold text-gray-900 hidden sm:inline">Enterprise RAG</span>
            </div>
          </motion.div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-12">
            <div className="flex items-center gap-8">
              {navItems.map((item) => (
                <motion.a
                  key={item.label}
                  href={item.href}
                  className={`text-sm font-medium transition ${
                    isActive(item.href)
                      ? 'text-blue-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                  whileHover={{ y: -2 }}
                >
                  {item.label}
                </motion.a>
              ))}
            </div>

            {/* Auth Buttons */}
            <div className="flex items-center gap-3 pl-8 border-l border-gray-200">
              <motion.button
                onClick={() => navigate('/login')}
                className="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                whileHover={{ backgroundColor: 'rgba(0,0,0,0.05)' }}
              >
                Sign in
              </motion.button>
              <motion.button
                onClick={() => navigate('/chat')}
                className="text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2 rounded-lg hover:shadow-lg transition"
                whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(59, 130, 246, 0.3)' }}
                whileTap={{ scale: 0.95 }}
              >
                Get started
              </motion.button>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-600"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <motion.div
            className="md:hidden pb-4 space-y-4"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="block text-sm font-medium text-gray-600 hover:text-gray-900 py-2"
              >
                {item.label}
              </a>
            ))}
            <div className="pt-4 border-t border-gray-200 space-y-2">
              <button
                onClick={() => navigate('/login')}
                className="w-full text-sm font-medium text-gray-600 py-2"
              >
                Sign in
              </button>
              <button
                onClick={() => navigate('/chat')}
                className="w-full text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2 rounded-lg"
              >
                Get started
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  );
}
