# DataWise Architecture

## 🏗️ **Improved Architecture (No Duplicate Database Connections)**

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │
│   Port: 9002    │
└─────────┬───────┘
          │
          │ HTTP Requests
          ▼
┌─────────────────┐    ┌─────────────────┐
│   Backend       │    │   MCP Server    │
│   (FastAPI)     │◄──►│   (Port 8001)   │
│   Port: 8000    │    │                 │
│   ├─ API        │    │   ├─ Context    │
│   ├─ Auth       │    │   ├─ Schema     │
│   └─ Database   │    │   └─ Analysis   │
└─────────┬───────┘    └─────────────────┘
          │
          │ Single Database Connection
          ▼
┌─────────────────┐
│   PostgreSQL    │
│   Port: 5432    │
└─────────────────┘
```

## 🔄 **How It Works**

### **1. Single Database Connection**
- ✅ **Only the main backend** connects to PostgreSQL
- ✅ **MCP server** communicates with backend via HTTP API
- ✅ **No duplicate connections** or connection pools
- ✅ **Better resource utilization**

### **2. Communication Flow**

#### **Frontend → Backend (Direct)**
```
Frontend → Backend API → Database
```

#### **Frontend → MCP Server → Backend**
```
Frontend → MCP Server → Backend API → Database
```

### **3. API Endpoints**

#### **Main Backend (Port 8000)**
- `POST /api/v1/queries/sql` - Execute SQL
- `POST /api/v1/queries/llm` - Execute LLM queries
- `GET /api/v1/queries/schema` - Get database schema
- `GET /api/v1/queries/sample-data/{table}` - Get sample data
- `GET /api/v1/queries/logs` - Get query logs

#### **MCP Server (Port 8001)**
- `POST /mcp/context` - Get database context for prompts
- `GET /mcp/schema` - Get schema (via backend)
- `GET /mcp/sample-data/{table}` - Get sample data (via backend)
- `GET /health` - Health check

## 🚀 **Benefits of This Approach**

### **Resource Efficiency**
- ✅ **Single database connection** from main backend
- ✅ **No connection pool duplication**
- ✅ **Lower memory usage**
- ✅ **Better performance**

### **Scalability**
- ✅ **MCP server can scale independently**
- ✅ **Backend can scale independently**
- ✅ **Database connection managed centrally**

### **Maintenance**
- ✅ **Single source of truth** for database operations
- ✅ **Easier to manage database migrations**
- ✅ **Centralized error handling**

### **Security**
- ✅ **Database credentials** only in main backend
- ✅ **Network isolation** between services
- ✅ **API-level access control**

## 🔧 **Docker Compose Services**

```yaml
services:
  # Database (Single Instance)
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: datadashboard
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  # Main Backend (Database Access)
  backend:
    build: ./Backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/datadashboard
      # ... other env vars
    depends_on:
      - postgres

  # MCP Server (No Database Access)
  mcp-server:
    build: ./Backend
    environment:
      BACKEND_URL: http://backend:8000  # Communicates with backend
      # No DATABASE_URL needed!
    depends_on:
      - backend  # Waits for backend, not database
```

## 📊 **Request Flow Examples**

### **Example 1: SQL Query**
```
1. Frontend → Backend: POST /api/v1/queries/sql
2. Backend → Database: Execute SQL
3. Backend → Frontend: Return results
```

### **Example 2: LLM Query with MCP**
```
1. Frontend → MCP Server: POST /mcp/context
2. MCP Server → Backend: GET /api/v1/queries/schema
3. Backend → Database: Get schema
4. Backend → MCP Server: Return schema
5. MCP Server → Backend: GET /api/v1/queries/sample-data/sales_data
6. Backend → Database: Get sample data
7. Backend → MCP Server: Return sample data
8. MCP Server → Frontend: Return context + SQL suggestion
```

## 🎯 **Why This is Better**

### **Before (Duplicate Connections)**
```
❌ Backend → Database
❌ MCP Server → Database (Duplicate!)
❌ Wasted resources
❌ Connection limits
❌ Complex configuration
```

### **After (Single Connection)**
```
✅ Backend → Database (Only connection)
✅ MCP Server → Backend API (HTTP calls)
✅ Efficient resource usage
✅ Better scalability
✅ Simpler architecture
```

## 🔄 **Alternative: Integrated MCP**

If you prefer even simpler architecture, you can keep MCP integrated:

```python
# In Backend/app/services/llm_service.py
class LLMService:
    def get_database_context(self, prompt: str):
        # Direct database access (no separate server)
        schema = self.database_service.get_database_schema()
        # ... rest of MCP logic
```

## 🚀 **Deployment Options**

### **Option 1: Separate MCP Server (Current)**
```bash
docker-compose up backend mcp-server
```

### **Option 2: Integrated MCP (Simpler)**
```bash
docker-compose up backend  # MCP functionality built-in
```

### **Option 3: Both (Flexible)**
```bash
docker-compose up  # All services
```

## 📈 **Performance Comparison**

| Metric | **Integrated MCP** | **Separate MCP** |
|--------|-------------------|------------------|
| **Latency** | Lower (direct calls) | Higher (HTTP calls) |
| **Resource Usage** | Lower | Higher |
| **Scalability** | Limited | Independent |
| **Complexity** | Simple | Moderate |
| **Database Connections** | 1 | 1 (via backend) |

## 🎯 **Recommendation**

For your current use case, I recommend the **separate MCP server** approach because:

1. ✅ **Clean separation of concerns**
2. ✅ **Independent scaling**
3. ✅ **Single database connection**
4. ✅ **Better maintainability**
5. ✅ **Future-proof architecture**

The architecture now properly avoids duplicate database connections while maintaining the benefits of a separate MCP service! 