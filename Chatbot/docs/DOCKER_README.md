# Docker Setup for Chatbot Backend

This document provides instructions for running the Chatbot backend using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system
- API keys for Google Gemini, EXA, and LangSmith services

## Quick Start

1. **Copy environment variables:**
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file with your actual API keys:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Check if services are running:**
   ```bash
   docker-compose ps
   ```

5. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - API Status: http://localhost:8000/api/status

## Services

### Chatbot Backend
- **Port:** 8000
- **Container:** chatbot-backend
- **Health Check:** http://localhost:8000/health

### PostgreSQL Database
- **Port:** 5432
- **Container:** chatbot-postgres
- **Database:** chatbot_db
- **User:** chatbot_user
- **Password:** chatbot_pass
- **Extensions:** pgvector (for vector operations)

### Redis Cache
- **Port:** 6379
- **Container:** chatbot-redis

### pgAdmin (Optional)
- **Port:** 8080
- **Container:** chatbot-pgadmin
- **Email:** admin@chatbot.com
- **Password:** admin123

To start with pgAdmin:
```bash
docker-compose --profile admin up -d
```

## Development Commands

### Start services in development mode:
```bash
docker-compose up
```

### Start services in background:
```bash
docker-compose up -d
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f chatbot
```

### Rebuild and restart:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Stop all services:
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: This will delete all data):
```bash
docker-compose down -v
```

## Environment Variables

The following environment variables can be configured in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Google Gemini API Key | Required |
| `EXA_API_KEY` | EXA API Key | Required |
| `LANGSMITH_API_KEY` | LangSmith API Key | Required |
| `LANGSMITH_PROJECT` | LangSmith Project Name | Dawar |
| `LANGCHAIN_TRACING_V2` | Enable LangChain tracing | true |
| `CHATBOT_MODEL` | Gemini model to use | gemini-2.5-pro |
| `MAX_HISTORY` | Max conversation history | 50 |

## Troubleshooting

### Service won't start
1. Check logs: `docker-compose logs [service-name]`
2. Verify environment variables in `.env` file
3. Ensure API keys are valid

### Database connection issues
1. Ensure PostgreSQL container is running: `docker-compose ps postgres`
2. Check database logs: `docker-compose logs postgres`
3. Verify database credentials in environment variables

### Port conflicts
If you get port conflict errors, you can modify the ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change left side to available port
```

### Reset everything
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

## Production Considerations

For production deployment:

1. **Security:**
   - Use proper secrets management instead of `.env` files
   - Change default database passwords
   - Use proper SSL certificates
   - Restrict CORS origins

2. **Performance:**
   - Use production-grade database (not local PostgreSQL)
   - Configure proper resource limits
   - Use external Redis service
   - Enable proper logging and monitoring

3. **Scalability:**
   - Use load balancer for multiple chatbot instances
   - Configure database connection pooling
   - Use external file storage for uploads

## API Endpoints

Once running, the following endpoints are available:

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/status` - Detailed API status
- `POST /api/feedback` - Submit feedback
- `POST /chat/*` - Chat endpoints
- `GET /kb/*` - Knowledge base endpoints
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation
