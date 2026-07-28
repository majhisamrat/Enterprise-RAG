# Getting Started with Enterprise RAG Frontend

Complete step-by-step guide to get your production-ready frontend up and running.

## 📋 System Requirements

- **Node.js**: 18+ (LTS recommended)
- **npm**: 9+ or yarn 3+
- **Git**: For version control
- **Browser**: Chrome, Firefox, Safari, or Edge (latest)

Check your versions:
```bash
node --version    # v18.17.0 or higher
npm --version     # 9.6.0 or higher
```

## 🚀 Installation (5 minutes)

### Step 1: Navigate to Frontend Directory

```bash
cd enterprise-rag-frontend
```

### Step 2: Install Dependencies

```bash
npm install
# or
yarn install
```

This installs all packages including:
- React 18.3
- Tailwind CSS 3.4
- Framer Motion 11.3
- React Router 6.28
- And 15+ more libraries

### Step 3: Create Environment File

Create `.env.local` in the root directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here

# Optional: Analytics & Error Tracking
VITE_SENTRY_DSN=your-sentry-dsn-here
VITE_GA_ID=your-google-analytics-id-here
```

**Important**: Never commit `.env.local` to git. It's already in `.gitignore`.

### Step 4: Start Development Server

```bash
npm run dev
```

You should see:
```
Local:        http://localhost:5173/
```

Open http://localhost:5173 in your browser.

## 🎯 Explore the Application

### Pages to Visit

1. **Home** (http://localhost:5173)
   - Landing page with hero section
   - Features showcase
   - Call-to-action buttons

2. **Chat** (http://localhost:5173/chat)
   - Document upload interface
   - Test the chat functionality
   - Upload a PDF to see it in action

3. **Dashboard** (http://localhost:5173/dashboard)
   - Analytics and statistics
   - Charts and visualizations
   - Document management

4. **Blog** (http://localhost:5173/blog)
   - Read the 5+ pre-written articles
   - Use search to find articles
   - Filter by category

5. **Documents** (http://localhost:5173/documents)
   - Manage uploaded documents
   - Delete or reindex documents

## 🛠️ Development Workflow

### Common Commands

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build locally
npm run preview

# Full build + preview
npm run build && npm run preview
```

### File Structure Quick Reference

```
src/
├── pages/              # Page components
│   ├── Home.tsx       # Landing page
│   ├── Chat.tsx       # Chat interface
│   ├── Dashboard.tsx  # Analytics dashboard
│   └── Blog.tsx       # Blog page
│
├── components/        # React components
│   ├── ui/            # Reusable UI components
│   ├── chat/          # Chat widgets
│   ├── blog/          # Blog widgets
│   └── dashboard/     # Dashboard widgets
│
├── utils/             # Utility functions
│   ├── a11y.ts       # Accessibility utilities
│   ├── performance.ts # Performance utilities
│   ├── validation.ts  # Input validation
│   └── formatting.ts  # Text formatting
│
├── styles/            # Styling
│   └── globals.css   # Global styles & Tailwind
│
└── hooks/             # Custom React hooks
    ├── useChat.ts    # Chat hook
    ├── useUpload.ts  # Upload hook
    └── useDocuments.ts # Documents hook
```

## 🎨 Customizing the Design

### Change Brand Colors

Edit `tailwind.config.js`:

```javascript
colors: {
  brand: {
    cyan: '#19b5df',        // Change primary color
    'cyan-dark': '#1293b6', // Change hover color
    ink: '#141c1b',         // Change text color
    // ... more colors
  }
}
```

Then use in components:
```tsx
<div className="text-brand-cyan bg-brand-soft">Custom colors</div>
```

### Customize Typography

Edit `tailwind.config.js` font config:
```javascript
fontFamily: {
  sans: ['Your Font Here', 'fallback'],
  mono: ['Your Mono Font', 'fallback'],
}
```

## 📝 Adding Content

### Add Blog Articles

Edit `src/data/blogData.ts`:

