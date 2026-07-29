import { useState } from 'react';
import { useQueryAnalytics, useUsageAnalytics, usePerformanceMetrics } from '@/hooks/useAnalytics';
import { PageHeader } from '@/components/shared/PageHeader';
import { CardSkeleton } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  BarChart3, Clock, Zap, Activity, TrendingUp, Search,
} from 'lucide-react';
import { formatMs } from '@/lib/utils';

type Period = 7 | 30 | 90;

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>(7);
  const { data: perf, isLoading: perfLoading, error: perfError, refetch: refetchPerf } = usePerformanceMetrics({ days: period });
  const { data: usage, isLoading: usageLoading, error: usageError, refetch: refetchUsage } = useUsageAnalytics({ days: period });

  const isLoading = perfLoading || usageLoading;
  const error = perfError || usageError;

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Analytics" description="System performance and usage metrics" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Failed to load analytics" onRetry={() => { refetchPerf(); refetchUsage(); }} />;

  const queryMetrics = perf?.query_metrics;
  const uploadMetrics = perf?.upload_metrics;
  const usageSummary = usage?.summary;

  return (
    <div>
      <PageHeader title="Analytics" description="System performance and usage metrics">
        <Select value={String(period)} onValueChange={(v) => setPeriod(Number(v) as Period)}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
          </SelectContent>
        </Select>
      </PageHeader>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Queries</CardTitle>
            <Search className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{queryMetrics?.total_queries ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg Latency</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatMs(queryMetrics?.avg_latency_ms ?? 0)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Uploads</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uploadMetrics?.total_uploads ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pages Indexed</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{usageSummary?.total_pages_indexed ?? 0}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Query Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">p50</p>
                <p className="text-lg font-bold">{formatMs(queryMetrics?.p50_latency_ms ?? 0)}</p>
              </div>
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">p95</p>
                <p className="text-lg font-bold">{formatMs(queryMetrics?.p95_latency_ms ?? 0)}</p>
              </div>
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">p99</p>
                <p className="text-lg font-bold">{formatMs(queryMetrics?.p99_latency_ms ?? 0)}</p>
              </div>
            </div>
            <Separator />
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Avg retrieved chunks</span>
              <span className="font-medium">{queryMetrics?.avg_retrieved_chunks.toFixed(1)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Upload Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">Avg Time</p>
                <p className="text-lg font-bold">{formatMs(uploadMetrics?.avg_processing_time_ms ?? 0)}</p>
              </div>
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">p50</p>
                <p className="text-lg font-bold">{formatMs(uploadMetrics?.p50_processing_time_ms ?? 0)}</p>
              </div>
              <div className="text-center p-3 bg-muted/50 rounded-lg">
                <p className="text-xs text-muted-foreground">p95</p>
                <p className="text-lg font-bold">{formatMs(uploadMetrics?.p95_processing_time_ms ?? 0)}</p>
              </div>
            </div>
            <Separator />
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Failed uploads</span>
              <Badge variant={uploadMetrics?.failed_uploads && uploadMetrics.failed_uploads > 0 ? 'destructive' : 'success'}>
                {uploadMetrics?.failed_uploads ?? 0}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Usage Summary ({period}-day period)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Chat Messages</p>
              <p className="text-lg font-semibold">{usageSummary?.total_chat_messages ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Total Vectors</p>
              <p className="text-lg font-semibold">{usageSummary?.total_vectors ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Queries / Day</p>
              <p className="text-lg font-semibold">{usageSummary?.queries_per_day.toFixed(1)}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Messages / Day</p>
              <p className="text-lg font-semibold">{usageSummary?.messages_per_day.toFixed(1)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
