import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { BlogPost } from '../../data/blogData';
import { motion } from 'framer-motion';
import { ArrowRight, Clock, User } from 'lucide-react';

interface EnhancedBlogCardProps {
  post: BlogPost;
  featured?: boolean;
}

export function EnhancedBlogCard({ post, featured = false }: EnhancedBlogCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        variant={featured ? 'elevated' : 'default'}
        hover
        className={`p-6 flex flex-col h-full ${featured ? 'lg:col-span-2' : ''}`}
      >
        <div className="flex items-start justify-between mb-4">
          <Badge variant="primary" size={featured ? 'md' : 'sm'}>
            {post.category}
          </Badge>
          <span className="text-xs font-semibold text-brand-muted">
            {new Date(post.date).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </span>
        </div>

        <h3 className={`${featured ? 'text-2xl' : 'text-lg'} font-bold text-brand-ink mb-3 leading-tight`}>
          {post.title}
        </h3>

        <p className="text-sm text-brand-muted mb-4 flex-1 line-clamp-2">
          {post.summary}
        </p>

        <div className="space-y-3 pt-4 border-t border-brand-line">
          <div className="flex items-center gap-4 text-xs text-brand-muted">
            <div className="flex items-center gap-1.5">
              <Clock size={14} />
              {post.readTime} min read
            </div>
            <div className="flex items-center gap-1.5">
              <User size={14} />
              {post.author}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {post.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-xs bg-brand-soft text-brand-ink rounded-md hover:bg-brand-cyan hover:text-white transition-colors cursor-pointer"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        <motion.div
          className="mt-4 inline-flex items-center gap-2 text-brand-cyan font-semibold text-sm group"
          whileHover={{ x: 4 }}
        >
          Read Article
          <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
        </motion.div>
      </Card>
    </motion.div>
  );
}