```typescript
{
  id: 'my-article',
  title: 'My Article Title',
  summary: 'Short description (1-2 sentences)',
  content: `# Full Markdown Content
    
  Write your article here using markdown.
  `,
  category: 'Architecture', // or 'Performance', 'Security', etc.
  author: 'Your Name',
  date: '2024-01-20',
  readTime: 5, // Estimated read time in minutes
  featured: true, // Show on homepage?
  tags: ['tag1', 'tag2', 'tag3'],
}
```

The blog page will automatically:
- Show featured articles first
- Display category filters
- Provide search functionality
- Calculate read time

### Add Navigation Items

Edit `src/layouts/DashboardLayout.tsx`:

```typescript
const navItems: NavItem[] = [
  { label: 'Chat', path: '/chat', icon: '💬' },
  { label: 'Your New Page', path: '/your-page', icon: '🎯' },
  // ... add more items
];
```

## 🔧 Using Components

### Button Component

```tsx
import { Button } from '@/components/ui';

// Variants: primary, secondary, ghost, danger
<Button variant="primary">Click me</Button>

// Sizes: sm, md, lg
<Button size="lg">Large button</Button>

// With icon
<Button icon={<ArrowRight size={20} />} iconPosition="right">
  Continue
</Button>

// Loading state
<Button isLoading>Processing...</Button>
```

### Card Component

```tsx
import { Card } from '@/components/ui';

// Variants: default, elevated, outlined
<Card variant="elevated" hover>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>
```

### Input Component

```tsx
import { Input } from '@/components/ui';

<Input
  label="Email"
  type="email"
  placeholder="name@example.com"
  error={error}
  icon={<Mail size={20} />}
/>
```

### Badge Component

```tsx
import { Badge } from '@/components/ui';

// Variants: primary, secondary, success, warning, danger
<Badge variant="primary">Architecture</Badge>
<Badge variant="success">Active</Badge>
```

## 🎬 Using Animations

```tsx
import { motion } from 'framer-motion';

// Simple fade-in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
>
  Faded content
</motion.div>

// Slide up on entrance
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
>
  Slid up content
</motion.div>

// Interactive hover effect
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Hover me
</motion.button>
```

## 🧰 Using Utilities

### Format Data

```tsx
import { 
  formatFileSize, 
  formatDate, 
  truncateText,
  getReadingTime 
} from '@/utils/formatting';

formatFileSize(1024000)           // "1000 KB"
formatDate(new Date())            // "Jan 20, 2024"
truncateText('Long text...', 20)  // "Long text..."
getReadingTime(articleText)       // 5 (minutes)
```

### Validate Input

```tsx
import { 
  isValidEmail, 
  isValidUrl, 
  isValidPhoneNumber,
  isStrongPassword 
} from '@/utils/validation';

isValidEmail('test@example.com')        // true
isValidUrl('https://example.com')       // true
isValidPhoneNumber('+1234567890')       // true
isStrongPassword('MyPass123!')          // true
```

### Track Performance

```tsx
import { 
  measurePerformance, 
  debounce,
  throttle 
} from '@/utils/performance';

// Measure sync operation
measurePerformance('my-task', () => {
  doSomething();
});

// Debounced search
const handleSearch = debounce((query) => {
  searchAPI(query);
}, 300);

// Throttled scroll
const handleScroll = throttle(() => {
  updateUI();
}, 100);
```

### Accessibility

```tsx
import { 
  announceToScreenReader, 
  setFocus,
  trapFocus 
} from '@/utils/a11y';

// Announce to screen readers
announceToScreenReader('Success! Document uploaded', 'polite');

// Set focus programmatically
setFocus(submitButton);

// Trap focus in modal
const handleKeyDown = (e) => {
  if (e.key === 'Tab') {
    trapFocus(e, modalElement);
  }
};
```

## 🧪 Testing Your Changes

### Type Checking

```bash
npm run type-check
```

Fix any TypeScript errors before proceeding.

### Visual Testing

```bash
npm run dev
# Open http://localhost:5173
# Test all pages and interactions
```

### Performance Testing

```bash
npm run build
npm run preview
# Open DevTools → Lighthouse → Run audit
```

