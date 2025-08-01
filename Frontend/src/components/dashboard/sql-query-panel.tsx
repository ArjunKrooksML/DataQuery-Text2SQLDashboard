'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '../ui/skeleton';
import { Play } from 'lucide-react';
import { apiClient, SqlQueryResponse } from '@/lib/api';

export default function SqlQueryPanel() {
  const [query, setQuery] = useState('SELECT * FROM sales_data WHERE region = \'North\';');
  
  const { mutate, data, isPending, error } = useMutation({
    mutationFn: apiClient.executeSqlQuery,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      mutate(query);
    }
  };

  return (
    <div className="grid h-full grid-rows-[auto,1fr] gap-6">
      <Card>
        <CardHeader>
          <CardTitle>SQL Query</CardTitle>
          <CardDescription>Execute a SQL query against the database.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="SELECT * FROM users;"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-h-[150px] font-code"
            />
            <Button type="submit" disabled={isPending || !query.trim()}>
              {isPending ? 'Running...' : 'Run Query'}
              <Play className="ml-2 h-4 w-4" />
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Results</CardTitle>
        </CardHeader>
        <CardContent>
          {isPending && (
             <div className="space-y-2">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          )}
          {error && <p className="text-destructive">An error occurred: {error.message}</p>}
          {data && data.success && data.data && (
            <Table>
              <TableHeader>
                <TableRow>
                  {data.columns?.map((key) => (
                    <TableHead key={key}>{key}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.data.map((row, rowIndex) => (
                  <TableRow key={rowIndex}>
                    {Object.values(row).map((value, index) => (
                      <TableCell key={index}>{String(value)}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
           {(!data || !data.success) && !isPending && !error && (
            <p className="text-muted-foreground">Query results will appear here.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
