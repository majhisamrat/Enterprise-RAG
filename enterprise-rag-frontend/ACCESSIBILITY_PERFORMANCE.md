# Accessibility & Performance Guide

This document covers all accessibility (A11y) and performance optimizations implemented in Enterprise RAG frontend.

## 🎯 Accessibility (WCAG 2.1 AA)

### 1. Semantic HTML
All components use proper semantic HTML:
- `<button>` for actions (not `<div>`)
- `<nav>` for navigation
- `<header>` and `<footer>` for page sections
- `<main>` for primary content
- `<article>`, `<section>` for content organization

### 2. ARIA Attributes
Proper use of ARIA where semantic HTML isn't enough:
```tsx
<button aria-label="Close dialog" onClick={handleClose}>
  ✕
</button>

<div role="status" aria-live="polite">
  Document uploaded successfully
</div>

<nav aria-label="Main navigation">
  {/* Navigation items */}
</nav>
```

### 3. Keyboard Navigation
- All interactive elements are keyboard accessible
- Tab order is logical and visible
- `Escape` key closes modals/dropdowns
- Arrow keys work in list/menu components
- `Enter` or `Space` to activate buttons

Use the `trapFocus()` utility in modals:
```tsx
function Modal() {
  const modalRef = useRef<HTMLDivElement>(null);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Tab' && modalRef.current) {
      trapFocus(e, modalRef.current);
    }
  };

  return <div ref={modalRef} onKeyDown={handleKeyDown}>...</div>;
}
```

### 4. Screen Reader Support
- Announce dynamic content changes using `announceToScreenReader()`
- Use `aria-live` regions for status updates
- Provide context for icon-only buttons with `aria-label`
- Use `aria-describedby` for form field descriptions

```tsx
import { announceToScreenReader } from '@/utils/a11y';

function onDocumentUploaded() {
  announceToScreenReader('Document uploaded successfully', 'polite');
}
```

### 5. Color Contrast
- All text meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- Don't rely on color alone to convey information
- Use icons + text combinations
- Check contrast with `getContrastRatio()` utility

### 6. Focus Management
- Focus indicators are always visible (2px ring with brand-cyan)
- Focus is properly restored after closing modals
- Use `setFocus()` utility to manage focus programmatically

```tsx
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  setFocus(inputRef.current);
}, []);

return <input ref={inputRef} />;
```

### 7. Form Accessibility
All forms follow best practices:
```tsx
<div>
  <label htmlFor="email-input" className="block mb-2 font-semibold">
    Email Address
  </label>
  <input
    id="email-input"
    type="email"
    aria-describedby="email-error"
    aria-invalid={hasError}
  />
  {hasError && (
    <span id="email-error" className="text-semantic-danger text-sm">
      Please enter a valid email
    </span>
  )}
</div>
```

### 8. Skip Links
Add skip-to-content link on every page:
```tsx
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>
<main id="main-content">
  {/* Main content */}
</main>
```

### Accessibility Testing Checklist
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Verify color contrast (use WebAIM contrast checker)
- [ ] Check focus indicators are visible
- [ ] Verify form labels and error messages
- [ ] Test responsive design on mobile
- [ ] Verify zoom up to 200% works properly

## ⚡ Performance Optimizations

### 1. Code Splitting
Routes are automatically code-split by React Router. Lazy load heavy components:
```tsx
import { lazy, Suspense } from 'react';

const Blog = lazy(() => import('./pages/Blog'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Blog />
    </Suspense>
  );
}
```

### 2. Image Optimization
Use Vite's image optimization:
```tsx
// Automatic optimization for small images
import logo from '@/assets/logo.svg';

// Lazy load large images
<img data-src="large-image.jpg" alt="Description" />
```

Then call `lazyLoadImages()` on component mount:
```tsx
import { lazyLoadImages } from '@/utils/performance';

useEffect(() => {
  lazyLoadImages();
}, []);
```

### 3. Bundle Size
- Tree-shaking removes unused code
- Tailwind CSS purges unused styles
- Dynamic imports for large libraries

Check bundle size:
```bash
npm run build
# Check dist/assets for file sizes
```

### 4. Debouncing & Throttling
Use for performance-intensive operations:
```tsx
import { debounce, throttle } from '@/utils/performance';

// Search: wait 300ms after typing stops
const handleSearch = debounce((query) => {
  fetchSearchResults(query);
}, 300);

// Scroll: fire at most every 100ms
const handleScroll = throttle(() => {
  updateVisibleItems();
}, 100);
```

### 5. Memoization
Prevent unnecessary re-renders:
```tsx
import { useMemo, useCallback } from 'react';

const filteredItems = useMemo(() => {
  return items.filter((item) => item.active);
}, [items]);

const handleClick = useCallback(() => {
  doSomething();
}, []);
```

### 6. Lazy Component Loading
```tsx
const ChartComponent = lazy(() => import('./Chart'));

export function Dashboard() {
  return (
    <Suspense fallback={<Skeleton />}>
      <ChartComponent />
    </Suspense>
  );
}
```

### 7. Monitoring & Metrics
Track performance metrics:
```tsx
import { measurePerformance, measureAsyncPerformance, reportMetric } from '@/utils/performance';

// Sync operation
measurePerformance('data-processing', () => {
  processData();
});

// Async operation
await measureAsyncPerformance('api-call', async () => {
  await fetchData();
});

// Report to analytics
reportMetric('page-load', 1250, { page: '/dashboard' });
```

### 8. Resource Prefetching
Prefetch resources that will likely be needed:
```tsx
import { prefetchResource, preloadResource } from '@/utils/performance';

// In navigation handlers
prefetchResource('/api/blog-posts', 'script');

// Preload critical fonts
preloadResource('https://fonts.googleapis.com/css2?family=Manrope', 'stylesheet');
```

### 9. Lighthouse Scores Target
- **Performance**: 90+
- **Accessibility**: 95+
- **Best Practices**: 95+
- **SEO**: 95+

Run Lighthouse audit:
```bash
npm run build
npm run preview
# Open DevTools > Lighthouse
```

### 10. Web Vitals
Optimize for Core Web Vitals:
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1

## 📱 Mobile Optimization

- Touch target sizes: minimum 48x48px
- Responsive images with `srcset`
- Mobile-first CSS approach
- Efficient viewport meta tag
- Optimized font loading

## 🔍 SEO Best Practices

All implemented in `index.html`:
- ✅ Meta description tags
- ✅ Open Graph tags for social sharing
- ✅ Twitter Card tags
- ✅ Canonical URL
- ✅ Structured data (JSON-LD)
- ✅ Mobile viewport tag
- ✅ Semantic heading hierarchy

## 🧪 Testing

### Accessibility Testing
```bash
# Use axe DevTools Chrome extension
# Test with keyboard navigation
# Screen reader testing (NVDA/JAWS)
```

### Performance Testing
```bash
npm run build
npm run preview
# Open in Chrome DevTools > Lighthouse
```

## 📚 Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Accessibility Standards](https://www.a11y-101.com/)
- [Lighthouse Documentation](https://developers.google.com/web/tools/lighthouse)
- [React Accessibility](https://reactjs.org/docs/accessibility.html)

---

**Last Updated**: January 2024
