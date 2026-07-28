import { useEffect, useRef, useState, useCallback } from 'react';

interface UseAutoScrollOptions {
  /**
   * Threshold in pixels from bottom to consider "at bottom"
   * Default: 100
   */
  threshold?: number;
  
  /**
   * Enable smooth scrolling behavior
   * Default: true
   */
  smooth?: boolean;
}

export function useAutoScroll<T extends HTMLElement>(
  dependencies: any[] = [],
  options: UseAutoScrollOptions = {}
) {
  const { threshold = 100, smooth = true } = options;
  
  const scrollRef = useRef<T>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const userScrolledRef = useRef(false);

  // Check if user is at the bottom
  const checkIfAtBottom = useCallback(() => {
    if (!scrollRef.current) return false;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
    
    return distanceFromBottom <= threshold;
  }, [threshold]);

  // Handle scroll event
  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    
    const atBottom = checkIfAtBottom();
    setIsAtBottom(atBottom);
    
    // If user manually scrolls to bottom, re-enable auto-scroll
    if (atBottom) {
      setShouldAutoScroll(true);
      userScrolledRef.current = false;
    } else {
      // User scrolled away from bottom
      if (!userScrolledRef.current) {
        userScrolledRef.current = true;
        setShouldAutoScroll(false);
      }
    }
  }, [checkIfAtBottom]);

  // Scroll to bottom function
  const scrollToBottom = useCallback((force = false) => {
    if (!scrollRef.current) return;
    
    if (force || shouldAutoScroll) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto',
      });
      
      setIsAtBottom(true);
      setShouldAutoScroll(true);
      userScrolledRef.current = false;
    }
  }, [shouldAutoScroll, smooth]);

  // Auto-scroll when dependencies change (new messages, etc.)
  useEffect(() => {
    if (shouldAutoScroll) {
      // Small delay to ensure DOM is updated
      const timer = setTimeout(() => scrollToBottom(), 50);
      return () => clearTimeout(timer);
    }
  }, [...dependencies, shouldAutoScroll, scrollToBottom]);

  // Attach scroll listener
  useEffect(() => {
    const element = scrollRef.current;
    if (!element) return;
    
    element.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      element.removeEventListener('scroll', handleScroll);
    };
  }, [handleScroll]);

  return {
    scrollRef,
    isAtBottom,
    scrollToBottom,
    shouldAutoScroll,
  };
}
