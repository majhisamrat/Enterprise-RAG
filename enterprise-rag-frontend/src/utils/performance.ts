/**
 * Performance monitoring and optimization utilities
 */

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
}

const metrics: PerformanceMetric[] = [];

/**
 * Measure performance metric
 */
export function measurePerformance(name: string, callback: () => void): number {
  const start = performance.now();
  callback();
  const end = performance.now();
  const duration = end - start;

  metrics.push({
    name,
    value: duration,
    unit: 'ms',
    timestamp: Date.now(),
  });

  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  }

  return duration;
}

/**
 * Measure async performance
 */
export async function measureAsyncPerformance(name: string, callback: () => Promise<void>): Promise<number> {
  const start = performance.now();
  await callback();
  const end = performance.now();
  const duration = end - start;

  metrics.push({
    name,
    value: duration,
    unit: 'ms',
    timestamp: Date.now(),
  });

  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  }

  return duration;
}

/**
 * Get Web Vitals metrics
 */
export function getWebVitals(): void {
  if ('web-vital' in window && typeof window !== 'undefined') {
    // Implementation would use web-vitals library
    // This is a placeholder for Core Web Vitals collection
  }
}

/**
 * Debounce function for performance
 */
export function debounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => callback(...args), delay);
  };
}

/**
 * Throttle function for performance
 */
export function throttle<T extends (...args: any[]) => any>(
  callback: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      callback(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Lazy load images
 */
export function lazyLoadImages(): void {
  if ('IntersectionObserver' in window) {
    const imageElements = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          img.src = img.dataset.src || '';
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      });
    });

    imageElements.forEach((img) => imageObserver.observe(img));
  }
}

/**
 * Report metrics (for analytics)
 */
export function reportMetric(name: string, value: number, extra?: Record<string, any>): void {
  if (process.env.NODE_ENV === 'production' && typeof window !== 'undefined') {
    // Send to analytics service
    const payload = {
      name,
      value,
      timestamp: Date.now(),
      ...extra,
    };

    // Example: navigator.sendBeacon('/api/metrics', JSON.stringify(payload));
    console.debug('[Metric]', payload);
  }
}

/**
 * Get stored metrics
 */
export function getMetrics(): PerformanceMetric[] {
  return [...metrics];
}

/**
 * Clear metrics
 */
export function clearMetrics(): void {
  metrics.length = 0;
}

/**
 * Prefetch resource
 */
export function prefetchResource(url: string, type: 'script' | 'stylesheet' | 'image' = 'script'): void {
  if (!document) return;

  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;

  if (type === 'stylesheet') {
    link.as = 'style';
  } else if (type === 'script') {
    link.as = 'script';
  } else if (type === 'image') {
    link.as = 'image';
  }

  document.head.appendChild(link);
}

/**
 * Preload critical resource
 */
export function preloadResource(url: string, type: 'script' | 'stylesheet' | 'font'): void {
  if (!document) return;

  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = url;

  if (type === 'stylesheet') {
    link.as = 'style';
  } else if (type === 'script') {
    link.as = 'script';
  } else if (type === 'font') {
    link.as = 'font';
    link.crossOrigin = 'anonymous';
  }

  document.head.appendChild(link);
}
