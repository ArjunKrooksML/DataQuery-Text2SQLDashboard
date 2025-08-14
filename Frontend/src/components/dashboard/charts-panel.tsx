'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Line, Doughnut, Pie } from 'react-chartjs-2';
import { BarChart3, TrendingUp, Database, Clock, Activity, PieChart, RefreshCw, Play } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';
import { useToast } from '@/hooks/use-toast';

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

export default function ChartsPanel() {
  const [selectedQueryId, setSelectedQueryId] = useState<string>('');
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>('');
  const [chartType, setChartType] = useState<'bar' | 'line' | 'pie' | 'doughnut'>('bar');
  const { toast } = useToast();

  // Fetch user's database connections
  const { data: connections, isLoading: connectionsLoading } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
  });

  // Fetch all query logs for analytics (general analytics)
  const { data: queryLogs, isLoading: logsLoading } = useQuery({
    queryKey: ['analytics-logs'],
    queryFn: () => apiClient.getQueryLogs(100),
  });

  // Fetch successful SQL queries for visualization selection
  const { data: sqlQueries, isLoading: sqlQueriesLoading } = useQuery({
    queryKey: ['visualization-queries'],
    queryFn: () => apiClient.getQueryLogs(50).then(logs => 
      logs.filter(log => log.query_type === 'sql' && log.status === 'success')
    ),
  });

  // Re-execute selected query to get fresh data for visualization
  const { mutate: reExecuteQuery, data: queryResultData, isPending: isReExecuting } = useMutation({
    mutationFn: ({ query, connectionId }: { query: string; connectionId: string }) =>
      apiClient.executeSqlQuery(query, connectionId),
    onSuccess: () => {
      toast({
        title: 'Query Re-executed',
        description: 'Data loaded for visualization.',
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

  // Get selected query details
  const selectedQuery = sqlQueries?.find(q => q.id.toString() === selectedQueryId);

  // Handle query selection and re-execution
  const handleQuerySelect = (queryId: string) => {
    setSelectedQueryId(queryId);
    const query = sqlQueries?.find(q => q.id.toString() === queryId);
    if (query && selectedConnectionId) {
      reExecuteQuery({ query: query.query_text, connectionId: selectedConnectionId });
    }
  };

  // Process query results for chart visualization
  const chartData = useMemo(() => {
    if (!queryResultData || !queryResultData.success || !queryResultData.data || queryResultData.data.length === 0) {
      return null;
    }

    const results = queryResultData.data;
    const columns = queryResultData.columns || [];

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
  }, [queryResultData, chartType]);

  // Process overall analytics data
  const processQueryTypeData = () => {
    if (!queryLogs) return null;
    
    const sqlCount = queryLogs.filter(log => log.query_type === 'sql').length;
    const llmCount = queryLogs.filter(log => log.query_type === 'llm').length;
    
    return {
      labels: ['SQL Queries', 'LLM Queries'],
      datasets: [{
        data: [sqlCount, llmCount],
        backgroundColor: ['hsl(var(--primary))', 'hsl(var(--accent))'],
        borderColor: ['hsl(var(--primary))', 'hsl(var(--accent))'],
        borderWidth: 1,
      }]
    };
  };

  const processExecutionTimeData = () => {
    if (!queryLogs) return null;
    
    const timeRanges = {
      '0-100ms': 0,
      '100-500ms': 0,
      '500ms-1s': 0,
      '1s-5s': 0,
      '5s+': 0
    };
    
    queryLogs.forEach(log => {
      const time = log.execution_time_ms || 0;
      if (time <= 100) timeRanges['0-100ms']++;
      else if (time <= 500) timeRanges['100-500ms']++;
      else if (time <= 1000) timeRanges['500ms-1s']++;
      else if (time <= 5000) timeRanges['1s-5s']++;
      else timeRanges['5s+']++;
    });
    
    return {
      labels: Object.keys(timeRanges),
      datasets: [{
        label: 'Query Count',
        data: Object.values(timeRanges),
        backgroundColor: 'hsla(var(--primary), 0.6)',
        borderColor: 'hsl(var(--primary))',
        borderWidth: 1,
      }]
    };
  };

  const processActivityTimelineData = () => {
    if (!queryLogs) return null;
    
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (6 - i));
      return date.toISOString().split('T')[0];
    });
    
    const activityData = last7Days.map(date => {
      return queryLogs.filter(log => 
        log.created_at.startsWith(date)
      ).length;
    });
    
    return {
      labels: last7Days.map(date => new Date(date).toLocaleDateString('en-US', { weekday: 'short' })),
      datasets: [{
        label: 'Queries per Day',
        data: activityData,
        fill: true,
        backgroundColor: 'hsla(var(--accent), 0.2)',
        borderColor: 'hsl(var(--accent))',
        tension: 0.4,
        pointBackgroundColor: 'hsl(var(--accent))',
        pointBorderColor: 'hsl(var(--background))',
        pointBorderWidth: 2,
      }]
    };
  };

  const processSuccessRateData = () => {
    if (!queryLogs) return null;
    
    const successCount = queryLogs.filter(log => log.status === 'success').length;
    const errorCount = queryLogs.filter(log => log.status === 'error').length;
    
    return {
      labels: ['Successful', 'Failed'],
      datasets: [{
        data: [successCount, errorCount],
        backgroundColor: ['hsl(var(--success))', 'hsl(var(--destructive))'],
        borderColor: ['hsl(var(--success))', 'hsl(var(--destructive))'],
        borderWidth: 1,
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: selectedQuery ? `Visualization: ${selectedQuery.query_text.substring(0, 50)}...` : 'Query Results Visualization'
      }
    },
    scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
      y: {
        beginAtZero: true,
      },
    } : undefined,
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  const queryTypeData = processQueryTypeData();
  const executionTimeData = processExecutionTimeData();
  const activityTimelineData = processActivityTimelineData();
  const successRateData = processSuccessRateData();

  return (
    <div className="space-y-6">
      {/* Query Visualization Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Custom Query Visualizations
          </CardTitle>
          <CardDescription>
            Select any SQL query from your history to create custom visualizations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Query and Connection Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Database Connection</label>
              <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select connection" />
                </SelectTrigger>
                <SelectContent>
                  {connectionsLoading ? (
                    <SelectItem value="loading" disabled>Loading...</SelectItem>
                  ) : connections?.map((connection) => (
                    <SelectItem key={connection.id} value={connection.id}>
                      {connection.name} ({connection.database_type})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">SQL Query</label>
              <Select value={selectedQueryId} onValueChange={handleQuerySelect} disabled={!selectedConnectionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select query to visualize" />
                </SelectTrigger>
                <SelectContent>
                  {sqlQueriesLoading ? (
                    <SelectItem value="loading" disabled>Loading queries...</SelectItem>
                  ) : sqlQueries?.map((query) => (
                    <SelectItem key={query.id} value={query.id.toString()}>
                      <div className="flex flex-col">
                        <span className="font-mono text-sm truncate max-w-[300px]">
                          {query.query_text}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(query.created_at), { addSuffix: true })}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Chart Type</label>
              <Select value={chartType} onValueChange={(value: any) => setChartType(value)} disabled={!chartData}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bar">Bar Chart</SelectItem>
                  <SelectItem value="line">Line Chart</SelectItem>
                  <SelectItem value="pie">Pie Chart</SelectItem>
                  <SelectItem value="doughnut">Doughnut Chart</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Re-execute Button */}
          {selectedQuery && selectedConnectionId && (
            <Button 
              onClick={() => reExecuteQuery({ query: selectedQuery.query_text, connectionId: selectedConnectionId })}
              disabled={isReExecuting}
              className="w-full"
            >
              {isReExecuting ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              {isReExecuting ? 'Loading Data...' : 'Generate Visualization'}
            </Button>
          )}

          {/* Visualization Display */}
          {isReExecuting && (
            <div className="h-[400px] flex items-center justify-center">
              <Skeleton className="h-full w-full" />
            </div>
          )}

          {queryResultData && chartData && !isReExecuting && (
            <div className="space-y-4">
              <div className="h-[400px] w-full border rounded-lg p-4">
                {chartType === 'bar' && <Bar data={chartData} options={chartOptions} />}
                {chartType === 'line' && <Line data={chartData} options={chartOptions} />}
                {chartType === 'pie' && <Pie data={chartData} options={chartOptions} />}
                {chartType === 'doughnut' && <Doughnut data={chartData} options={chartOptions} />}
              </div>
              
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <div>
                  <p>Data from: {queryResultData.row_count} rows</p>
                  <p>Columns: {queryResultData.columns?.join(', ')}</p>
                </div>
                <Badge variant="outline">
                  <Clock className="h-3 w-3 mr-1" />
                  {queryResultData.execution_time_ms}ms
                </Badge>
              </div>
            </div>
          )}

          {queryResultData && !chartData && !isReExecuting && (
            <div className="text-center py-12 text-muted-foreground border rounded-lg">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="font-medium">No numeric data for visualization</p>
              <p className="text-sm">This query doesn't contain numeric columns suitable for charting.</p>
              <p className="text-sm">Try selecting a query with numeric data (sales, counts, amounts, etc.)</p>
            </div>
          )}

          {!selectedQuery && !isReExecuting && (
            <div className="text-center py-12 text-muted-foreground border rounded-lg">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="font-medium">Select a query to visualize</p>
              <p className="text-sm">Choose a database connection and SQL query from your history to create custom charts.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Analytics Overview Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Query Analytics Overview
          </CardTitle>
          <CardDescription>
            Overall analytics and insights from your database queries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <Database className="h-8 w-8 text-primary" />
              <div>
                <p className="text-2xl font-bold">{queryLogs?.length || 0}</p>
                <p className="text-sm text-muted-foreground">Total Queries</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <TrendingUp className="h-8 w-8 text-accent" />
              <div>
                <p className="text-2xl font-bold">
                  {queryLogs?.filter(log => log.status === 'success').length || 0}
                </p>
                <p className="text-sm text-muted-foreground">Successful</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <Clock className="h-8 w-8 text-orange-500" />
              <div>
                <p className="text-2xl font-bold">
                  {queryLogs && queryLogs.length > 0 
                    ? Math.round(queryLogs.reduce((sum, log) => sum + (log.execution_time_ms || 0), 0) / queryLogs.length)
                    : 0}ms
                </p>
                <p className="text-sm text-muted-foreground">Avg. Time</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
              <Activity className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-2xl font-bold">
                  {queryLogs ? Math.round((queryLogs.filter(log => log.status === 'success').length / queryLogs.length) * 100) : 0}%
                </p>
                <p className="text-sm text-muted-foreground">Success Rate</p>
              </div>
            </div>
          </div>

          {/* Analytics Charts Grid */}
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Query Type Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  {logsLoading ? (
                    <Skeleton className="h-full w-full" />
                  ) : queryTypeData ? (
                    <Doughnut data={queryTypeData} options={doughnutOptions} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      No data available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Query Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  {logsLoading ? (
                    <Skeleton className="h-full w-full" />
                  ) : successRateData ? (
                    <Doughnut data={successRateData} options={doughnutOptions} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      No data available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Execution Time Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  {logsLoading ? (
                    <Skeleton className="h-full w-full" />
                  ) : executionTimeData ? (
                    <Bar data={executionTimeData} options={chartOptions} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      No data available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>7-Day Activity Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[250px]">
                  {logsLoading ? (
                    <Skeleton className="h-full w-full" />
                  ) : activityTimelineData ? (
                    <Line data={activityTimelineData} options={chartOptions} />
                  ) : (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      No data available
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}