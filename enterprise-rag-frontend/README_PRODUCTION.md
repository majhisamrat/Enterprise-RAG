# Enterprise RAG Frontend - Production Ready

A modern, production-grade React frontend for Enterprise Retrieval Augmented Generation system, inspired by Napkin.ai's elegant design language.

## ✨ Features

- 🎨 **Modern Design System** - Tailwind CSS with custom Napkin-inspired brand colors
- ⚡ **High Performance** - Code splitting, image optimization, efficient bundling
- ♿ **Accessible** - WCAG 2.1 AA compliant with full keyboard navigation
- 📱 **Responsive** - Mobile-first design working on all devices
- 🎬 **Smooth Animations** - Framer Motion for engaging transitions
- 🔍 **SEO Optimized** - Meta tags, structured data, sitemap
- 📊 **Data Visualization** - Recharts for beautiful analytics
- 🧠 **Smart Blog System** - Dynamic content with search and filtering
- 🔐 **Security First** - HTTPS, CSP headers, input validation
- 📈 **Monitoring Ready** - Error tracking and performance metrics

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd enterprise-rag-frontend
npm install
```

### Development

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### Production Build

```bash
npm run build
npm run preview
```

The `dist/` folder contains optimized production files.

## 📁 Project Structure

```
enterprise-rag-frontend/
├── src/
│   ├── api/                 # API client & requests
│   ├── components/          # React components
│   │   ├── ui/             # Reusable UI components
│   │   ├── chat/           # Chat interface
│   │   ├── blog/           # Blog components
│   │   ├── upload/         # Upload widgets
│   │   └── dashboard/      # Dashboard widgets
│   ├── data/               # Static data (blog posts)
│   ├── hooks/              # Custom React hooks
│   ├── layouts/            # Layout components
│   ├── pages/              # Page components
│   ├── routes/             # Router configuration
│   ├── store/              # Zustand state management
│   ├── styles/             # Global styles
│   ├── types/              # TypeScript types
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Root component
│   └── main.tsx            # Entry point
├── public/                 # Static assets
├── dist/                   # Production build (after npm run build)
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts          # Vite configuration
└── package.json            # Dependencies

```

## 🎨 Design System

### Colors
- **Primary**: `#19b5df` (Cyan)
- **Secondary**: `#1293b6` (Cyan Dark)
- **Text**: `#141c1b` (Ink)
- **Muted**: `#687772` (Muted Gray)
- **Border**: `#dce6e1` (Line)
- **Background**: `#f6f8f6` (Soft)

Access via Tailwind: `text-brand-cyan`, `bg-brand-soft`, `border-brand-line`

### Typography
- **Primary Font**: Manrope (400, 500, 600, 700, 800)
- **Code Font**: DM Mono (400, 500)

### Components
- **Button** - Primary, secondary, ghost, danger variants
- **Card** - Default, elevated, outlined variants
- **Input** - Text fields with icons and validation
- **Badge** - Category/tag indicators
- **Modal** - Accessible modals with focus trapping

## 📖 Pages

### Home (`/`)
Landing page with hero section, features showcase, and CTA.

### Chat (`/chat`)
Document upload and intelligent chat interface for querying documents.

### Dashboard (`/dashboard`)
Analytics dashboard with stats, charts, and document overview.

### Blog (`/blog`)
Searchable blog with category filtering and featured articles about RAG architecture.

### Documents (`/documents`)
Manage uploaded documents with delete and reindex operations.

### Settings (`/settings`)
User preferences and model configuration.

## 🔧 Key Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3 | UI framework |
| TypeScript | 5.5 | Type safety |
| Tailwind CSS | 3.4 | Styling |
| Framer Motion | 11.3 | Animations |
| React Router | 6.28 | Routing |
| Zustand | 4.5 | State management |
| Axios | 1.7 | HTTP client |
| Recharts | 2.12 | Charts & graphs |
| Lucide React | 0.408 | Icons |
| Vite | 5.4 | Build tool |

## 🎯 Performance Metrics

### Target Scores (Lighthouse)
- Performance: **90+**
- Accessibility: **95+**
- Best Practices: **95+**
- SEO: **95+**

### Core Web Vitals Targets
- LCP (Largest Contentful Paint): **< 2.5s**
- FID (First Input Delay): **< 100ms**
- CLS (Cumulative Layout Shift): **< 0.1**

## ♿ Accessibility Features

✅ WCAG 2.1 AA Compliant
- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader optimization
- Color contrast compliance
- Reduced motion support

Run accessibility audit:
```bash
# Open Chrome DevTools → Lighthouse → Accessibility
```

## 📊 Blog System

Dynamic blog with 5+ pre-written articles on:
- Hybrid Vector & Sparse Search in RAG
- Performance optimization techniques
- Security best practices
- Document chunking strategies
- Deployment guide

### Add New Articles
Edit `src/data/blogData.ts` and add to `blogPosts` array.

## 🔐 Security

- ✅ HTTPS/TLS enforcement
- ✅ Content Security Policy
- ✅ XSS Protection
- ✅ CORS configuration
- ✅ Input validation
- ✅ Secure headers
- ✅ No sensitive data in bundled code

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel --prod
```

### Docker
```bash
docker build -t enterprise-rag-frontend .
docker run -p 3000:3000 enterprise-rag-frontend
```

### Nginx
See `DEPLOYMENT.md` for detailed configuration.

### AWS/S3 + CloudFront
```bash
npm run build
aws s3 sync dist/ s3://bucket-name/
```

Full deployment guides in `DEPLOYMENT.md`.

## 📈 Monitoring

### Error Tracking (Sentry)
```tsx
import * as Sentry from "@sentry/react";
Sentry.init({ dsn: process.env.REACT_APP_SENTRY_DSN });
```

### Analytics (Google Analytics)
```tsx
import ReactGA from "react-ga4";
ReactGA.initialize(process.env.REACT_APP_GA_ID);
```

### Performance Metrics
Use utility functions to track performance:
```tsx
import { measurePerformance, reportMetric } from '@/utils/performance';

measurePerformance('data-processing', () => {
  processData();
});

reportMetric('page-load', 1250, { page: '/dashboard' });
```

## 🧪 Testing & Quality

```bash
# Type checking
npm run type-check

# Build
npm run build

# Preview production build
npm run preview
```

### Performance Testing
```bash
npm run build
npm run preview
# Open Chrome DevTools → Lighthouse
```

## 📚 Documentation

- `PRODUCTION_GUIDE.md` - Detailed feature documentation
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `ACCESSIBILITY_PERFORMANCE.md` - A11y and performance details
- `CHANGELOG.md` - Version history

## 🔄 Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Develop and test locally: `npm run dev`
3. Type check: `npm run type-check`
4. Build: `npm run build`
5. Commit and push
6. Create pull request
7. CI/CD pipeline runs tests
8. Deploy to production

## 📦 Dependencies

All dependencies are pinned to specific versions for stability:
```json
{
  "react": "^18.3.1",
  "tailwindcss": "^3.4.10",
  "framer-motion": "^11.3.24"
  // ... see package.json for full list
}
```

Keep dependencies updated:
```bash
npm outdated
npm update
```

## 🆘 Troubleshooting

### Issue: Page not loading
- Check browser console for errors
- Verify API endpoints in environment variables
- Clear browser cache and reload

### Issue: Styles not applying
- Restart dev server: `npm run dev`
- Check Tailwind purge configuration
- Run `npm run build` to verify

### Issue: Slow performance
- Run Lighthouse audit
- Check for unused dependencies
- Profile with Chrome DevTools

## 🤝 Contributing

1. Follow existing code style
2. Use TypeScript for type safety
3. Create reusable components
4. Add proper accessibility attributes
5. Test on mobile devices
6. Update documentation

## 📄 License

Proprietary - Enterprise RAG System

## 📞 Support & Contact

- **Issues**: Report bugs with reproduction steps
- **Questions**: Contact development team
- **Deployment**: See `DEPLOYMENT.md`

## 🎉 What's New

### Version 1.0.0 (Latest)
✨ Production-grade frontend with:
- Napkin.ai-inspired design system
- Full responsive implementation
- WCAG 2.1 AA accessibility
- Comprehensive blog system
- Performance optimizations
- Security hardening
- Production deployment ready

---

**Status**: ✅ Production Ready
**Last Updated**: January 2024
**Version**: 1.0.0
