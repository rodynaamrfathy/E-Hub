# Production Deployment Guide

This guide provides comprehensive instructions for deploying the Chatbot API to AWS Lambda in a production-ready configuration.

## 🚀 Quick Start

1. **Set up environment variables**:
   ```bash
   export AWS_REGION=us-east-1
   export LAMBDA_FUNCTION_NAME=chatbot-backend-prod
   export ECR_REPOSITORY=chatbot-lambda
   export ENVIRONMENT=production
   ```

2. **Deploy to Lambda**:
   ```bash
   ./deploy-lambda.sh
   ```

## 📋 Prerequisites

### AWS Setup
- AWS CLI configured with appropriate permissions
- Docker installed and running
- `jq` command-line JSON processor

### Required AWS Permissions
Your AWS credentials need the following permissions:
- `lambda:*` (for Lambda function management)
- `ecr:*` (for container registry operations)
- `sts:GetCallerIdentity` (for account ID retrieval)
- `logs:*` (for CloudWatch logging)

## 🔧 Environment Configuration

### 1. Lambda Environment Variables

Set these in your Lambda function configuration:

```bash
# Core Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO

# API Keys (Required)
GOOGLE_API_KEY=your_actual_api_key
LANGSMITH_API_KEY=your_langsmith_key
EXA_API_KEY=your_exa_key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Security
ALLOWED_HOSTS=your-api-gateway-domain.amazonaws.com
CORS_ORIGINS=https://your-frontend-domain.com

# Features
ENABLE_DOCS=false
ENABLE_METRICS=true
```

### 2. Lambda Function Configuration

Recommended settings:
- **Memory**: 1024 MB (minimum for ML workloads)
- **Timeout**: 30 seconds
- **Architecture**: x86_64
- **Runtime**: Container image

## 🏗️ Architecture Overview

```
Internet → API Gateway → Lambda Function → RDS/Neon Database
                      ↓
                   CloudWatch Logs
```

### Key Components

1. **FastAPI Application**: Production-optimized with security middleware
2. **Lambda Handler**: Custom handler with proper error handling and logging
3. **Database**: PostgreSQL with connection pooling
4. **Monitoring**: CloudWatch integration with structured logging

## 🛡️ Security Features

### Implemented Security Measures

1. **Security Headers**:
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 1; mode=block
   - Content Security Policy

2. **CORS Configuration**:
   - Configurable allowed origins
   - Proper credential handling
   - Exposed correlation headers

3. **Request Validation**:
   - Input sanitization
   - Rate limiting ready
   - Trusted host middleware

4. **Error Handling**:
   - No sensitive data exposure
   - Structured error responses
   - Correlation ID tracking

## 📊 Monitoring & Observability

### Health Checks

The API provides multiple health check endpoints:

- `/health` - Comprehensive health check with database connectivity
- `/health/ready` - Kubernetes-style readiness probe
- `/health/live` - Kubernetes-style liveness probe

### Logging

- **Structured logging** with correlation IDs
- **Request/response logging** with timing
- **Error tracking** with stack traces
- **CloudWatch integration** for centralized logs

### Metrics

Monitor these key metrics:
- Response times
- Error rates
- Database connection pool usage
- Lambda cold starts
- Memory utilization

## 🚦 Deployment Process

### Automated Deployment

The `deploy-lambda.sh` script handles:

1. **Pre-deployment validation**
2. **Docker image building** with optimizations
3. **ECR repository management**
4. **Image pushing and tagging**
5. **Lambda function updates**
6. **Post-deployment testing**

### Manual Verification

After deployment, verify:

1. **Health check**:
   ```bash
   curl https://your-api-gateway-url/health
   ```

2. **API functionality**:
   ```bash
   curl -X POST https://your-api-gateway-url/chat/stream \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "conversation_id": "test"}'
   ```

3. **CloudWatch logs**:
   Check `/aws/lambda/chatbot-backend-prod` log group

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Deploy to Lambda
        run: |
          export ENVIRONMENT=production
          ./deploy-lambda.sh
```

## 🔧 Troubleshooting

### Common Issues

1. **Cold Start Performance**:
   - Use provisioned concurrency for consistent performance
   - Optimize imports and initialization code
   - Consider connection pooling configuration

2. **Memory Issues**:
   - Monitor CloudWatch metrics
   - Increase Lambda memory if needed
   - Optimize database queries

3. **Database Connections**:
   - Configure appropriate pool sizes
   - Use connection pooling
   - Handle connection timeouts gracefully

### Debugging

1. **Check CloudWatch logs**:
   ```bash
   aws logs tail /aws/lambda/chatbot-backend-prod --follow
   ```

2. **Test locally**:
   ```bash
   docker run -p 8000:8000 -e ENVIRONMENT=development chatbot-lambda:latest
   ```

3. **Validate configuration**:
   ```bash
   aws lambda get-function-configuration --function-name chatbot-backend-prod
   ```

## 📈 Performance Optimization

### Lambda Optimizations

1. **Memory allocation**: Start with 1024MB, adjust based on usage
2. **Provisioned concurrency**: For consistent performance
3. **Connection pooling**: Optimize database connections
4. **Code splitting**: Lazy load heavy dependencies

### Database Optimizations

1. **Connection pooling**: Configure appropriate pool sizes
2. **Query optimization**: Use indexes and efficient queries
3. **Connection reuse**: Implement proper connection management

## 🔒 Security Best Practices

1. **API Keys**: Use AWS Secrets Manager for production
2. **Network Security**: Configure VPC if needed
3. **IAM Roles**: Use least privilege principle
4. **Logging**: Don't log sensitive information
5. **HTTPS**: Always use SSL/TLS
6. **Rate Limiting**: Implement at API Gateway level

## 📞 Support

For issues or questions:
1. Check CloudWatch logs first
2. Review this documentation
3. Test locally with Docker
4. Check AWS Lambda console for function status

## 🔄 Updates and Maintenance

### Regular Maintenance

1. **Security updates**: Keep dependencies updated
2. **Monitoring**: Review CloudWatch metrics regularly
3. **Cost optimization**: Monitor Lambda costs and optimize
4. **Performance**: Review and optimize based on usage patterns

### Version Management

- Use semantic versioning for Docker images
- Tag releases appropriately
- Maintain rollback capability
- Test thoroughly before production deployment