Target scores:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 95+

### Accessibility Testing

```bash
# Test with keyboard only (no mouse)
# Open DevTools → Lighthouse → Accessibility
# Test with screen reader (if available)
```

## 🚀 Building for Production

### Step 1: Final Checks

```bash
npm run type-check    # No TypeScript errors
npm run build         # Build succeeds
```

### Step 2: Build

```bash
npm run build
```

Output:
- Creates `dist/` directory
- Optimized JavaScript/CSS
- Ready to deploy

### Step 3: Preview Production Build

```bash
npm run preview
```

Test the production build locally before deploying.

## 📦 Deployment Options

### Quick Deploy to Vercel (Recommended)

```bash
npm install -g vercel
vercel --prod
```

### Docker Deployment

```bash
# Build image
docker build -t enterprise-rag-frontend .

# Run container
docker run -p 3000:3000 enterprise-rag-frontend

# Visit http://localhost:3000
```

### Static Hosting (S3, Netlify, GitHub Pages)

```bash
npm run build
# Upload dist/ folder to your host
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README_PRODUCTION.md` | Complete project overview |
| `QUICK_START.md` | 5-minute quick reference |
| `PRODUCTION_GUIDE.md` | Feature documentation |
| `DEPLOYMENT.md` | Deployment instructions |
| `ACCESSIBILITY_PERFORMANCE.md` | A11y & performance guide |
| `ARCHITECTURE.md` | System architecture details |
| `TRANSFORMATION_SUMMARY.md` | What was built |

## 🆘 Troubleshooting

### Problem: "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### Problem: Port 5173 already in use
**Solution**: 
```bash
npm run dev -- --port 3000
```

### Problem: Styles not applying
**Solution**: 
```bash
# Restart dev server
# Ctrl+C to stop
npm run dev
```

### Problem: API calls failing
**Solution**: 
- Check `.env.local` has correct `VITE_API_URL`
- Ensure backend is running (port 8000)
- Check browser console for CORS errors

### Problem: TypeScript errors
**Solution**:
```bash
npm run type-check
# Fix errors shown
```

## 💡 Pro Tips

1. **Use DevTools Chrome Extension**
   - React DevTools (components inspector)
   - Redux DevTools (state management)
   - Lighthouse (performance audit)

2. **Keep Components Small**
   - Each component = one responsibility
   - Easier to test and maintain

3. **Reuse Utilities**
   - Check `src/utils/` before writing code
   - 30+ utilities already available

4. **Use Tailwind First**
   - Custom CSS only when necessary
   - Most styles can be built with Tailwind

5. **Test on Mobile**
   - Responsive design is critical
   - Use Chrome DevTools device emulation

6. **Monitor Performance**
   - Run Lighthouse audit regularly
   - Target: Performance 90+, Accessibility 95+

7. **Keep Dependencies Updated**
   ```bash
   npm outdated        # See outdated packages
   npm update          # Update all packages
   ```

## 🎓 Learning Path

### Day 1: Setup & Exploration
- [ ] Install and run locally
- [ ] Explore all pages
- [ ] Read QUICK_START.md

### Day 2: Customization
- [ ] Change brand colors
- [ ] Add blog articles
- [ ] Customize navigation

### Day 3: Development
- [ ] Create new page
- [ ] Add new component
- [ ] Use utilities in components

### Day 4: Optimization
- [ ] Run Lighthouse audit
- [ ] Fix performance issues
- [ ] Test accessibility

### Day 5: Deployment
- [ ] Build for production
- [ ] Test production build
- [ ] Deploy to hosting

## 🎉 You're Ready!

Your Enterprise RAG frontend is now ready for development and deployment.

**Next Steps**:
1. ✅ Install dependencies
2. ✅ Setup environment variables
3. ✅ Run development server
4. ✅ Explore the application
5. ✅ Start customizing
6. ✅ Deploy to production

---

**Questions?** Check the relevant documentation file.
**Issues?** See the troubleshooting section.
**Ready to deploy?** See DEPLOYMENT.md.

**Happy coding! 🚀**
