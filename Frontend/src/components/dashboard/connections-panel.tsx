'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '../ui/skeleton';
import { Plus, Database, TestTube, Edit, Trash2, Eye } from 'lucide-react';
import { apiClient, DatabaseConnection, ConnectionCreate, ConnectionUpdate } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function ConnectionsPanel() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState<DatabaseConnection | null>(null);
  const [formData, setFormData] = useState<ConnectionCreate>({
    name: 'PostgreSQL Connection', // Default name
    database_type: 'postgresql', // Fixed to PostgreSQL
    host: '',
    port: 5432,
    database_name: '',
    username: '',
    password: '',
  });
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch connections
  const { data: connections, isLoading, error } = useQuery({
    queryKey: ['connections'],
    queryFn: () => apiClient.getConnections(),
  });

  // Create connection mutation
  const createMutation = useMutation({
    mutationFn: (data: ConnectionCreate) => apiClient.createConnection(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      setIsCreateDialogOpen(false);
      setFormData({
        name: 'PostgreSQL Connection', // Default name
        database_type: 'postgresql', // Fixed to PostgreSQL
        host: '',
        port: 5432,
        database_name: '',
        username: '',
        password: '',
      });
      toast({
        title: 'Success',
        description: 'Database connection created successfully',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Update connection mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ConnectionUpdate }) =>
      apiClient.updateConnection(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      setIsEditDialogOpen(false);
      setSelectedConnection(null);
      toast({
        title: 'Success',
        description: 'Database connection updated successfully',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Delete connection mutation
  const deleteMutation = useMutation({
    mutationFn: (connectionId: string) => apiClient.deleteConnection(connectionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast({
        title: 'Success',
        description: 'Database connection deleted successfully',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: (connectionId: string) => apiClient.testConnection(connectionId),
    onSuccess: (data) => {
      if (data.success) {
        toast({
          title: 'Connection Test',
          description: 'Connection test successful!',
        });
      } else {
        toast({
          title: 'Connection Test',
          description: `Connection test failed: ${data.error}`,
          variant: 'destructive',
        });
      }
    },
    onError: (error) => {
      toast({
        title: 'Connection Test',
        description: error.message,
        variant: 'destructive',
      });
    },
  });

  const handleCreateConnection = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleUpdateConnection = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedConnection) {
      updateMutation.mutate({
        id: selectedConnection.id,
        data: formData as ConnectionUpdate,
      });
    }
  };

  const handleEditConnection = (connection: DatabaseConnection) => {
    setSelectedConnection(connection);
    setFormData({
      name: connection.name,
      database_type: connection.database_type,
      host: connection.host || '',
      port: connection.port || 5432,
      database_name: connection.database_name || '',
      username: connection.username || '',
      password: '',
    });
    setIsEditDialogOpen(true);
  };

  const handleDeleteConnection = (connectionId: string) => {
    if (confirm('Are you sure you want to delete this connection?')) {
      deleteMutation.mutate(connectionId);
    }
  };

  const handleTestConnection = (connectionId: string) => {
    testMutation.mutate(connectionId);
  };

  const getDatabaseTypeColor = (type: string) => {
    switch (type) {
      case 'postgresql':
        return 'bg-blue-100 text-blue-800';
      case 'mysql':
        return 'bg-orange-100 text-orange-800';
      case 'sqlite':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Database Connections</h2>
          <p className="text-muted-foreground">Manage your database connections</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Connection
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Add PostgreSQL Connection</DialogTitle>
              <DialogDescription>
                Add a new PostgreSQL database connection to your account.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleCreateConnection}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="host" className="text-right">
                    Host
                  </Label>
                  <Input
                    id="host"
                    value={formData.host}
                    onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="port" className="text-right">
                    Port
                  </Label>
                  <Input
                    id="port"
                    type="number"
                    value={formData.port}
                    onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="database_name" className="text-right">
                    Database
                  </Label>
                  <Input
                    id="database_name"
                    value={formData.database_name}
                    onChange={(e) => setFormData({ ...formData, database_name: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="username" className="text-right">
                    Username
                  </Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="password" className="text-right">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Connection'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Your Connections</CardTitle>
          <CardDescription>Manage your database connections</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          )}
          {error && <p className="text-destructive">Error loading connections: {error.message}</p>}
          {connections && connections.length === 0 && (
            <p className="text-muted-foreground">No database connections found. Create your first connection above.</p>
          )}
          {connections && connections.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Host</TableHead>
                  <TableHead>Database</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {connections.map((connection) => (
                  <TableRow key={connection.id}>
                    <TableCell className="font-medium">{connection.name}</TableCell>
                    <TableCell>
                      <Badge className={getDatabaseTypeColor(connection.database_type)}>
                        {connection.database_type}
                      </Badge>
                    </TableCell>
                    <TableCell>{connection.host}:{connection.port}</TableCell>
                    <TableCell>{connection.database_name}</TableCell>
                    <TableCell>
                      <Badge variant={connection.is_active ? 'default' : 'secondary'}>
                        {connection.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleTestConnection(connection.id)}
                          disabled={testMutation.isPending}
                        >
                          <TestTube className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditConnection(connection)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteConnection(connection.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Database Connection</DialogTitle>
            <DialogDescription>
              Update your database connection settings.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpdateConnection}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-name" className="text-right">
                  Name
                </Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-database_type" className="text-right">
                  Type
                </Label>
                <Select
                  value={formData.database_type}
                  onValueChange={(value) => setFormData({ ...formData, database_type: value })}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="postgresql">PostgreSQL</SelectItem>
                    <SelectItem value="mysql">MySQL</SelectItem>
                    <SelectItem value="sqlite">SQLite</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-host" className="text-right">
                  Host
                </Label>
                <Input
                  id="edit-host"
                  value={formData.host}
                  onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-port" className="text-right">
                  Port
                </Label>
                <Input
                  id="edit-port"
                  type="number"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-database_name" className="text-right">
                  Database
                </Label>
                <Input
                  id="edit-database_name"
                  value={formData.database_name}
                  onChange={(e) => setFormData({ ...formData, database_name: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-username" className="text-right">
                  Username
                </Label>
                <Input
                  id="edit-username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="edit-password" className="text-right">
                  Password
                </Label>
                <Input
                  id="edit-password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="col-span-3"
                  placeholder="Leave blank to keep current password"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Updating...' : 'Update Connection'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
} 