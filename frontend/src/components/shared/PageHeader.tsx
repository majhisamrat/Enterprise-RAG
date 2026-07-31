import { cn } from '@/lib/utils';
import { FadeIn } from '@/components/shared/motion';

interface PageHeaderProps {
  title: string;
  description?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}

export function PageHeader({ title, description, children, className }: PageHeaderProps) {
  return (
    <FadeIn direction="down" duration={0.3} className={cn('flex flex-col md:flex-row md:items-center justify-between gap-6 pb-10', className)}>
      <div className="space-y-2">
        <h1 className="text-4xl lg:text-5xl font-black tracking-tight text-foreground">
          {title}
        </h1>
        {description && typeof description === 'string' ? (
          <p className="text-lg text-muted-foreground font-semibold">{description}</p>
        ) : (
          description
        )}
      </div>
      {children && <div className="flex flex-wrap items-center gap-4 shrink-0">{children}</div>}
    </FadeIn>
  );
}
