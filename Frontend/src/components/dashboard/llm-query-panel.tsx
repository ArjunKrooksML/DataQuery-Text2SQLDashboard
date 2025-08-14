'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '../ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { BrainCircuit, Sparkles, Database, Eye, History, Clock, X } from 'lucide-react';
import { apiClient, LlmQueryResponse } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatDistanceToNow } from 'date-fns';

export default function LlmQueryPanel() {
  const [prompt, setPrompt] = useState('');
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');
  const { toast } = useToast();

  // Fetch user's database connections
  const { data: connections, isLoading: connectionsLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
  });

  // Fetch LLM query history
  const { data: llmHistory, isLoading: historyLoading, refetch: refetchHistory } = useQuery({
    queryKey: ['llm-history'],
    queryFn: () => apiClient.getQueryLogs(20).then(logs => 
      logs.filter(log => log.query_type === 'llm')
    ),
  });

  // Fetch schema for selected connection
  const { data: schema, isLoading: schemaLoading } = useQuery({
    queryKey: ['schema', selectedConnectionId],
    queryFn: () => apiClient.getConnectionSchema(selectedConnectionId),
    enabled: !!selectedConnectionId,
  });

  const { mutate, data, isPending, error } = useMutation({
    mutationFn: ({ prompt, connectionId }: { prompt: string; connectionId: string }) => 
      apiClient.executeLlmQuery(prompt, connectionId),
    onSuccess: () => {
      refetchHistory();
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && selectedConnectionId) {
      mutate({ prompt, connectionId: selectedConnectionId });
    } else if (!selectedConnectionId) {
      toast({
        title: 'No Connection Selected',
        description: 'Please select a database connection first.',
        variant: 'destructive',
      });
    }
  };

  const useHistoryPrompt = (historyPrompt: string) => {
    setPrompt(historyPrompt);
  };

  return (
    <div className="grid h-full grid-cols-[1fr,400px] gap-6">
      {/* Main Panel */}
      <div className="space-y-6">
        {/* Connection Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Database Connection
            </CardTitle>
            <CardDescription>Select a database to provide context for the AI</CardDescription>
          </CardHeader>
          <CardContent>
            {connectionsLoading ? (
              <Skeleton className="h-10 w-full" />
            ) : (
              <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a database connection" />
                </SelectTrigger>
                <SelectContent>
                  {connections?.map((connection) => (
                    <SelectItem key={connection.id} value={connection.id}>
                      {connection.name} ({connection.database_name})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </CardContent>
        </Card>

        {/* Schema Display */}
        {selectedConnectionId && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Database Schema
              </CardTitle>
              <CardDescription>Available tables and columns for AI context</CardDescription>
            </CardHeader>
            <CardContent>
              {schemaLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[60%]" />
                  <Skeleton className="h-4 w-[80%]" />
                  <Skeleton className="h-4 w-[40%]" />
                </div>
              ) : schema ? (
                <div className="max-h-40 overflow-y-auto space-y-2">
                  {schema.schema_data?.tables?.map((table: any) => (
                    <div key={table.name} className="p-2 bg-muted rounded">
                      <div className="font-medium text-sm">{table.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {table.columns?.map((col: any) => col.name).join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">No schema information available</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* LLM Query Form */}
        <Card>
          <CardHeader>
            <CardTitle>LLM Prompt</CardTitle>
            <CardDescription>
              Ask the AI a question in natural language. The AI will use the selected database schema for context.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Textarea
                placeholder="e.g., 'Show me the total number of orders from John Doe' or 'What are the most popular products?'"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[100px] font-code"
              />
              <Button 
                type="submit" 
                disabled={isPending || !prompt.trim() || !selectedConnectionId}
              >
                {isPending ? 'Thinking...' : 'Ask AI'}
                <Sparkles className="ml-2 h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* AI Response */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BrainCircuit className="h-5 w-5" />
              AI Response
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isPending && (
              <div className="space-y-2">
                <Skeleton className="h-4 w-[80%]" />
                <Skeleton className="h-4 w-[60%]" />
              </div>
            )}
            {error && <p className="text-destructive">An error occurred: {error.message}</p>}
            {data && (
              <div className="prose prose-invert max-w-none text-foreground">
                <p>{data.response}</p>
                {data.sql_generated && (
                  <div className="mt-4 p-3 bg-muted rounded-lg">
                    <p className="text-sm font-mono text-muted-foreground">Generated SQL:</p>
                    <p className="text-sm font-mono">{data.sql_generated}</p>
                  </div>
                )}
                {data.confidence_score && (
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant="outline">
                      Confidence: {Math.round(data.confidence_score * 100)}%
                    </Badge>
                    <Badge variant="outline">
                      <Clock className="h-3 w-3 mr-1" />
                      {data.execution_time_ms}ms
                    </Badge>
                  </div>
                )}
              </div>
            )}
            {!data && !isPending && !error && (
              <p className="text-muted-foreground">The AI's response will appear here.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* History Sidebar */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            LLM Query History
          </CardTitle>
          <CardDescription>Recent AI prompts and responses</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-[600px] overflow-y-auto">
            {historyLoading ? (
              <div className="p-4 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : llmHistory && llmHistory.length > 0 ? (
              <div className="space-y-2">
                {llmHistory.map((log, index) => (
                  <div
                    key={index}
                    className="p-3 hover:bg-muted/50 cursor-pointer border-b border-border group"
                    onClick={() => useHistoryPrompt(log.query_text)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{log.query_text}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge 
                            variant={log.status === 'success' ? 'default' : 'destructive'}
                            className="text-xs"
                          >
                            {log.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                          </span>
                        </div>
                      </div>
                      <BrainCircuit className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-muted-foreground">
                <BrainCircuit className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No LLM queries yet</p>
                <p className="text-xs">Ask your first AI question to see history here</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}