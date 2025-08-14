'use client';

import React, { useState, useMemo } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '../ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Line, Doughnut, Pie } from 'react-chartjs-2';
import { Play, Database, History, Clock, BarChart3, PieChart, TrendingUp, Table as TableIcon } from 'lucide-react';
import { apiClient, SqlQueryResponse, DatabaseConnection } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { formatDistanceToNow } from 'date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

export default function SqlQueryPanel() {
  const [query, setQuery] = useState('SELECT * FROM sales_data WHERE region = \'North\';');
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');
  const [chartType, setChartType] = useState<'bar' | 'line' | 'pie' | 'doughnut'>('bar');
  const { toast } = useToast();

  const { data: connections, isLoading: connectionsLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
  });

  // Fetch SQL query history
  const { data: sqlHistory, isLoading: historyLoading, refetch: refetchHistory } = useQuery({
    queryKey: ['sql-history'],
    queryFn: () => apiClient.getQueryLogs(20).then(logs => 
      logs.filter(log => log.query_type === 'sql')
    ),
  });

  const { mutate, data, isPending, error } = useMutation({
    mutationFn: ({ query, connectionId }: { query: string; connectionId: string }) =>
      apiClient.executeSqlQuery(query, connectionId),
    onSuccess: () => {
      refetchHistory();
      toast({
        title: 'Query Executed',
        description: 'SQL query executed successfully.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Query Failed',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && selectedConnectionId) {
      mutate({ query, connectionId: selectedConnectionId });
    }
  };

  const useHistoryQuery = (historyQuery: string) => {
    setQuery(historyQuery);
  };

  // Process SQL results for chart visualization
  const chartData = useMemo(() => {
    if (!data || !data.success || !data.data || data.data.length === 0) {
      return null;
    }

    const results = data.data;
    const columns = data.columns || [];

    // Find potential numeric columns for visualization
    const numericColumns = columns.filter(col => {
      return results.some(row => {
        const value = row[col];
        return !isNaN(Number(value)) && value !== null && value !== '';
      });
    });

    // Find potential categorical columns
    const categoricalColumns = columns.filter(col => {
      return !numericColumns.includes(col);
    });

    if (numericColumns.length === 0) {
      return null;
    }

    // Use first categorical column as labels, first numeric column as data
    const labelColumn = categoricalColumns[0] || columns[0];
    const dataColumn = numericColumns[0];

    const labels = results.map(row => String(row[labelColumn])).slice(0, 20); // Limit to 20 items
    const values = results.map(row => Number(row[dataColumn]) || 0).slice(0, 20);

    // Generate colors
    const colors = labels.map((_, index) => 
      `hsl(${(index * 137.5) % 360}, 70%, 60%)`
    );

    return {
      labels,
      datasets: [{
        label: dataColumn,
        data: values,
        backgroundColor: chartType === 'line' ? 'rgba(59, 130, 246, 0.1)' : colors,
        borderColor: chartType === 'line' ? 'rgb(59, 130, 246)' : colors,
        borderWidth: 1,
        fill: chartType === 'line' ? true : false,
      }]
    };
  }, [data, chartType]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: data?.columns?.[0] ? `${data.columns[0]} Analysis` : 'Query Results Visualization'
      }
    },
    scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
      y: {
        beginAtZero: true,
      },
    } : undefined,
  };

  React.useEffect(() => {
    if (connections && connections.length > 0 && (!selectedConnectionId || selectedConnectionId === "loading" || selectedConnectionId === "none")) {
      setSelectedConnectionId(connections[0].id);
    }
  }, [connections, selectedConnectionId]);

  return (
    <div className="grid h-full grid-cols-[1fr,350px] gap-6">
      {/* Main Panel */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>SQL Query</CardTitle>
            <CardDescription>Execute a SQL query against the database.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Connection Selector */}
              <div className="space-y-2">
                <Label htmlFor="connection">Database Connection</Label>
                <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a database connection" />
                  </SelectTrigger>
                  <SelectContent>
                    {connectionsLoading ? (
                      <SelectItem value="loading" disabled>Loading connections...</SelectItem>
                    ) : connections && connections.length > 0 ? (
                      connections.map((connection: DatabaseConnection) => (
                        <SelectItem key={connection.id} value={connection.id}>
                          {connection.name} ({connection.database_type})
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="none" disabled>No connections available</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              <Textarea
                placeholder="SELECT * FROM users;"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="min-h-[150px] font-code"
              />
              <Button 
                type="submit" 
                disabled={isPending || !query.trim() || !selectedConnectionId || selectedConnectionId === "loading" || selectedConnectionId === "none"}
              >
                {isPending ? 'Running...' : 'Run Query'}
                <Play className="ml-2 h-4 w-4" />
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Results with Tabs for Table and Charts */}
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
            {data && data.success && (
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{data.row_count} rows returned</span>
                <Badge variant="outline">
                  <Clock className="h-3 w-3 mr-1" />
                  {data.execution_time_ms}ms
                </Badge>
              </div>
            )}
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
              <Tabs defaultValue="table" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="table" className="flex items-center gap-2">
                    <TableIcon className="h-4 w-4" />
                    Table View
                  </TabsTrigger>
                  <TabsTrigger value="charts" className="flex items-center gap-2" disabled={!chartData}>
                    <BarChart3 className="h-4 w-4" />
                    Chart View
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="table" className="mt-4">
                  <div className="max-h-[400px] overflow-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {data.columns?.map((key) => (
                            <TableHead key={key} className="font-medium">{key}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {data.data.map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {Object.values(row).map((value, index) => (
                              <TableCell key={index} className="font-mono text-sm">
                                {String(value)}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </TabsContent>
                
                <TabsContent value="charts" className="mt-4">
                  {chartData ? (
                    <div className="space-y-4">
                      {/* Chart Type Selector */}
                      <div className="flex items-center gap-4">
                        <Label>Chart Type:</Label>
                        <Select value={chartType} onValueChange={(value: any) => setChartType(value)}>
                          <SelectTrigger className="w-48">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bar">
                              <div className="flex items-center gap-2">
                                <BarChart3 className="h-4 w-4" />
                                Bar Chart
                              </div>
                            </SelectItem>
                            <SelectItem value="line">
                              <div className="flex items-center gap-2">
                                <TrendingUp className="h-4 w-4" />
                                Line Chart
                              </div>
                            </SelectItem>
                            <SelectItem value="pie">
                              <div className="flex items-center gap-2">
                                <PieChart className="h-4 w-4" />
                                Pie Chart
                              </div>
                            </SelectItem>
                            <SelectItem value="doughnut">
                              <div className="flex items-center gap-2">
                                <PieChart className="h-4 w-4" />
                                Doughnut Chart
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      {/* Chart Display */}
                      <div className="h-[400px] w-full">
                        {chartType === 'bar' && <Bar data={chartData} options={chartOptions} />}
                        {chartType === 'line' && <Line data={chartData} options={chartOptions} />}
                        {chartType === 'pie' && <Pie data={chartData} options={chartOptions} />}
                        {chartType === 'doughnut' && <Doughnut data={chartData} options={chartOptions} />}
                      </div>
                      
                      {/* Chart Info */}
                      <div className="text-sm text-muted-foreground">
                        <p>Automatically generated from your SQL query results.</p>
                        <p>Showing data from columns: {data.columns?.join(', ')}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p className="font-medium">No chart data available</p>
                      <p className="text-sm">Your query results need numeric data to generate charts.</p>
                      <p className="text-sm">Try queries with numeric columns for visualization.</p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            )}
            
            {data && !data.success && (
              <div className="p-4 border border-destructive rounded-lg">
                <p className="text-destructive font-medium">Query Error:</p>
                <p className="text-sm text-muted-foreground mt-1">{data.message}</p>
              </div>
            )}
            {(!data || !data.success) && !isPending && !error && (
              <p className="text-muted-foreground">Query results will appear here.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* History Sidebar */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            SQL Query History
          </CardTitle>
          <CardDescription>Recent SQL queries and results</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="max-h-[600px] overflow-y-auto">
            {historyLoading ? (
              <div className="p-4 space-y-3">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : sqlHistory && sqlHistory.length > 0 ? (
              <div className="space-y-2">
                {sqlHistory.map((log, index) => (
                  <div
                    key={index}
                    className="p-3 hover:bg-muted/50 cursor-pointer border-b border-border group"
                    onClick={() => useHistoryQuery(log.query_text)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-mono truncate">{log.query_text}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge 
                            variant={log.status === 'success' ? 'default' : 'destructive'}
                            className="text-xs"
                          >
                            {log.status}
                          </Badge>
                          {log.execution_time_ms && (
                            <Badge variant="outline" className="text-xs">
                              <Clock className="h-3 w-3 mr-1" />
                              {log.execution_time_ms}ms
                            </Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                          </span>
                        </div>
                      </div>
                      <Database className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-muted-foreground">
                <Database className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No SQL queries yet</p>
                <p className="text-xs">Execute your first query to see history here</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}