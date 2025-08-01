# Multi-Tenant Database Architecture

## 🏗️ **Architecture Overview**

### **Two-Tier Database System**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM DATABASE                           │
│  (PostgreSQL - Contains user management & configurations)      │
├─────────────────────────────────────────────────────────────────┤
│ • users                    # User accounts & authentication    │
│ • database_connections     # Client DB configurations         │
│ • query_history           # Query execution logs              │
│ • query_cache             # Cached query results              │
│ • user_sessions           # Authentication sessions           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ (Dynamic Connection)
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT DATABASES                            │
│  (Various databases - Customer data & business logic)         │
├─────────────────────────────────────────────────────────────────┤
│ Client 1 Database:                                            │
│ • sales_data              # Customer 1's sales data          │
│ • orders                  # Customer 1's orders              │
│ • customers               # Customer 1's customers           │
│                                                              │
│ Client 2 Database:                                            │
│ • inventory               # Customer 2's inventory           │
│ • products                # Customer 2's products            │
│ • suppliers               # Customer 2's suppliers           │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 **Security & Isolation**

### **Tenant Isolation Rules**
```
Client 1 ──► Can only access Client_Database_1
Client 2 ──► Can only access Client_Database_2
Client 3 ──► Can only access Client_Database_3
```

### **Access Control Matrix**
| User | Platform DB | Client DB 1 | Client DB 2 | Client DB 3 |
|------|-------------|-------------|-------------|-------------|
| Client 1 User | ✅ Read/Write | ✅ Read/Write | ❌ No Access | ❌ No Access |
| Client 2 User | ✅ Read/Write | ❌ No Access | ✅ Read/Write | ❌ No Access |
| Client 3 User | ✅ Read/Write | ❌ No Access | ❌ No Access | ✅ Read/Write |

## 🗄️ **Database Structure**

### **Platform Database (PostgreSQL)**
```sql
-- User Management
users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Client Database Configurations
database_connections (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),
    database_type VARCHAR(50),  -- postgresql, mysql, sqlite, etc.
    host VARCHAR(255),          -- Client DB IP address
    port INTEGER,               -- Client DB port
    database_name VARCHAR(255), -- Client DB name
    username VARCHAR(255),      -- Client DB username
    password_encrypted TEXT,    -- AES encrypted password
    connection_string_encrypted TEXT,
    schema_json JSONB,         -- Cached schema
    is_active BOOLEAN,
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Query History (Platform-level logging)
query_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    database_connection_id UUID REFERENCES database_connections(id),
    natural_language_query TEXT,
    generated_sql_query TEXT,
    execution_time_ms INTEGER,
    row_count INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    result_hash VARCHAR(64),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### **Client Databases (Various Types)**
```sql
-- Example: Client 1 Database (PostgreSQL)
sales_data (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    region VARCHAR(50),
    sales_amount DECIMAL(10,2),
    sales_date DATE
)

-- Example: Client 2 Database (MySQL)
inventory (
    id INT PRIMARY KEY,
    product_name VARCHAR(100),
    quantity INT,
    warehouse VARCHAR(50),
    last_updated TIMESTAMP
)
```

## 🔧 **Implementation Details**

### **1. Dynamic Database Connection Management**

```python
class DatabaseConnectionService:
    def get_client_connection(self, user_id: UUID, connection_id: UUID):
        """Get client database connection for specific user"""
        connection = self.get_connection_config(connection_id)
        
        # Verify user has access to this connection
        if not self.user_has_access(user_id, connection_id):
            raise AccessDeniedError("User cannot access this database")
        
        # Create dynamic connection to client database
        return self.create_dynamic_connection(connection)
    
    def create_dynamic_connection(self, connection_config):
        """Create connection to client database"""
        if connection_config.database_type == "postgresql":
            return create_postgresql_connection(connection_config)
        elif connection_config.database_type == "mysql":
            return create_mysql_connection(connection_config)
        elif connection_config.database_type == "sqlite":
            return create_sqlite_connection(connection_config)
```

### **2. Multi-Tenant Query Execution**

```python
class MultiTenantQueryService:
    def execute_query(self, user_id: UUID, connection_id: UUID, query: str):
        """Execute query on client database with tenant isolation"""
        
        # 1. Get user's database connection
        connection = self.db_service.get_client_connection(user_id, connection_id)
        
        # 2. Execute query on client database
        result = connection.execute(query)
        
        # 3. Log query in platform database
        self.log_query(user_id, connection_id, query, result)
        
        return result
