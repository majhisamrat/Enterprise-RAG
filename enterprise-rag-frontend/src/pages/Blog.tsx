import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { VennDiagram } from '../components/blog/VennDiagram';
import { EnhancedBlogCard } from '../components/blog/EnhancedBlogCard';
import { blogPosts, getAllCategories, getFeaturedPosts } from '../data/blogData';
import { Search } from 'lucide-react';

export function Blog() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const categories = getAllCategories();
  const featuredPosts = getFeaturedPosts();

  const filteredPosts = useMemo(() => {
    return blogPosts.filter((post) => {
      const matchesCategory = !selectedCategory || post.category === selectedCategory;
      const matchesSearch =
        searchQuery === '' ||
        post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        post.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      return matchesCategory && matchesSearch;
    });
  }, [selectedCategory, searchQuery]);

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm z-50 border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
          <a href="/" className="text-lg font-bold text-gray-900">
            Enterprise RAG
          </a>
          <div className="hidden md:flex items-center gap-6 text-sm">
            <a href="/" className="text-gray-600 hover:text-gray-900">Home</a>
            <a href="/chat" className="text-gray-600 hover:text-gray-900">Chat</a>
            <a href="/blog" className="text-gray-900 font-medium">Blog</a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <motion.section
        className="pt-24 pb-12 px-4 sm:px-6 lg:px-8 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-4">
          Deep dives into RAG
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Learn how to build, optimize, and deploy retrieval augmented generation systems.
        </p>
      </motion.section>

      {/* Our Story Section */}
      <motion.section
        className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 grid lg:grid-cols-2 gap-12 items-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex justify-center">
          <VennDiagram />
        </div>

        <div>
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Our mission</h2>
          
          <div className="space-y-4 text-gray-600 leading-relaxed">
            <p>
              Enterprise documentation is often trapped across hundreds of PDFs, slides, spreadsheets, and technical docs. Traditional keyword search yields outdated, fragmented results.
            </p>

            <p>
              We built Enterprise RAG to bridge this gap. By combining dense vector retrieval with sparse keyword matching and pre-warmed embeddings, teams get precise answers with verifiable citations in milliseconds.
            </p>

            <p className="italic text-gray-700 font-medium pt-4">
              "Visual context truly captures the essence of an idea."
            </p>
          </div>
        </div>
      </motion.section>

      {/* Search and Filters */}
      <motion.section
        className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="space-y-6">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Categories */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedCategory === null
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
              }`}
            >
              All
            </button>

            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  selectedCategory === cat
                    ? 'bg-gray-900 text-white'
                    : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Articles Grid */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        {filteredPosts.length > 0 ? (
          <motion.div
            className="grid md:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {filteredPosts.map((post, idx) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <EnhancedBlogCard post={post} />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No articles found.</p>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto text-center text-sm text-gray-600">
          <p>&copy; 2024 Enterprise RAG. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
