# DataWise Backend API

A FastAPI backend with PostgreSQL database and MCP (Model Context Protocol) integration for the DataWise dashboard.

## 🚀 Features

- **FastAPI** with automatic API documentation
- **PostgreSQL** database with SQLAlchemy ORM
- **MCP Integration** - Model Context Protocol for AI-powered database queries
- **Google AI (Gemini)** integration via Genkit
- **JWT Authentication** with secure password hashing
- **Query Logging** for SQL and LLM queries
- **Database Schema Discovery** for AI context
- **CORS Support** for frontend integration

## 🏗️ Architecture

```
Backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Configuration & security
│   ├── database/             # Database connection
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   └── services/             # Business logic
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── main.py                  # FastAPI application
```

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `env.example` to `.env` and configure:

```bash
cp env.example .env
```

Update the following variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: JWT secret key
- `REDIS_URL`: Redis connection (optional)

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb datadashboard

# Run migrations
alembic upgrade head
```

### 5. Run the Application

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Queries
- `POST /api/v1/queries/sql` - Execute SQL query
- `POST /api/v1/queries/llm` - Execute LLM query with database context
- `GET /api/v1/queries/logs` - Get query history
- `GET /api/v1/queries/schema` - Get database schema
- `GET /api/v1/queries/sample-data/{table_name}` - Get sample data

## 🤖 MCP Integration

The backend implements Model Context Protocol (MCP) for AI-powered database interactions:

1. **Database Schema Discovery**: Automatically discovers table structures
2. **Context-Aware Queries**: Provides relevant schema and sample data to AI
3. **SQL Generation**: AI can generate SQL from natural language
4. **Intelligent Responses**: AI responses are enhanced with database context

### Example LLM Query Flow:

1. User asks: "Show me the total sales by region"
2. System discovers relevant tables (sales, regions)
3. Provides schema and sample data to AI
4. AI generates SQL: `SELECT region, SUM(sales) FROM sales GROUP BY region`
5. Returns both natural language response and generated SQL

## 🔐 Security Features

- **JWT Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **CORS Protection** for frontend integration
- **Input Validation** with Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy

## 📊 Database Models

### Users
- User authentication and management
- JWT token generation and validation

### Query Logs
- Track SQL and LLM query execution
- Performance metrics and error logging
- User association for audit trails

### Database Schema
- Store metadata about database structure
- Sample data for AI context
- Schema versioning and updates

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
OPENAI_API_KEY=your-production-key
SECRET_KEY=your-secure-secret-key
```

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black app/
isort app/
```

## 🤝 Integration with Frontend

The backend is designed to work seamlessly with the Next.js frontend:

1. **CORS Configuration**: Allows requests from frontend
2. **JWT Authentication**: Secure API access
3. **Real-time Updates**: WebSocket support (planned)
4. **Error Handling**: Consistent error responses

## 📈 Monitoring & Logging

- **Query Performance**: Track execution times
- **Error Logging**: Comprehensive error tracking
- **User Activity**: Audit trails for queries
- **Health Checks**: `/health` endpoint for monitoring

## 🔮 Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Redis caching for improved performance
- [ ] Advanced query optimization
- [ ] Multi-database support
- [ ] Query result caching
- [ ] Advanced analytics and reporting 