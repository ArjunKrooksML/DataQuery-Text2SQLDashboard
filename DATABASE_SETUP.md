# Database Setup Guide

This guide will help you set up the new database schema for the DataWise application.

## 🗄️ **Database Requirements**

### **PostgreSQL Setup**
- PostgreSQL 12+ (recommended: PostgreSQL 14+)
- UUID extension enabled
- JSONB support (usually available by default)

## 🚀 **Step-by-Step Setup**

### **Step 1: Create PostgreSQL Database**

#### **Option A: Using Docker (Recommended)**
```bash
# Start PostgreSQL container
docker run --name postgres-datadashboard \
  -e POSTGRES_DB=datadashboard \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:15
```

#### **Option B: Local PostgreSQL Installation**
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Run the database creation script
\i Backend/scripts/create_database.sql
```

### **Step 2: Configure Environment Variables**

Create or update your `.env` file in the Backend directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/datadashboard
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/datadashboard

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Application Settings
DEBUG=True
ENVIRONMENT=development
```

### **Step 3: Install Dependencies**

```bash
cd Backend
pip install -r requirements.txt
```

### **Step 4: Run Database Setup Script**

```bash
# Navigate to Backend directory
cd Backend

# Run the new database setup script
python scripts/setup_new_database.py
```

This script will:
- ✅ Create all new tables with UUID primary keys
- ✅ Create sample data tables (sales_data, orders, customers)
- ✅ Create a sample user (admin@datadashboard.com / admin123)
- ✅ Create a sample database connection
- ✅ Create sample query history

### **Step 5: Verify Setup**

#### **Check Database Tables**
```bash
# Connect to PostgreSQL
psql -U postgres -d datadashboard

# List all tables
\dt

# Check users table
SELECT * FROM users;

# Check database_connections table
SELECT * FROM database_connections;

# Check query_history table
SELECT * FROM query_history;
```

#### **Expected Tables**
```
users                    # User accounts with UUID primary keys
database_connections     # Database connection configurations
query_history           # Query execution history
query_cache             # Cached query results
user_sessions           # User authentication sessions
sales_data              # Sample sales data
orders                  # Sample orders data
customers               # Sample customers data
```

## 🔧 **Database Schema Overview**

### **Core Tables (New Schema)**

#### **1. users**
```sql
- id: UUID PRIMARY KEY
- email: VARCHAR(255) UNIQUE
- password_hash: VARCHAR(255)
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- company_name: VARCHAR(255)
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### **2. database_connections**
```sql
- id: UUID PRIMARY KEY
- user_id: UUID (Foreign Key to users)
- name: VARCHAR(255)
- database_type: VARCHAR(50)
- host: VARCHAR(255)
- port: INTEGER
- database_name: VARCHAR(255)
- username: VARCHAR(255)
- password_encrypted: TEXT
- connection_string_encrypted: TEXT
- schema_json: JSONB
- is_active: BOOLEAN
- last_connected_at: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### **3. query_history**
```sql
- id: UUID PRIMARY KEY
- user_id: UUID (Foreign Key to users)
- database_connection_id: UUID (Foreign Key to database_connections)
- natural_language_query: TEXT
- generated_sql_query: TEXT
- execution_time_ms: INTEGER
- row_count: INTEGER
- status: VARCHAR(20)
- error_message: TEXT
- result_hash: VARCHAR(64)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### **4. query_cache**
```sql
- id: UUID PRIMARY KEY
- result_hash: VARCHAR(64) UNIQUE
- database_connection_id: UUID (Foreign Key to database_connections)
- sql_query: TEXT
- result_data: JSONB
- expires_at: TIMESTAMP
- created_at: TIMESTAMP
```

#### **5. user_sessions**
```sql
- id: UUID PRIMARY KEY
- user_id: UUID (Foreign Key to users)
- token_hash: VARCHAR(255)
- expires_at: TIMESTAMP
- created_at: TIMESTAMP
```

## 🧪 **Testing the Setup**

### **1. Test Database Connection**
```bash
cd Backend
python -c "
from app.database.connection import get_db
from app.models import User
db = next(get_db())
users = db.query(User).all()
print(f'Found {len(users)} users')
"
```

### **2. Test API Endpoints**
```bash
# Start the backend
cd Backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test login endpoint
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@datadashboard.com&password=admin123"
```

### **3. Test Frontend Integration**
```bash
# Start the frontend
cd Frontend
npm run dev

# Visit: http://localhost:9002
# Login with: admin@datadashboard.com / admin123
```

## 🔒 **Security Considerations**

### **1. Database Credentials**
- ✅ Passwords are stored encrypted (AES encryption)
- ✅ Connection strings are encrypted
- ✅ No plain text credentials in database

### **2. User Sessions**
- ✅ Session tokens are hashed
- ✅ Automatic session expiration
- ✅ Cascade deletion on user removal

### **3. Query History**
- ✅ User-specific query isolation
- ✅ Database connection tracking
- ✅ Execution time and row count logging

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. UUID Extension Error**
```bash
# Solution: Enable UUID extension
psql -U postgres -d datadashboard -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

#### **2. Connection Refused**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Or for local installation
sudo systemctl status postgresql
```

#### **3. Permission Denied**
```bash
# Check database permissions
psql -U postgres -d datadashboard -c "\du"
```

#### **4. Import Errors**
```bash
# Make sure you're in the Backend directory
cd Backend

# Install dependencies
pip install -r requirements.txt

# Check Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## ✅ **Verification Checklist**

- [ ] PostgreSQL database created
- [ ] UUID extension enabled
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Database setup script executed
- [ ] Sample data created
- [ ] API endpoints responding
- [ ] Frontend can connect to backend
- [ ] User can login successfully

## 🎯 **Next Steps**

After successful database setup:

1. **Implement Multi-tenant Features**: Add tenant isolation
2. **Add Database Connection Management**: Create connection CRUD operations
3. **Implement Schema Masking**: Add security for sensitive data
4. **Create Agentic AI**: Implement specialized AI agents
5. **Add Dashboard APIs**: Create chart and visualization endpoints

Your database is now ready for the enhanced DataWise application! 🚀 