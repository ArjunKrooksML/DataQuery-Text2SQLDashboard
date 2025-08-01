'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BrainCircuit, Database } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { apiClient } from '@/lib/api';

export default function LogsPanel() {
  const { data, isPending, error } = useQuery({
    queryKey: ['logs'],
    queryFn: () => apiClient.getQueryLogs(50),
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
        <CardTitle>Query Logs</CardTitle>
        <CardDescription>A list of your last 5 queries.</CardDescription>
      </CardHeader>
      <CardContent>
        {isPending && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
          </div>
        )}
        {error && <p className="text-destructive">Failed to load logs: {error.message}</p>}
        {data && (
          <ul className="space-y-4">
            {data.map((log, i) => (
              <li key={i} className="flex items-center gap-4 p-2 rounded-lg hover:bg-muted/50">
                <div className="flex-shrink-0">{getIcon(log.query_type as 'sql' | 'llm')}</div>
                <div className="flex-grow">
                  <p className="font-code text-sm truncate">{log.query_text}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
