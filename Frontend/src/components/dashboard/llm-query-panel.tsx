'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Skeleton } from '../ui/skeleton';
import { BrainCircuit, Sparkles, Database, Eye } from 'lucide-react';
import { apiClient, LlmQueryResponse } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function LlmQueryPanel() {
  const [prompt, setPrompt] = useState('');
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');
  const { toast } = useToast();

  // Fetch user's database connections
  const { data: connections, isLoading: connectionsLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
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

  return (
    <div className="grid h-full grid-rows-[auto,auto,1fr] gap-6">
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
            </div>
          )}
          {!data && !isPending && !error && (
            <p className="text-muted-foreground">The AI's response will appear here.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
