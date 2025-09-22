# 🤖 AI Chatbot Backend - Production Ready

A production-ready AI chatbot backend built with FastAPI, optimized for AWS Lambda deployment with comprehensive Docker support for development and production.

## 🚀 Features

- **FastAPI Backend**: High-performance async API with automatic documentation
- **AWS Lambda Ready**: Optimized for serverless deployment with Mangum adapter
- **Multi-Modal AI**: Supports text and image processing with Google Gemini
- **Production Security**: Security headers, CORS, request validation, and error handling
- **Database Integration**: PostgreSQL with pgvector for embeddings and chat history
- **Comprehensive Monitoring**: Health checks, logging, and metrics collection
- **Development Tools**: Hot reload, debugging, and testing support

## 📋 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys and database URL
# Required: GOOGLE_API_KEY, DATABASE_URL
```

### 2. Development with Docker Compose

```bash
# Start development environment
docker-compose up --build

# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. AWS Lambda Deployment

```bash
# Set environment variables
export AWS_REGION=us-east-1
export LAMBDA_FUNCTION_NAME=chatbot-backend
export ECR_REPOSITORY=chatbot-lambda

# Deploy to Lambda
./deploy-lambda.sh

# Validate deployment
./validate-deployment.sh
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │────│  Lambda Function │────│   PostgreSQL    │
│                 │    │   (FastAPI +     │    │   (Neon DB)     │
│                 │    │    Mangum)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌────▼────┐            ┌─────▼─────┐          ┌─────▼─────┐
    │ Frontend│            │  Gemini   │          │  pgvector │
    │   App   │            │    AI     │          │ Embeddings│
    └─────────┘            └───────────┘          └───────────┘
```

## 🔧 Configuration Files

### Core Files
- `requirements.txt` - Python dependencies (production optimized)
- `pyproject.toml` - Project configuration and development dependencies
- `env.example` - Development environment template
- `lambda.env.example` - Production Lambda environment template

### Docker Files
- `Dockerfile.dev` - Development container with debugging tools
- `Dockerfile.lambda` - Production Lambda container (optimized)
- `Dockerfile.original` - Alternative Lambda configuration
- `docker-compose.yml` - Development orchestration

### Deployment Scripts
- `deploy-lambda.sh` - Automated Lambda deployment
- `validate-deployment.sh` - Post-deployment validation
- `PRODUCTION_CHECKLIST.md` - Pre-deployment checklist
- `PRODUCTION_DEPLOYMENT.md` - Comprehensive deployment guide

## 🛠️ Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

```bash
# Build development image
docker build -f Dockerfile.dev -t chatbot-dev .

# Run with volume mounting for hot reload
docker-compose up chatbot
```

### Testing

```bash
# Install test dependencies
pip install -r requirements.txt pytest pytest-asyncio

# Run tests
pytest backend/tests/
```

## 🚀 Production Deployment

### Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- ECR repository created
- Lambda function created (or will be created by script)

### Environment Variables (Production)

Set these in your Lambda function configuration:

```bash
ENVIRONMENT=production
GOOGLE_API_KEY=your_actual_api_key
DATABASE_URL=your_postgresql_url
LANGSMITH_API_KEY=your_langsmith_key
CORS_ORIGINS=https://your-domain.com
ALLOWED_HOSTS=your-api-gateway-domain.amazonaws.com
```

### Deployment Process

1. **Validate Configuration**
   ```bash
   # Check all requirements
   ./validate-deployment.sh
   ```

2. **Deploy to Lambda**
   ```bash
   # Automated deployment
   ./deploy-lambda.sh
   ```

3. **Post-Deployment Validation**
   ```bash
   # Test deployed function
   curl https://your-api-gateway-url/health
   ```

## 📊 Monitoring & Health Checks

### Health Endpoints

- `/health` - Comprehensive health check with database connectivity
- `/health/ready` - Kubernetes-style readiness probe
- `/health/live` - Kubernetes-style liveness probe

### Logging

- Structured logging with correlation IDs
- CloudWatch integration for Lambda
- Request/response timing and error tracking

## 🔒 Security Features

- **Security Headers**: XSS protection, content type options, frame options
- **CORS Configuration**: Configurable origins for cross-domain requests
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Secure error responses without information leakage
- **Production Mode**: API documentation disabled in production

## 🧪 Testing

### Automated Tests

```bash
# Unit tests
pytest backend/tests/test_*.py

# Integration tests
pytest backend/tests/test_*_integration.py

# Load testing
# (Configure your load testing tool)
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/chat/new \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation"}'
```

## 📚 Documentation

- `docs/architecture.md` - System architecture overview
- `docs/api_reference.md` - API endpoint documentation
- `docs/streaming_implementation.md` - Real-time streaming details
- `LAMBDA_DEPLOYMENT.md` - Lambda-specific deployment guide
- `PRODUCTION_DEPLOYMENT.md` - Complete production setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the troubleshooting guides in the docs/ directory
2. Review CloudWatch logs for Lambda deployments
3. Validate configuration with the provided scripts
4. Create an issue with detailed error information

---

**Production Ready** ✅ | **Docker Optimized** ✅ | **AWS Lambda** ✅ | **Security Hardened** ✅