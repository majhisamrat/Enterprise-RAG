import { motion } from 'framer-motion';
import { Button } from '../components/ui/Button';
import { Navbar } from '../components/Navbar';
import { ArrowRight, Zap, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <Navbar />

      {/* Hero Section - Napkin.ai inspired */}
      <motion.section
        className="pt-32 pb-20 px-4 sm:px-6 lg:px-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex flex-col items-center text-center space-y-8">
            {/* Icon with background */}
            <motion.div
              className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-50 rounded-2xl flex items-center justify-center"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: 'spring' }}
            >
              <Sparkles className="w-8 h-8 text-blue-600" />
            </motion.div>

            {/* Headline with mixed styling - Napkin AI style */}
            <motion.div
              className="space-y-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-tight">
                Get intelligent answers
              </h1>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 flex-wrap">
                <span className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900">from</span>
                <div className="bg-gradient-to-r from-blue-400 to-cyan-300 text-transparent bg-clip-text inline-block px-4 py-2 rounded-lg">
                  <span className="text-5xl sm:text-6xl lg:text-7xl font-bold">your documents</span>
                </div>
              </div>
            </motion.div>

            {/* Subheading */}
            <motion.p
              className="text-lg sm:text-xl text-gray-600 max-w-2xl leading-relaxed"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.6 }}
            >
              Turn PDFs, wikis, and docs into a searchable knowledge base. Ask questions. Get contextual answers. No hallucinations.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4 pt-4"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <motion.button
                onClick={() => navigate('/chat')}
                className="px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-xl transition flex items-center justify-center gap-2 group"
                whileHover={{ y: -2, boxShadow: '0 12px 32px rgba(59, 130, 246, 0.4)' }}
                whileTap={{ scale: 0.95 }}
              >
                Start asking questions
                <ArrowRight size={18} className="group-hover:translate-x-1 transition" />
              </motion.button>

              <motion.button
                onClick={() => navigate('/blog')}
                className="px-6 sm:px-8 py-3 sm:py-4 border-2 border-gray-200 text-gray-900 font-semibold rounded-lg hover:bg-gray-50 transition"
                whileHover={{ borderColor: '#000' }}
                whileTap={{ scale: 0.95 }}
              >
                Learn more
              </motion.button>
            </motion.div>

            {/* Trust indicators */}
            <motion.div
              className="pt-8 text-sm text-gray-500 space-y-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <p>✨ No credit card required • 🚀 Free tier available</p>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* Feature Grid Section - Napkin style with colored boxes */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
              Built for enterprise knowledge
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to transform documents into searchable intelligence
            </p>
          </motion.div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: '📤',
                title: 'Multi-format ingestion',
                description: 'PDF, Word, Markdown, HTML, text. Upload any format.',
                color: 'from-green-50 to-green-100',
                border: 'border-green-200',
              },
              {
                icon: '🔍',
                title: 'Hybrid search',
                description: 'Vector + keyword matching. Find exact matches and semantic concepts.',
                color: 'from-blue-50 to-blue-100',
                border: 'border-blue-200',
              },
              {
                icon: '⚡',
                title: 'Sub-100ms latency',
                description: 'Pre-warmed embeddings and optimized indexing for instant responses.',
                color: 'from-purple-50 to-purple-100',
                border: 'border-purple-200',
              },
              {
                icon: '🏢',
                title: 'Multi-tenant ready',
                description: 'Serve multiple organizations with complete data isolation.',
                color: 'from-orange-50 to-orange-100',
                border: 'border-orange-200',
              },
              {
                icon: '📊',
                title: 'Analytics & insights',
                description: 'Monitor retrieval accuracy, query patterns, and performance metrics.',
                color: 'from-red-50 to-red-100',
                border: 'border-red-200',
              },
              {
                icon: '🔐',
                title: 'Enterprise security',
                description: 'Google OAuth, role-based access, encrypted data at rest and in transit.',
                color: 'from-indigo-50 to-indigo-100',
                border: 'border-indigo-200',
              },
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                className={`bg-gradient-to-br ${feature.color} border ${feature.border} rounded-2xl p-8 hover:shadow-lg transition`}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.08 }}
                whileHover={{ y: -4 }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-700 text-sm leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works - Visual step-by-step */}
      <section id="how" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">How it works</h2>
            <p className="text-lg text-gray-600">Four simple steps to intelligent document retrieval</p>
          </motion.div>

          {/* Steps */}
          <div className="space-y-12">
            {[
              {
                step: '1',
                title: 'Upload your documents',
                description: 'Drag and drop PDFs, Word docs, Markdown files, or paste text directly. Supports any document format.',
                icon: '📄',
                accent: 'green',
              },
              {
                step: '2',
                title: 'We index and embed',
                description: 'Our system chunks documents, generates embeddings, and creates both vector and keyword indices for fast retrieval.',
                icon: '⚙️',
                accent: 'blue',
              },
              {
                step: '3',
                title: 'Ask your questions',
                description: 'Query your knowledge base with natural language. Our hybrid search finds the most relevant content instantly.',
                icon: '💬',
                accent: 'purple',
              },
              {
                step: '4',
                title: 'Get precise answers',
                description: 'Responses grounded in your actual documents, with citations so you know exactly where the info came from.',
                icon: '✨',
                accent: 'orange',
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                className="grid md:grid-cols-2 gap-12 items-center"
                initial={{ opacity: 0, x: idx % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
              >
                <div className={idx % 2 === 1 ? 'md:order-2' : ''}>
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 bg-gray-900 text-white rounded-lg flex items-center justify-center font-bold">
                      {item.step}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-3">{item.title}</h3>
                      <p className="text-gray-600 text-lg leading-relaxed">{item.description}</p>
                    </div>
                  </div>
                </div>

                <motion.div
                  className={`md:order-${idx % 2 === 1 ? '1' : '2'} text-6xl text-center p-12 rounded-3xl bg-gradient-to-br ${
                    item.accent === 'green'
                      ? 'from-green-50 to-green-100 border border-green-200'
                      : item.accent === 'blue'
                      ? 'from-blue-50 to-blue-100 border border-blue-200'
                      : item.accent === 'purple'
                      ? 'from-purple-50 to-purple-100 border border-purple-200'
                      : 'from-orange-50 to-orange-100 border border-orange-200'
                  }`}
                  whileHover={{ y: -8 }}
                >
                  {item.icon}
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases - Napkin style */}
      <section id="features" className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-20"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">Use cases</h2>
            <p className="text-lg text-gray-600">Perfect for teams across your organization</p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: '📚', title: 'Documentation', description: 'Internal wikis & API docs' },
              { icon: '🏪', title: 'E-commerce', description: 'Product catalogs & specs' },
              { icon: '⚖️', title: 'Legal', description: 'Contracts & policies' },
              { icon: '🏥', title: 'Healthcare', description: 'Medical records & protocols' },
              { icon: '📖', title: 'Learning', description: 'Training & courses' },
              { icon: '🔬', title: 'Research', description: 'Papers & datasets' },
              { icon: '💼', title: 'HR', description: 'Policies & handbooks' },
              { icon: '📰', title: 'Content', description: 'Articles & newsletters' },
            ].map((useCase, idx) => (
              <motion.div
                key={idx}
                className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition text-center"
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.05 }}
                whileHover={{ y: -4 }}
              >
                <div className="text-4xl mb-3">{useCase.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{useCase.title}</h3>
                <p className="text-sm text-gray-600">{useCase.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { stat: '98%+', label: 'Retrieval Accuracy' },
              { stat: '142ms', label: 'Query Response' },
              { stat: '50K+', label: 'Documents Indexed' },
              { stat: '99.9%', label: 'Uptime SLA' },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl sm:text-5xl font-bold mb-2">{item.stat}</div>
                <p className="text-gray-300 text-sm">{item.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <motion.div
          className="max-w-2xl mx-auto text-center space-y-8"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl sm:text-5xl font-bold text-gray-900">
            Ready to get started?
          </h2>
          <p className="text-lg text-gray-600">
            Transform your documents into intelligence. Start free, no credit card required.
          </p>
          <motion.button
            onClick={() => navigate('/chat')}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-xl transition inline-flex items-center gap-2 group text-lg"
            whileHover={{ y: -2, boxShadow: '0 12px 32px rgba(59, 130, 246, 0.4)' }}
            whileTap={{ scale: 0.95 }}
          >
            Start free
            <Zap size={20} className="group-hover:scale-110 transition" />
          </motion.button>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-16 px-4 sm:px-6 lg:px-8 border-t border-gray-800">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-5 gap-12 mb-12">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-blue-600 rounded flex items-center justify-center">
                  <span className="text-white font-bold text-xs">◆</span>
                </div>
                <span className="font-semibold">Enterprise RAG</span>
              </div>
              <p className="text-sm text-gray-400">Transform documents into intelligent knowledge.</p>
            </div>

            {[
              {
                title: 'Product',
                links: [
                  { label: 'Features', href: '#features' },
                  { label: 'Pricing', href: '#' },
                  { label: 'Security', href: '#' },
                ],
              },
              {
                title: 'Company',
                links: [
                  { label: 'Blog', href: '/blog' },
                  { label: 'About', href: '#' },
                  { label: 'Contact', href: '#' },
                ],
              },
              {
                title: 'Legal',
                links: [
                  { label: 'Privacy', href: '#' },
                  { label: 'Terms', href: '#' },
                ],
              },
              {
                title: 'Social',
                links: [
                  { label: 'Twitter', href: '#' },
                  { label: 'GitHub', href: '#' },
                  { label: 'LinkedIn', href: '#' },
                ],
              },
            ].map((col) => (
              <div key={col.title}>
                <h3 className="font-semibold text-white mb-4">{col.title}</h3>
                <ul className="space-y-2">
                  {col.links.map((link) => (
                    <li key={link.label}>
                      <a href={link.href} className="text-sm hover:text-white transition">
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-sm text-gray-500">
            <p>&copy; 2024 Enterprise RAG. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
