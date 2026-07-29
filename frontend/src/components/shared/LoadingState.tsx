import { cn } from '@/lib/utils';

interface LoadingStateProps {
  className?: string;
  count?: number;
}

export function LoadingState({ className, count = 3 }: LoadingStateProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse space-y-2">
          <div className="h-4 bg-muted rounded w-3/4" />
          <div className="h-3 bg-muted rounded w-1/2" />
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('rounded-xl border bg-card p-6 space-y-4', className)}>
      <div className="h-5 bg-muted rounded w-1/3 animate-pulse" />
      <div className="h-8 bg-muted rounded w-1/4 animate-pulse" />
      <div className="h-3 bg-muted rounded w-2/3 animate-pulse" />
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="h-4 bg-muted rounded flex-1 animate-pulse" />
          ))}
        </div>
      ))}
    </div>
  );
}
