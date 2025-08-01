# Database Setup Guide

## 🗄️ **Overview**

This guide covers setting up all databases required for your DataWise application:

1. **PostgreSQL** - Platform Database (User management, configurations)
2. **MongoDB** - Session & Cache Database (Sessions, caching, rate limiting)
3. **Client Databases** - Sample data for testing

## 🚀 **Quick Setup (Docker)**

### **Option 1: All-in-One Setup**
```bash
# 1. Clone your repository
git clone <your-repo>
cd AI_POWERED_SQL_DASHBOARD

# 2. Create environment file
cp Backend/env.example Backend/.env
# Edit Backend/.env with your OpenAI API key

# 3. Start all services (includes all databases)
docker-compose up -d

# 4. Initialize PostgreSQL with sample data
docker-compose exec backend python scripts/setup_new_database.py

# 5. Create MongoDB indexes
docker-compose exec mongodb mongosh --eval "
use datadashboard_cache
db.sessions.createIndex({'session_id': 1})
db.sessions.createIndex({'user_id': 1})
db.sessions.createIndex({'expires_at': 1}, {expireAfterSeconds: 0})
db.cache.createIndex({'key': 1})
db.cache.createIndex({'expires_at': 1}, {expireAfterSeconds: 0})
db.rate_limits.createIndex({'user_id': 1, 'time_window': 1})
db.rate_limits.createIndex({'time_window': 1})
"
```

### **Option 2: Manual Setup**
```bash
# 1. Start databases only
docker-compose up postgres mongodb redis -d

# 2. Set up environment
cp Backend/env.example Backend/.env
# Edit Backend/.env

# 3. Initialize PostgreSQL
docker-compose exec backend python scripts/setup_new_database.py

# 4. Create MongoDB indexes
docker-compose exec mongodb mongosh --eval "
use datadashboard_cache
db.sessions.createIndex({'session_id': 1})
db.sessions.createIndex({'user_id': 1})
db.sessions.createIndex({'expires_at': 1}, {expireAfterSeconds: 0})
db.cache.createIndex({'key': 1})
db.cache.createIndex({'expires_at': 1}, {expireAfterSeconds: 0})
db.rate_limits.createIndex({'user_id': 1, 'time_window': 1})
db.rate_limits.createIndex({'time_window': 1})
"

# 5. Start application services
docker-compose up backend frontend -d
```

## 📋 **Detailed Setup Instructions**

### **1. PostgreSQL Setup (Platform Database)**

#### **Using Docker (Recommended)**
```bash
# Start PostgreSQL
docker-compose up postgres -d

# Check if PostgreSQL is running
docker-compose exec postgres psql -U postgres -d datadashboard -c "\dt"
```

#### **Using Local PostgreSQL**
```bash
# 1. Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/

# 2. Create database
sudo -u postgres psql
CREATE DATABASE datadashboard;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q

# 3. Update environment
# In Backend/.env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/datadashboard
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:your_password@localhost:5432/datadashboard
```

#### **Initialize PostgreSQL Schema**
```bash
# Run the setup script
cd Backend
python scripts/setup_new_database.py
```

This creates:
- ✅ **users** table (with sample admin user)
- ✅ **database_connections** table (with sample connection)
- ✅ **query_history** table
- ✅ **query_cache** table
- ✅ **user_sessions** table
- ✅ **sales_data**, **orders**, **customers** tables (sample data)

### **2. MongoDB Setup (Session & Cache Database)**

#### **Using Docker (Recommended)**
```bash
# Start MongoDB
docker-compose up mongodb -d

# Check if MongoDB is running
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"
```

#### **Using Local MongoDB**
```bash
# 1. Install MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb/brew/mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community

# 2. Start MongoDB service
sudo systemctl start mongodb

# 3. Create database and user
mongosh
use datadashboard_cache
db.createUser({
  user: "admin",
  pwd: "admin123",
  roles: ["readWrite"]
})
exit

# 4. Update environment
# In Backend/.env
MONGODB_URL=mongodb://admin:admin123@localhost:27017/datadashboard_cache?authSource=admin
MONGODB_DATABASE=datadashboard_cache
```

#### **Create MongoDB Indexes**
```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh

# Or if using local MongoDB
mongosh

# Create indexes for performance
use datadashboard_cache

# Sessions collection indexes
db.sessions.createIndex({"session_id": 1})
db.sessions.createIndex({"user_id": 1})
db.sessions.createIndex({"expires_at": 1}, {expireAfterSeconds: 0})

# Cache collection indexes
db.cache.createIndex({"key": 1})
db.cache.createIndex({"expires_at": 1}, {expireAfterSeconds: 0})

# Rate limits collection indexes
db.rate_limits.createIndex({"user_id": 1, "time_window": 1})
db.rate_limits.createIndex({"time_window": 1})

exit
```

### **3. Redis Setup (Optional - for additional caching)**

#### **Using Docker**
```bash
# Start Redis
docker-compose up redis -d

# Check if Redis is running
docker-compose exec redis redis-cli ping
```

#### **Using Local Redis**
```bash
# 1. Install Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# 2. Start Redis
sudo systemctl start redis-server

# 3. Test connection
redis-cli ping
```

### **4. Client Database Setup (Sample Data)**

