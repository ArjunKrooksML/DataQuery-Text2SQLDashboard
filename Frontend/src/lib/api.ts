import { getToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1_URL = `${API_BASE_URL}/api/v1`;

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
}

export interface SqlQueryRequest {
  query: string;
  query_type: 'sql';
  connection_id: string;
}

export interface SqlQueryResponse {
  success: boolean;
  data?: any[];
  message?: string;
  execution_time_ms?: number;
  columns?: string[];
  row_count?: number;
}

export interface LlmQueryRequest {
  prompt: string;
  include_schema?: boolean;
  include_sample_data?: boolean;
}

export interface LlmQueryResponse {
  response: string;
  sql_generated?: string;
  confidence_score?: number;
  execution_time_ms?: number;
}

export interface QueryLog {
  id: number;
  query_type: 'sql' | 'llm';
  query_text: string;
  status: string;
  execution_time_ms?: number;
  created_at: string;
  user_id?: number;
}

// Database Connection Interfaces
export interface DatabaseConnection {
  id: string;
  name: string;
  database_type: string;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  is_active: boolean;
  last_connected_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ConnectionCreate {
  name: string;
  database_type: string;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  password?: string;
}

export interface ConnectionUpdate {
  name?: string;
  database_type?: string;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  password?: string;
  is_active?: boolean;
}

export interface ConnectionTestResponse {
  success: boolean;
  message: string;
  error: string;
}

export interface SchemaResponse {
  connection_id: string;
  schema_data: any;
  success: boolean;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_V1_URL}${endpoint}`;
    
    // Get auth token
    const token = getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    // Add authorization header if token exists
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Merge with any additional headers from options
    if (options.headers) {
      Object.assign(headers, options.headers);
    }
    
    const config: RequestInit = {
      headers,
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // SQL Query
  async executeSqlQuery(query: string, connectionId: string): Promise<SqlQueryResponse> {
    return this.request<SqlQueryResponse>(`/queries/sql?connection_id=${connectionId}`, {
      method: 'POST',
      body: JSON.stringify({
        query,
        query_type: 'sql' as const,
      }),
    });
  }

  // LLM Query
  async executeLlmQuery(prompt: string, connectionId: string): Promise<LlmQueryResponse> {
    return this.request<LlmQueryResponse>(`/queries/llm?connection_id=${connectionId}`, {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        include_schema: true,
        include_sample_data: true,
      }),
    });
  }

  // Get Query Logs
  async getQueryLogs(limit: number = 50): Promise<QueryLog[]> {
    return this.request<QueryLog[]>(`/queries/logs?limit=${limit}`, {
      method: 'GET',
    });
  }

  // Delete All Query History
  async deleteQueryHistory(): Promise<{ message: string; deleted_count: number }> {
    return this.request<{ message: string; deleted_count: number }>('/queries/logs', {
      method: 'DELETE',
    });
  }

  // Delete Single Query Log
  async deleteSingleQueryLog(logId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/queries/logs/${logId}`, {
      method: 'DELETE',
    });
  }

  // Get Database Schema
  async getDatabaseSchema(connectionId: string): Promise<any[]> {
    return this.request<any[]>(`/queries/schema?connection_id=${connectionId}`, {
      method: 'GET',
    });
  }

  // Get Sample Data
  async getSampleData(tableName: string, connectionId: string, limit: number = 5): Promise<any[]> {
    return this.request<any[]>(`/queries/sample-data/${tableName}?connection_id=${connectionId}&limit=${limit}`, {
      method: 'GET',
    });
  }

  // Database Connection Management
  async getConnections(): Promise<DatabaseConnection[]> {
    return this.request<DatabaseConnection[]>('/connections', {
      method: 'GET',
    });
  }

  async createConnection(connectionData: ConnectionCreate): Promise<DatabaseConnection> {
    return this.request<DatabaseConnection>('/connections', {
      method: 'POST',
      body: JSON.stringify(connectionData),
    });
  }

  async getConnection(connectionId: string): Promise<DatabaseConnection> {
    return this.request<DatabaseConnection>(`/connections/${connectionId}`, {
      method: 'GET',
    });
  }

  async updateConnection(connectionId: string, updateData: ConnectionUpdate): Promise<DatabaseConnection> {
    return this.request<DatabaseConnection>(`/connections/${connectionId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async deleteConnection(connectionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/connections/${connectionId}`, {
      method: 'DELETE',
    });
  }

  async testConnection(connectionId: string): Promise<ConnectionTestResponse> {
    return this.request<ConnectionTestResponse>(`/connections/${connectionId}/test`, {
      method: 'POST',
    });
  }

  async getConnectionSchema(connectionId: string): Promise<SchemaResponse> {
    return this.request<SchemaResponse>(`/connections/${connectionId}/schema`, {
      method: 'GET',
    });
  }

  // Authentication
  async login(email: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append('username', email); // Backend expects 'username' field but we pass email
    formData.append('password', password);

    return this.request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email, // Backend expects 'username' field but we pass email
        password,
      }),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    company_name?: string;
  }): Promise<any> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }
}

export const apiClient = new ApiClient();

// Debug: Ensure apiClient is properly exported
console.log('ApiClient initialized:', apiClient); 