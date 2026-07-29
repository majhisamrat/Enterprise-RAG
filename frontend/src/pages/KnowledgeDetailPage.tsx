import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  useKnowledgeBase,
  useUploadHistory,
  useDeleteKnowledgeBase,
  useUploadDocument,
  useReindexKb,
} from '@/hooks/useKnowledge';
import { PageHeader } from '@/components/shared/PageHeader';
import { LoadingState, CardSkeleton } from '@/components/shared/LoadingState';
import { ErrorState } from '@/components/shared/ErrorState';
import { EmptyState } from '@/components/shared/EmptyState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from '@/components/ui/dialog';
import {
  ArrowLeft, Upload, RefreshCw, Trash2, FileText, AlertCircle, Clock, Database, Layers, BarChart3,
} from 'lucide-react';
import { formatBytes, formatMs, formatDate } from '@/lib/utils';

export default function KnowledgeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: kb, isLoading, error, refetch } = useKnowledgeBase(id);
  const { data: history } = useUploadHistory(id);
  const deleteKb = useDeleteKnowledgeBase();
  const uploadDoc = useUploadDocument();
  const reindexKb = useReindexKb();

  const [uploadOpen, setUploadOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [tags, setTags] = useState('');

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading..." />
        <CardSkeleton />
      </div>
    );
  }

  if (error) return <ErrorState title="Failed to load knowledge base" onRetry={() => refetch()} />;
  if (!kb) return <ErrorState title="Knowledge base not found" />;

  const handleUpload = async () => {
    if (!file) return;
    await uploadDoc.mutateAsync({ kbId: id!, file, displayName: displayName || undefined, tags: tags || undefined });
    setUploadOpen(false);
    setFile(null);
    setDisplayName('');
    setTags('');
  };

  const handleDelete = async () => {
    await deleteKb.mutateAsync(id!);
    navigate('/knowledge');
  };

  const stats = [
    { label: 'Uploads', value: history?.total ?? 0, icon: FileText },
    { label: 'Queries', value: kb.query_count, icon: BarChart3 },
  ];

  return (
    <div>
      <PageHeader
        title={kb.display_name}
        description={<span className="font-mono text-xs">{kb.name}</span>}
      >
        <Button variant="outline" onClick={() => navigate('/knowledge')}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <Button variant="outline" onClick={() => reindexKb.mutate(id!)} disabled={reindexKb.isPending}>
          <RefreshCw className="h-4 w-4 mr-1" />
          Reindex
        </Button>
        <Button onClick={() => setUploadOpen(true)}>
          <Upload className="h-4 w-4 mr-1" />
          Upload
        </Button>
        <Button variant="destructive" onClick={() => setDeleteOpen(true)}>
          <Trash2 className="h-4 w-4 mr-1" />
          Delete
        </Button>
      </PageHeader>

      {kb.description && (
        <p className="text-sm text-muted-foreground mb-6">{kb.description}</p>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{String(s.value)}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4">Upload History</h2>
        {!history || history.uploads.length === 0 ? (
          <EmptyState
            title="No uploads yet"
            description="Upload documents to this knowledge base to enable search and chat."
            action={{ label: 'Upload Document', onClick: () => setUploadOpen(true) }}
          />
        ) : (
          <div className="space-y-3">
            {history.uploads.map((u) => (
              <Card key={u.id}>
                <CardContent className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3 min-w-0">
                    <FileText className="h-5 w-5 text-muted-foreground shrink-0" />
                    <div className="min-w-0">
                      <p className="font-medium truncate">{u.original_filename}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatBytes(u.file_size_bytes)} &middot; {u.page_count} pages &middot; {u.chunk_count} chunks &middot; {u.total_vectors} vectors
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <Badge variant={u.processing_status === 'completed' ? 'success' : u.processing_status === 'failed' ? 'destructive' : 'warning'}>
                      {u.processing_status}
                    </Badge>
                    {u.processing_duration_ms > 0 && (
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatMs(u.processing_duration_ms)}
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>
              Supported formats: PDF, DOCX, TXT, MD, CSV, PPTX, XLSX
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="file">File</Label>
              <Input id="file" type="file" accept=".pdf,.docx,.txt,.md,.csv,.pptx,.xlsx" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="display-name">Display Name (optional)</Label>
              <Input id="display-name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Defaults to filename" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tags">Tags (optional, comma-separated)</Label>
              <Input id="tags" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="e.g. sales, q1, 2026" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setUploadOpen(false)}>Cancel</Button>
            <Button onClick={handleUpload} disabled={!file || uploadDoc.isPending}>
              {uploadDoc.isPending ? 'Uploading...' : 'Upload'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Knowledge Base?</DialogTitle>
            <DialogDescription>
              This will permanently delete all uploads, vectors, and chat sessions for this KB. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              All {history?.total ?? 0} uploads and their vectors will be removed.
            </AlertDescription>
          </Alert>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleteKb.isPending}>
              {deleteKb.isPending ? 'Deleting...' : 'Delete Forever'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