#### **Create Sample Client Database**
```bash
# 1. Create a sample client database
docker-compose exec postgres psql -U postgres -c "
CREATE DATABASE client1_database;
CREATE DATABASE client2_database;
"

# 2. Add sample data to client databases
docker-compose exec postgres psql -U postgres -d client1_database -c "
CREATE TABLE sales_data (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    region VARCHAR(50),
    sales_amount DECIMAL(10,2),
    sales_date DATE
);

INSERT INTO sales_data (product_name, region, sales_amount, sales_date) VALUES
('Widget A', 'North', 1500.00, '2024-01-15'),
('Widget B', 'South', 2200.00, '2024-01-15'),
('Widget C', 'East', 1800.00, '2024-01-15'),
('Widget A', 'West', 1200.00, '2024-01-16'),
('Widget B', 'North', 2500.00, '2024-01-16');
"
```

## 🔧 **Environment Configuration**

### **Create Environment File**
```bash
# Copy example environment file
cp Backend/env.example Backend/.env

# Edit the file with your settings
nano Backend/.env
```

### **Required Environment Variables**
```bash
# Database URLs
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/datadashboard
DATABASE_URL_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/datadashboard

# MongoDB
MONGODB_URL=mongodb://admin:admin123@localhost:27017/datadashboard_cache?authSource=admin
MONGODB_DATABASE=datadashboard_cache

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Session and Cache Settings
SESSION_EXPIRE_MINUTES=60
CACHE_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## 🧪 **Verification Steps**

### **1. Check PostgreSQL**
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d datadashboard

# List tables
\dt

# Check sample data
SELECT * FROM users LIMIT 5;
SELECT * FROM sales_data LIMIT 5;

# Exit
\q
```

### **2. Check MongoDB**
```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh

# Switch to database
use datadashboard_cache

# List collections
show collections

# Check indexes
db.sessions.getIndexes()
db.cache.getIndexes()

# Exit
exit
```

### **3. Check Redis**
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test connection
ping

# Exit
exit
```

## 🚀 **Start Application**

### **Option 1: Using Docker Compose**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### **Option 2: Manual Start**
```bash
# 1. Start databases
docker-compose up postgres mongodb redis -d

# 2. Start backend
cd Backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (in new terminal)
cd Frontend
npm install
npm run dev
```

## 🔍 **Troubleshooting**

### **PostgreSQL Issues**
```bash
# Check if PostgreSQL is running
docker-compose exec postgres pg_isready

# Reset PostgreSQL data
docker-compose down
docker volume rm datadashboard_postgres_data
docker-compose up postgres -d
```

### **MongoDB Issues**
```bash
# Check if MongoDB is running
docker-compose exec mongodb mongosh --eval "db.runCommand('ping')"

# Reset MongoDB data
docker-compose down
docker volume rm datadashboard_mongodb_data
docker-compose up mongodb -d
```

### **Connection Issues**
```bash
# Check if all services are accessible
curl http://localhost:8000/health
curl http://localhost:9002

# Check database connections
docker-compose exec backend python -c "
from app.database.connection import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('PostgreSQL: OK')
"
```

## 📊 **Database Architecture Summary**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PLATFORM DATABASE                           │
│  (PostgreSQL - User management & configurations)               │
├─────────────────────────────────────────────────────────────────┤
│ • users                    # User accounts & authentication    │
│ • database_connections     # Client DB configurations         │
│ • query_history           # Query execution logs              │
│ • query_cache             # Cached query results              │
│ • user_sessions           # Authentication sessions           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION & CACHE DATABASE                    │
│  (MongoDB - Session storage & performance optimization)       │
├─────────────────────────────────────────────────────────────────┤
│ • sessions                # User session data                 │
│ • cache                   # Query & LLM response cache       │
│ • rate_limits             # Rate limiting data               │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT DATABASES                            │
│  (Various databases - Customer data & business logic)         │
├─────────────────────────────────────────────────────────────────┤
│ Client 1 Database:                                            │
│ • sales_data              # Customer 1's sales data          │
│ • orders                  # Customer 1's orders              │
│                                                              │
│ Client 2 Database:                                            │
│ • inventory               # Customer 2's inventory           │
│ • products                # Customer 2's products            │
└─────────────────────────────────────────────────────────────────┘
```

## ✅ **Setup Checklist**

- [ ] **PostgreSQL** running and accessible
- [ ] **MongoDB** running and accessible
- [ ] **Redis** running (optional)
- [ ] **Environment variables** configured
- [ ] **PostgreSQL schema** initialized with sample data
- [ ] **MongoDB indexes** created
- [ ] **Sample client databases** created
- [ ] **Backend** starts without errors
- [ ] **Frontend** starts without errors
- [ ] **Health checks** pass

## 🎯 **Quick Commands**

```bash
# Complete setup in one go
docker-compose up -d
docker-compose exec backend python scripts/setup_new_database.py
docker-compose exec mongodb mongosh --eval "use datadashboard_cache; db.sessions.createIndex({'session_id': 1}); db.cache.createIndex({'key': 1});"

# Check everything is working
curl http://localhost:8000/health
curl http://localhost:9002

# View logs
docker-compose logs -f
```

Your databases are now ready to support the multi-tenant DataWise application! 🚀 