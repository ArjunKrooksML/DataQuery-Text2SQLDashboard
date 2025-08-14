'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { BrainCircuit, Database, Trash2, X } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function LogsPanel() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  const { data, isPending, error } = useQuery({
    queryKey: ['logs'],
    queryFn: () => apiClient.getQueryLogs(50),
  });

  // Mutation for deleting all query history
  const deleteAllMutation = useMutation({
    mutationFn: () => apiClient.deleteQueryHistory(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['logs'] });
      toast({
        title: 'History Cleared',
        description: `Successfully deleted ${data.deleted_count} query records.`,
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to delete query history. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Mutation for deleting single query log
  const deleteSingleMutation = useMutation({
    mutationFn: (logId: string) => apiClient.deleteSingleQueryLog(logId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['logs'] });
      toast({
        title: 'Query Deleted',
        description: 'Query log has been successfully deleted.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to delete query log. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const getIcon = (type: 'sql' | 'llm') => {
    if (type === 'sql') {
      return <Database className="h-5 w-5 text-primary" />;
    }
    return <BrainCircuit className="h-5 w-5 text-accent" />;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Query Logs</CardTitle>
            <CardDescription>A list of your recent queries.</CardDescription>
          </div>
          {data && data.length > 0 && (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={deleteAllMutation.isPending}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear History
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Clear Query History</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete all query history? This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => deleteAllMutation.mutate()}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    Delete All
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        )}
        {error && <p className="text-destructive">Failed to load logs: {error.message}</p>}
        {data && data.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No query history yet</p>
            <p className="text-sm">Execute your first SQL or LLM query to see it here.</p>
          </div>
        )}
        {data && data.length > 0 && (
          <ul className="space-y-4">
            {data.map((log, i) => (
              <li key={i} className="flex items-center gap-4 p-2 rounded-lg hover:bg-muted/50 group">
                <div className="flex-shrink-0">{getIcon(log.query_type as 'sql' | 'llm')}</div>
                <div className="flex-grow">
                  <p className="font-code text-sm truncate">{log.query_text}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => deleteSingleMutation.mutate(log.id.toString())}
                  disabled={deleteSingleMutation.isPending}
                >
                  <X className="h-4 w-4" />
                </Button>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
