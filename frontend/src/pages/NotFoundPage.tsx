import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-muted-foreground">404</h1>
      <p className="mt-2 text-lg text-muted-foreground">Page not found</p>
      <Button asChild className="mt-6">
        <Link to="/">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Go to Dashboard
        </Link>
      </Button>
    </div>
  );
}
