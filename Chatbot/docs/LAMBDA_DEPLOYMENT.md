# AWS Lambda Deployment Guide

This guide explains how to deploy the chatbot backend to AWS Lambda using Docker containers.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- An AWS ECR repository created
- AWS Lambda function created (or will be created)

## Architecture Changes

The deployment has been optimized for AWS Lambda:

- ✅ **Removed Redis dependency** - No longer required for serverless deployment
- ✅ **Lambda-optimized Dockerfile** - Uses AWS Lambda Python base image
- ✅ **Mangum integration** - ASGI adapter for FastAPI on Lambda
- ✅ **Optimized dependencies** - Minimal package set for faster cold starts
- ✅ **Single-stage build** - Reduced image size and complexity

## Quick Deployment

### 1. Set Environment Variables

```bash
export AWS_REGION=us-east-1
export LAMBDA_FUNCTION_NAME=chatbot-backend
export ECR_REPOSITORY=chatbot-lambda
```

### 2. Create ECR Repository (if not exists)

```bash
aws ecr create-repository \
    --repository-name chatbot-lambda \
    --region $AWS_REGION
```

### 3. Deploy Using Script

```bash
./deploy-lambda.sh
```

## Manual Deployment Steps

### 1. Build Docker Image

```bash
docker build -t chatbot-lambda:latest .
```

### 2. Push to ECR

```bash
# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag chatbot-lambda:latest \
    $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-lambda:latest

docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-lambda:latest
```

### 3. Create/Update Lambda Function

```bash
# Create function (if not exists)
aws lambda create-function \
    --function-name chatbot-backend \
    --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
    --code ImageUri=$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-lambda:latest \
    --package-type Image \
    --timeout 30 \
    --memory-size 1024

# Update function code
aws lambda update-function-code \
    --function-name chatbot-backend \
    --image-uri $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/chatbot-lambda:latest
```

## Environment Configuration

Set the following environment variables in your Lambda function:

```bash
# Copy from lambda.env.example and set in Lambda console or via CLI
aws lambda update-function-configuration \
    --function-name chatbot-backend \
    --environment Variables='{
        "GOOGLE_API_KEY":"your_key_here",
        "DATABASE_URL":"your_db_url_here",
        "CHATBOT_MODEL":"gemini-2.5-pro"
    }'
```

## API Gateway Integration

To expose the Lambda function via HTTP, create an API Gateway:

```bash
# Create API Gateway (REST API)
aws apigateway create-rest-api \
    --name chatbot-api \
    --description "Chatbot Backend API"

# Configure proxy integration to Lambda
# (Additional API Gateway configuration required)
```

## Performance Optimizations

The Dockerfile includes several Lambda-specific optimizations:

1. **AWS Lambda base image** - Optimized runtime environment
2. **Multi-stage build** - Removes build tools from final image (saves ~550MB)
3. **Mangum ASGI adapter** - Efficient FastAPI integration
4. **Minimal dependencies** - Reduced cold start time and image size
5. **Layer caching** - Dependencies installed before application code
6. **Python optimization** - Removes .pyc, .pyo, __pycache__, tests, and dist-info
7. **No Redis** - Eliminated external dependencies

### Image Size Optimization

- **Original size**: 1.85GB
- **Optimized size**: 1.3GB  
- **Savings**: 550MB (30% reduction)

For even smaller images, use `requirements-minimal.txt` which removes LangChain dependencies and can reduce size to ~800MB.

## Monitoring and Logging

Lambda automatically provides:
- CloudWatch Logs integration
- X-Ray tracing (if enabled)
- CloudWatch Metrics

## Cost Optimization

- **Memory**: Start with 1024MB, adjust based on performance
- **Timeout**: Set to 30 seconds for API responses
- **Provisioned Concurrency**: Consider for production workloads

## Troubleshooting

### Common Issues

1. **Cold Start Timeout**: Increase memory allocation
2. **Import Errors**: Verify all dependencies in requirements.txt
3. **Database Connection**: Ensure VPC configuration if using private DB
4. **Environment Variables**: Check Lambda configuration

### Debugging

```bash
# Test function locally
docker run -p 8080:8080 chatbot-lambda:latest

# View Lambda logs
aws logs tail /aws/lambda/chatbot-backend --follow
```

## Migration from Docker Compose

The following changes were made from the original Docker Compose setup:

- ❌ **Removed**: Redis service and dependencies
- ❌ **Removed**: Volume mounts (not applicable in Lambda)
- ❌ **Removed**: Network configuration
- ✅ **Added**: Mangum ASGI adapter
- ✅ **Added**: Lambda-specific handler
- ✅ **Modified**: Base image to AWS Lambda Python

## Next Steps

1. Set up API Gateway for HTTP access
2. Configure CloudWatch alarms for monitoring
3. Implement CI/CD pipeline for automated deployments
4. Consider using AWS SAM for infrastructure as code
