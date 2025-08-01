'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '../ui/skeleton';
import { BrainCircuit, Sparkles } from 'lucide-react';
import { apiClient, LlmQueryResponse } from '@/lib/api';

export default function LlmQueryPanel() {
  const [prompt, setPrompt] = useState('');

  const { mutate, data, isPending, error } = useMutation({
    mutationFn: ({ prompt, connectionId }: { prompt: string; connectionId: string }) => 
      apiClient.executeLlmQuery(prompt, connectionId),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      // TODO: Get actual connectionId from selected connection
      // For now, using a placeholder - this should be selected from user's connections
      const connectionId = "c1c9cb2d-0999-44cd-bca7-41128e2919e4"; // Placeholder
      mutate({ prompt, connectionId });
    }
  };

  return (
    <div className="grid h-full grid-rows-[auto,1fr] gap-6">
      <Card>
        <CardHeader>
          <CardTitle>LLM Prompt</CardTitle>
          <CardDescription>Ask the AI a question in natural language.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="e.g., 'Show me the total number of orders from John Doe'"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[100px] font-code"
            />
            <Button type="submit" disabled={isPending || !prompt.trim()}>
              {isPending ? 'Thinking...' : 'Ask AI'}
              <Sparkles className="ml-2 h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

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
