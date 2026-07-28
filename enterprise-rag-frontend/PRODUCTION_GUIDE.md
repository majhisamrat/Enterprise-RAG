# Enterprise RAG Frontend - Production Grade Guide

This is a production-ready React + TypeScript frontend for the Enterprise RAG system, inspired by Napkin.ai's modern design language.

## 🚀 Quick Start

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Visit `http://localhost:5173` in your browser.

### Production Build

```bash
npm run build
```

The build output will be in the `dist/` directory, ready for deployment.

## 📁 Project Structure

```
src/
├── api/              # API integration layer
├── components/
│   ├── ui/          # Reusable UI components (Button, Card, Input, Badge)
│   ├── chat/        # Chat interface components
│   ├── blog/        # Blog-related components
│   ├── upload/      # Document upload components
│   └── dashboard/   # Dashboard widgets
├── data/            # Static data (blog posts, constants)
├── hooks/           # Custom React hooks
├── layouts/         # Layout components (DashboardLayout)
├── pages/           # Page components
├── routes/          # Router configuration
├── store/           # State management (Zustand)
├── styles/          # Global styles and Tailwind
├── types/           # TypeScript types
└── utils/           # Utility functions
```

## 🎨 Design System

### Colors

- **Brand Cyan**: `#19b5df` - Primary action color
- **Dark Sidebar**: `#13181a` - Navigation background
- **Ink**: `#141c1b` - Text color
- **Muted**: `#687772` - Secondary text
- **Line**: `#dce6e1` - Borders

Access via CSS variables or Tailwind classes:
```tsx
<div className="text-brand-cyan bg-brand-soft border-brand-line">
  Content
</div>
```

### Typography

- **Font**: Manrope (primary), DM Mono (code)
- **Sizes**: Use Tailwind classes (text-sm, text-base, text-lg, etc.)

### Components

All reusable components are in `src/components/ui/`:
- `Button` - With variants: primary, secondary, ghost, danger
- `Card` - With variants: default, elevated, outlined
- `Input` - With label, error, and icon support
- `Badge` - For tags and categories

## 🔧 Key Technologies

- **React 18.3** - UI framework
- **TypeScript 5.5** - Type safety
- **Tailwind CSS 3.4** - Utility-first styling
- **Framer Motion 11.3** - Smooth animations
- **React Router 6.28** - Client-side routing
- **Zustand 4.5** - State management
- **Axios 1.7** - HTTP client
- **Recharts 2.12** - Data visualization
- **Lucide React 0.408** - Icons

## 📝 Blog System

The blog system features dynamic content generation:

### Adding New Blog Posts

Edit `src/data/blogData.ts`:

```typescript
export const blogPosts: BlogPost[] = [
  {
    id: 'unique-slug',
    title: 'Article Title',
    summary: 'Brief summary',
    content: '# Full markdown content',
    category: 'Architecture',
    author: 'Author Name',
    date: '2024-01-15',
    readTime: 5,
    featured: true,
    tags: ['tag1', 'tag2'],
  },
  // ... more posts
];
```

### Features

- ✅ Dynamic category filtering
- ✅ Search functionality
- ✅ Featured posts showcase
- ✅ Read time estimation
- ✅ Tag-based organization
- ✅ Responsive grid layout

## 🎭 Pages

### Home (`/`)
- Landing page with hero section
- Feature showcase
- CTA buttons
- Responsive design

### Chat (`/chat`)
- Document upload interface
- Message history
- Real-time chat responses
- Markdown support

### Dashboard (`/dashboard`)
- Stats cards with trends
- Query performance charts
- Document distribution pie chart
- Recent documents table

### Blog (`/blog`)
- Featured articles section
- Dynamic blog post cards
- Search and category filtering
- "Our Story" section with Venn diagram

### Documents (`/documents`)
- Uploaded documents list
- Document management
- Delete and reindex operations

### Settings (`/settings`)
- User preferences
- Model configuration
- API settings

## 🎬 Animations

All animations use Framer Motion:

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  whileHover={{ y: -4 }}
  transition={{ duration: 0.3 }}
>
  Animated content
</motion.div>
```

Common patterns:
- `fadeIn` - Opacity animation
- `slideUp` - Slide up from below
- `whileHover` - Interactive hover effects
- `staggerContainer` - Cascading animations

## 🛡️ Performance Optimizations

1. **Code Splitting** - Route-based lazy loading
2. **Image Optimization** - Next-gen formats
3. **CSS Optimization** - Tree-shaking unused styles
4. **Bundling** - Vite for fast builds

## ♿ Accessibility

- ✅ Semantic HTML
- ✅ ARIA labels on interactive elements
- ✅ Keyboard navigation support
- ✅ Focus indicators on buttons
- ✅ Color contrast compliance (WCAG AA)

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints:
  - sm: 640px
  - md: 768px
  - lg: 1024px
  - xl: 1280px
  - 2xl: 1536px

## 🚀 Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Environment Variables

Create `.env.local`:
```
VITE_API_URL=https://your-api.com
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## 📊 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Create reusable components
4. Add Tailwind classes for styling
5. Use Framer Motion for animations

## 📄 License

Proprietary - Enterprise RAG

## 🆘 Support

For issues and questions, contact the development team.

---

**Last Updated**: January 2024
**Version**: 1.0.0
