# Enterprise RAG - Frontend

A production-grade frontend for Enterprise Retrieval-Augmented Generation (RAG) system. Built with React, TypeScript, Tailwind CSS, and Framer Motion, featuring a Napkin.ai-inspired design.

## Features

- 🎨 **Modern UI Design**: Napkin.ai-inspired minimalist aesthetic with colorful gradients
- 🔍 **Hybrid Search**: Vector + keyword matching for precise document retrieval
- 📚 **Multi-format Support**: Upload PDF, Word, Markdown, HTML, and text files
- ⚡ **High Performance**: Sub-100ms query response time with optimized embeddings
- 🏢 **Multi-tenant Ready**: Complete data isolation between organizations
- 📊 **Analytics Dashboard**: Monitor retrieval accuracy and performance metrics
- 🔐 **Enterprise Security**: Google OAuth, role-based access control
- 📱 **Fully Responsive**: Works seamlessly on mobile, tablet, and desktop
- ✨ **Smooth Animations**: Framer Motion for polished user interactions

## Tech Stack

- **Frontend Framework**: React 18.3.1
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4.10
- **Animations**: Framer Motion 11.3.24
- **Routing**: React Router 7.18.1
- **UI Icons**: Lucide React
- **Charts**: Recharts 3.0.2
- **Build Tool**: Vite 5.4.21

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/enterprise-rag-frontend.git
   cd enterprise-rag-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Configure the following variables:
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_GOOGLE_CLIENT_ID=your_google_client_id
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## Project Structure

```
src/
├── api/               # API client and endpoints
├── components/        # Reusable React components
│   ├── ui/           # Base UI components (Button, Card, Input, etc.)
│   ├── blog/         # Blog-specific components
│   └── common/       # Common components (Loader, etc.)
├── data/             # Static data (blog posts, etc.)
├── hooks/            # Custom React hooks
├── layouts/          # Page layouts
├── pages/            # Full-page components
│   ├── Home.tsx      # Landing page
│   ├── Blog.tsx      # Blog listing
│   ├── Chat.tsx      # Chat interface
│   ├── Documents.tsx # Document management
│   ├── Dashboard.tsx # Analytics dashboard
│   └── ...
├── routes/           # Routing configuration
├── store/            # State management
├── styles/           # Global styles
└── types/            # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server (Vite)
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint (if configured)
- `npm run type-check` - Run TypeScript type checking

## Key Pages

- **Home** (`/`) - Landing page with features and CTA
- **Chat** (`/chat`) - Main chat interface for querying documents
- **Documents** (`/documents`) - Upload and manage documents
- **Dashboard** (`/dashboard`) - View analytics and metrics
- **Blog** (`/blog`) - Educational content about RAG systems
- **Settings** (`/settings`) - User preferences and configuration

## Blog Posts

The frontend includes 9 comprehensive blog posts:

1. **Getting Started with Enterprise RAG** - Beginner's guide to RAG concepts
2. **Building Your First Knowledge Base** - Step-by-step tutorial
3. **Optimizing Retrieval Accuracy in Production** - Performance tuning guide
4. **Multi-Tenant RAG** - Advanced scaling and data isolation
5. Plus 5 additional technical deep-dives

## Component Library

### UI Components (`src/components/ui/`)

- **Button**: Customizable button with variants and sizes
- **Card**: Container component with shadow and border
- **Input**: Form input with validation support
- **Badge**: Tag/label component
- **Select**: Dropdown selection component

### Blog Components (`src/components/blog/`)

- **EnhancedBlogCard**: Featured blog post card
- **BlogCard**: Standard blog listing card
- **VennDiagram**: Custom Venn diagram visualization

## Design System

### Colors

- **Primary**: Blue (`#3B82F6`)
- **Text**: Gray-900 (`#111827`)
- **Muted**: Gray-600 (`#4B5563`)
- **Backgrounds**: Pastel gradients (green-50, blue-50, purple-50, orange-50)

### Typography

- **Headings**: Bold, large font sizes (3xl to 7xl)
- **Body**: Gray-600 with 1.5-1.75 line height
- **Accent Text**: Colored with gradient overlays

### Spacing

- Uses Tailwind's standard scale: 4px, 8px, 12px, 16px, 24px, 32px, etc.
- Section padding: 20px, 24px, or 32px

## Performance Optimizations

- ✅ Lazy loading with React.lazy and Suspense
- ✅ Image optimization and responsive images
- ✅ Code splitting with Vite
- ✅ Tree-shaking for unused code
- ✅ CSS minification and Tailwind purging
- ✅ Gzip compression enabled

## Security

- ✅ Environment variables for sensitive data
- ✅ HTTPS enforced in production
- ✅ Google OAuth 2.0 authentication
- ✅ Role-based access control
- ✅ XSS and CSRF protection via React
- ✅ Secure headers configured

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@enterpriserag.com or open an issue on GitHub.

## Roadmap

- [ ] Dark mode support
- [ ] Internationalization (i18n)
- [ ] Advanced filtering in blog
- [ ] User feedback system
- [ ] Export/download capabilities
- [ ] Integration with more document formats

## Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy with a single click

### Netlify

1. Connect your GitHub repository to Netlify
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Set environment variables in Netlify dashboard

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## Acknowledgments

- Design inspiration from [Napkin.ai](https://www.napkin.ai)
- Icons from [Lucide React](https://lucide.dev)
- Animations powered by [Framer Motion](https://www.framer.com/motion)
- Styling with [Tailwind CSS](https://tailwindcss.com)

---

**Made with ❤️ for enterprise teams**
