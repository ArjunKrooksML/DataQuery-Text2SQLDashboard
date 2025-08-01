# DataWise Setup Guide

Complete setup guide for the AI-Powered SQL Dashboard with FastAPI backend and Next.js frontend.

## 🏗️ Architecture Overview

```
AI_POWERED_SQL_DASHBOARD/
├── Frontend/          # Next.js React application
├── Backend/           # FastAPI Python application
├── docker-compose.yml # Complete stack orchestration
└── SETUP.md          # This file
```

## 🚀 Quick Start (Docker)

The fastest way to get everything running:

### 1. Prerequisites
- Docker and Docker Compose installed
- OpenAI API key (for LLM features)

### 2. Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd AI_POWERED_SQL_DASHBOARD

# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here
```

### 3. Start the Application
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost:9002
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (postgres/postgres)

## 🛠️ Manual Setup

### Backend Setup

#### 1. Python Environment
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Database Setup
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb datadashboard

# Set up environment variables
cp env.example .env
# Edit .env with your database credentials
```

#### 3. Run Backend
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

#### 1. Node.js Environment
```bash
cd Frontend
npm install
```

#### 2. Environment Configuration
```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### 3. Run Frontend
```bash
npm run dev
```

## 🔧 Database Setup

### 1. Initialize Database
```bash
cd Backend
python scripts/setup_database.py
```

This will create:
- Sample tables (sales_data, orders, users)
- Sample data for testing
- Admin user (admin/admin123)
- Sample query logs

### 2. Database Schema
The setup creates these tables:

**sales_data**
- id (SERIAL PRIMARY KEY)
- product_name (VARCHAR)
- region (VARCHAR)
- sales_amount (DECIMAL)
- sales_date (DATE)
- customer_id (INTEGER)

**orders**
- id (SERIAL PRIMARY KEY)
- order_date (DATE)
- customer_name (VARCHAR)
- total_amount (DECIMAL)
- status (VARCHAR)

**users** (for authentication)
- id (SERIAL PRIMARY KEY)
- username (VARCHAR UNIQUE)
- email (VARCHAR UNIQUE)
- hashed_password (VARCHAR)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

**query_logs** (for tracking queries)
- id (SERIAL PRIMARY KEY)
- user_id (INTEGER)
- query_type (ENUM: 'sql', 'llm')
- query_text (TEXT)
- response_data (TEXT)
- execution_time_ms (INTEGER)
- status (VARCHAR)
- created_at (TIMESTAMP)

## 🔐 Authentication

### Default Admin User
- **Username**: admin
- **Password**: admin123

### Frontend Authentication Flow
The frontend now includes a complete authentication system:

1. **Login Page**: Users are redirected to `/login` first
2. **JWT Tokens**: Stored in localStorage for session persistence
3. **Protected Routes**: Dashboard requires authentication
4. **Auto-redirect**: Authenticated users are redirected to dashboard

### API Authentication
The backend uses JWT tokens for authentication:

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

### Testing Authentication
1. **Start the application**: `docker-compose up`
2. **Visit**: http://localhost:9002
3. **You'll be redirected to**: http://localhost:9002/login
4. **Login with**: admin/admin123
5. **You'll be redirected to**: http://localhost:9002/dashboard

## 🤖 MCP (Model Context Protocol) Features

### Database-Aware AI
The backend implements MCP for intelligent database interactions:

1. **Schema Discovery**: Automatically discovers table structures
2. **Context-Aware Queries**: Provides relevant schema to AI
3. **SQL Generation**: AI can generate SQL from natural language
4. **Intelligent Responses**: Enhanced responses with database context

### Example Queries

**Natural Language to SQL:**
- Input: "Show me total sales by region"
- Generated SQL: `SELECT region, SUM(sales_amount) FROM sales_data GROUP BY region`

**AI-Powered Analysis:**
- Input: "What are the top selling products?"
- AI Response: Analyzes data and provides insights with generated SQL

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register

### Queries
- `POST /api/v1/queries/sql` - Execute SQL
- `POST /api/v1/queries/llm` - Execute LLM query
- `GET /api/v1/queries/logs` - Get query history
- `GET /api/v1/queries/schema` - Get database schema
- `GET /api/v1/queries/sample-data/{table}` - Get sample data

## 🔍 Testing the Application

### 1. SQL Queries
Try these sample queries:
```sql
SELECT * FROM sales_data LIMIT 5;
SELECT region, SUM(sales_amount) FROM sales_data GROUP BY region;
SELECT product_name, COUNT(*) FROM sales_data GROUP BY product_name;
```

### 2. LLM Queries
Try these natural language queries:
- "What are the top selling products?"
- "Show me sales by region"
- "How many orders do we have?"
- "What's the average order value?"

### 3. Charts
The charts panel displays sample data. In a real implementation, this would connect to your actual database.

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d datadashboard
```

#### 2. API Connection
```bash
# Test backend health
curl http://localhost:8000/health

# Check API docs
curl http://localhost:8000/docs
```

#### 3. Frontend Issues
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

#### 4. Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Environment Variables

**Backend (.env)**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/datadashboard
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
DEBUG=True
```

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Production Deployment

### 1. Environment Variables
```bash
# Production settings
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secure-production-key
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### 2. Security Considerations
- Change default passwords
- Use strong SECRET_KEY
- Enable HTTPS
- Configure CORS properly
- Set up proper database permissions

### 3. Performance Optimization
- Enable Redis caching
- Use connection pooling
- Implement query result caching
- Set up monitoring and logging

## 📈 Monitoring & Logging

### Backend Logs
```bash
# View backend logs
docker-compose logs backend

# View real-time logs
docker-compose logs -f backend
```

### Database Monitoring
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d datadashboard

# View query logs
SELECT * FROM query_logs ORDER BY created_at DESC LIMIT 10;
```

## 🔮 Next Steps

### Potential Enhancements
1. **Real-time Updates**: WebSocket integration
2. **Advanced Analytics**: More chart types and dashboards
3. **Multi-database Support**: Connect to different databases
4. **Query Optimization**: AI-powered query suggestions
5. **User Management**: Role-based access control
6. **Data Export**: CSV, Excel export functionality
7. **Scheduled Reports**: Automated report generation
8. **Mobile App**: React Native mobile application

### Integration Possibilities
- **BI Tools**: Connect to Tableau, Power BI
- **Data Warehouses**: Snowflake, BigQuery integration
- **ETL Pipelines**: Apache Airflow integration
- **Monitoring**: Prometheus, Grafana integration

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Google AI Documentation](https://ai.google.dev/)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 