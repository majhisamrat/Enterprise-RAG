import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKnowledgeBases, useCreateKnowledgeBase } from '@/hooks/useKnowledge';
import { PageHeader } from '@/components/shared/PageHeader';
import { CardSkeleton } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Database } from 'lucide-react';

export default function KnowledgeBasesPage() {
  const { data: kbs, isLoading, error, refetch } = useKnowledgeBases();
  const createKb = useCreateKnowledgeBase();
  const navigate = useNavigate();

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: '', display_name: '', description: '' });

  const handleCreate = async () => {
    if (!form.name || !form.display_name) return;
    await createKb.mutateAsync({
      name: form.name,
      display_name: form.display_name,
      description: form.description || undefined,
    });
    setOpen(false);
    setForm({ name: '', display_name: '', description: '' });
  };

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Knowledge Bases" description="Organize documents into domain-specific collections" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      </div>
    );
  }

  if (error) return <ErrorState title="Failed to load knowledge bases" onRetry={() => refetch()} />;

  return (
    <div>
      <PageHeader title="Knowledge Bases" description="Organize documents into domain-specific collections">
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-1" />
              New KB
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Knowledge Base</DialogTitle>
              <DialogDescription>
                A knowledge base groups related documents for focused search and chat.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="kb-name">Name (identifier)</Label>
                <Input id="kb-name" placeholder="e.g. sales_2026" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} />
                <p className="text-xs text-muted-foreground">Used in API requests, no spaces</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="kb-display">Display Name</Label>
                <Input id="kb-display" placeholder="e.g. Sales 2026 Documents" value={form.display_name} onChange={(e) => setForm((p) => ({ ...p, display_name: e.target.value }))} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="kb-desc">Description (optional)</Label>
                <Input id="kb-desc" placeholder="Description of this knowledge base" value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={createKb.isPending || !form.name || !form.display_name}>
                {createKb.isPending ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </PageHeader>

      {(!kbs || kbs.length === 0) ? (
        <EmptyState
          title="No knowledge bases yet"
          description="Create your first knowledge base to start organizing documents."
          action={{ label: 'Create Knowledge Base', onClick: () => setOpen(true) }}
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {kbs.map((kb) => (
            <Card
              key={kb.id}
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => navigate(`/knowledge/${kb.id}`)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-primary" />
                    <CardTitle className="text-base">{kb.display_name}</CardTitle>
                  </div>
                  <Badge variant={kb.status === 'active' ? 'success' : 'secondary'}>{kb.status}</Badge>
                </div>
                <p className="text-xs text-muted-foreground font-mono">{kb.name}</p>
              </CardHeader>
              <CardContent>
                {kb.description && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{kb.description}</p>
                )}
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="text-muted-foreground">Queries </span><span className="font-medium">{kb.query_count}</span></div>
                  <div><span className="text-muted-foreground">Created </span><span className="font-medium">{new Date(kb.created_at).toLocaleDateString()}</span></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
