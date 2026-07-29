import { useNavigate } from 'react-router-dom';
import { useDashboard } from '@/hooks/useAnalytics';
import { PageHeader } from '@/components/shared/PageHeader';
import { CardSkeleton } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Plus, Database, FileText, Layers, Search, BarChart3 } from 'lucide-react';

const statCards = [
  { key: 'total_knowledge_bases', label: 'Knowledge Bases', icon: Database, color: 'text-blue-600' },
  { key: 'total_uploads', label: 'Uploads', icon: FileText, color: 'text-emerald-600' },
  { key: 'total_chunks', label: 'Chunks', icon: Layers, color: 'text-purple-600' },
  { key: 'total_queries', label: 'Queries', icon: Search, color: 'text-amber-600' },
  { key: 'total_pages', label: 'Pages Indexed', icon: BarChart3, color: 'text-rose-600' },
];

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useDashboard();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Dashboard" description="Overview of your RAG system" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Failed to load dashboard" onRetry={() => refetch()} />;

  const summary = data?.summary;

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your RAG system">
        <Button onClick={() => navigate('/knowledge')}>
          <Plus className="h-4 w-4 mr-1" />
          New Knowledge Base
        </Button>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {statCards.map((stat) => {
          const value = summary?.[stat.key as keyof typeof summary] ?? 0;
          const Icon = stat.icon;
          return (
            <Card key={stat.key}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{String(value)}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Knowledge Bases</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {data?.knowledge_bases?.map((kb) => (
            <Card
              key={kb.id}
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => navigate(`/knowledge/${kb.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">{kb.display_name}</CardTitle>
                  <Badge variant={kb.status === 'active' ? 'success' : 'secondary'}>{kb.status}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{kb.name}</p>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Uploads </span>
                    <span className="font-medium">{kb.statistics?.total_uploads ?? 0}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Queries </span>
                    <span className="font-medium">{kb.statistics?.query_count ?? 0}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Vectors </span>
                    <span className="font-medium">{kb.statistics?.total_vectors ?? 0}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Pages </span>
                    <span className="font-medium">{kb.statistics?.total_pages ?? 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