```

### **3. Schema Detection & Caching**

```python
class SchemaDetectionService:
    def detect_client_schema(self, connection_id: UUID):
        """Detect and cache client database schema"""
        connection = self.get_connection(connection_id)
        
        # Detect tables, columns, relationships
        schema = self.analyze_database_schema(connection)
        
        # Cache schema in platform database
        self.cache_schema(connection_id, schema)
        
        return schema
```

## 🚀 **Setup Examples**

### **Example 1: Client 1 (E-commerce)**
```python
# Platform Database Configuration
client1_connection = DatabaseConnection(
    user_id=client1_user_id,
    name="E-commerce Database",
    database_type="postgresql",
    host="192.168.1.100",
    port=5432,
    database_name="ecommerce_db",
    username="ecommerce_user",
    password_encrypted="encrypted_password_here"
)

# Client 1 Database Tables
# - products
# - orders
# - customers
# - inventory
```

### **Example 2: Client 2 (Manufacturing)**
```python
# Platform Database Configuration
client2_connection = DatabaseConnection(
    user_id=client2_user_id,
    name="Manufacturing Database",
    database_type="mysql",
    host="192.168.1.101",
    port=3306,
    database_name="manufacturing_db",
    username="manufacturing_user",
    password_encrypted="encrypted_password_here"
)

# Client 2 Database Tables
# - production_lines
# - quality_metrics
# - suppliers
# - raw_materials
```

## 🔒 **Security Implementation**

### **1. Connection Encryption**
```python
class EncryptionService:
    def encrypt_database_password(self, password: str) -> str:
        """Encrypt database password using AES"""
        key = settings.ENCRYPTION_KEY
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    
    def decrypt_database_password(self, encrypted_password: str) -> str:
        """Decrypt database password"""
        key = settings.ENCRYPTION_KEY
        data = base64.b64decode(encrypted_password.encode())
        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()
```

### **2. Access Control**
```python
class AccessControlService:
    def user_has_access(self, user_id: UUID, connection_id: UUID) -> bool:
        """Check if user has access to specific database connection"""
        connection = self.get_connection(connection_id)
        return connection.user_id == user_id
    
    def filter_queries_by_user(self, user_id: UUID, queries: List[QueryHistory]):
        """Filter query history by user access"""
        return [q for q in queries if q.user_id == user_id]
```

## 📊 **API Endpoints**

### **Platform Database APIs**
```python
# User Management
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/users/profile

# Database Connection Management
GET    /api/v1/connections
POST   /api/v1/connections
PUT    /api/v1/connections/{connection_id}
DELETE /api/v1/connections/{connection_id}
POST   /api/v1/connections/{connection_id}/test

# Query History
GET /api/v1/queries/history
GET /api/v1/queries/history/{query_id}
```

### **Client Database APIs**
```python
# Query Execution (with tenant isolation)
POST /api/v1/queries/sql
POST /api/v1/queries/llm
GET  /api/v1/queries/schema
GET  /api/v1/queries/sample-data/{table}

# Dashboard Data
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/charts
GET /api/v1/dashboard/analytics
```

## 🎯 **Benefits of This Architecture**

### **✅ Security**
- Complete tenant isolation
- Encrypted database credentials
- User-specific access control
- Audit trail for all queries

### **✅ Scalability**
- Support for multiple database types
- Dynamic connection management
- Cached schema information
- Performance optimization

### **✅ Flexibility**
- Any database type (PostgreSQL, MySQL, SQLite, etc.)
- Custom connection configurations
- Schema auto-detection
- Multi-tenant dashboard

### **✅ Management**
- Centralized user management
- Connection health monitoring
- Query performance tracking
- Usage analytics

## 🔄 **Workflow Example**

### **Client 1 User Workflow**
1. **Login**: User authenticates via Platform Database
2. **Select Database**: User chooses their Client Database connection
3. **Query**: User writes natural language query
4. **Execution**: System connects to Client Database 1 dynamically
5. **Results**: Query results returned to user
6. **Logging**: Query logged in Platform Database

### **Client 2 User Workflow**
1. **Login**: Same Platform Database, different user
2. **Select Database**: User chooses their Client Database connection
3. **Query**: User writes natural language query
4. **Execution**: System connects to Client Database 2 dynamically
5. **Results**: Query results returned to user
6. **Logging**: Query logged in Platform Database

This architecture ensures complete isolation between clients while providing a unified interface for all users! 🚀 