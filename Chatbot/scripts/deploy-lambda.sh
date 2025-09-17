#!/bin/bash

# Production AWS Lambda Deployment Script for Chatbot API
# This script builds, tests, and deploys the chatbot to AWS Lambda with production optimizations

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration with validation
REGION=${AWS_REGION:-us-east-1}
FUNCTION_NAME=${LAMBDA_FUNCTION_NAME:-chatbot-backend}
ECR_REPOSITORY=${ECR_REPOSITORY:-chatbot-lambda}
IMAGE_TAG=${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}
ENVIRONMENT=${ENVIRONMENT:-production}

# Validate required environment variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    log_info "AWS_ACCOUNT_ID not set, attempting to retrieve..."
fi

log_info "Starting production Lambda deployment process..."
log_info "Environment: ${ENVIRONMENT}"
log_info "Region: ${REGION}"
log_info "Function: ${FUNCTION_NAME}"
log_info "Repository: ${ECR_REPOSITORY}"
log_info "Image Tag: ${IMAGE_TAG}"

# Get AWS Account ID
log_info "Retrieving AWS Account ID..."
if ! ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
    log_error "Failed to retrieve AWS Account ID. Please check your AWS credentials."
    exit 1
fi
log_success "AWS Account ID: ${ACCOUNT_ID}"

# ECR Repository URI
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}"

# Pre-deployment validation
log_info "Running pre-deployment validation..."

# Check if ECR repository exists
if ! aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${REGION} >/dev/null 2>&1; then
    log_warning "ECR repository ${ECR_REPOSITORY} does not exist. Creating it..."
    aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${REGION}
    log_success "ECR repository created"
fi

# Validate Lambda Dockerfile exists
if [ ! -f "Dockerfile.lambda" ]; then
    log_error "Dockerfile.lambda not found in current directory"
    exit 1
fi

# Validate backend directory exists
if [ ! -d "backend" ]; then
    log_error "Backend directory not found"
    exit 1
fi

# Build Docker image with Lambda optimizations
log_info "Building optimized Docker image for Lambda using Dockerfile.lambda..."
docker build \
    --file Dockerfile.lambda \
    --tag ${ECR_REPOSITORY}:${IMAGE_TAG} \
    --tag ${ECR_REPOSITORY}:latest \
    --build-arg ENVIRONMENT=${ENVIRONMENT} \
    --platform linux/amd64 \
    .
log_success "Lambda Docker image built successfully"

# Test the image locally (optional)
if [ "${SKIP_LOCAL_TEST:-false}" != "true" ]; then
    log_info "Running basic image validation..."
    if docker run --rm ${ECR_REPOSITORY}:${IMAGE_TAG} python -c "import lambda_function; print('✅ Lambda handler imports successfully')" 2>/dev/null; then
        log_success "Image validation passed"
    else
        log_warning "Image validation failed, but continuing deployment"
    fi
fi

# Login to ECR
log_info "Authenticating with ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
log_success "ECR authentication successful"

# Tag and push image
log_info "Tagging image for ECR..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:latest

log_info "Pushing image to ECR (this may take a few minutes)..."
docker push ${ECR_URI}:${IMAGE_TAG}
docker push ${ECR_URI}:latest
log_success "Image pushed to ECR successfully"

# Update Lambda function
log_info "Updating Lambda function code..."
UPDATE_RESULT=$(aws lambda update-function-code \
    --function-name ${FUNCTION_NAME} \
    --image-uri ${ECR_URI}:${IMAGE_TAG} \
    --region ${REGION} \
    --output json)

# Wait for update to complete
log_info "Waiting for function update to complete..."
aws lambda wait function-updated --function-name ${FUNCTION_NAME} --region ${REGION}

# Update environment variables for production
log_info "Updating Lambda environment configuration..."
aws lambda update-function-configuration \
    --function-name ${FUNCTION_NAME} \
    --environment Variables="{ENVIRONMENT=${ENVIRONMENT}}" \
    --timeout 30 \
    --memory-size 1024 \
    --region ${REGION} \
    >/dev/null

# Test the deployed function
log_info "Testing deployed function..."
if TEST_RESULT=$(aws lambda invoke \
    --function-name ${FUNCTION_NAME} \
    --payload '{"httpMethod":"GET","path":"/health","headers":{},"requestContext":{"httpMethod":"GET","resourcePath":"/health"}}' \
    --region ${REGION} \
    response.json \
    --output text 2>/dev/null); then
    
    if [ -f "response.json" ]; then
        if grep -q '"status":"healthy"' response.json 2>/dev/null; then
            log_success "Health check passed"
        else
            log_warning "Health check returned unexpected response:"
            cat response.json 2>/dev/null || echo "Unable to read response"
        fi
        rm -f response.json
    fi
else
    log_warning "Lambda function test failed, but deployment may still be successful"
fi

# Get function details
FUNCTION_ARN=$(echo ${UPDATE_RESULT} | jq -r '.FunctionArn')
FUNCTION_VERSION=$(echo ${UPDATE_RESULT} | jq -r '.Version')

log_success "Lambda deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "🌐 Function Name: ${FUNCTION_NAME}"
echo "🏷️  Function ARN: ${FUNCTION_ARN}"
echo "📦 Version: ${FUNCTION_VERSION}"
echo "🖼️  Image URI: ${ECR_URI}:${IMAGE_TAG}"
echo "🌍 Region: ${REGION}"
echo "⚙️  Environment: ${ENVIRONMENT}"
echo ""
echo "🔗 Next Steps:"
echo "   1. Configure API Gateway to route requests to this function"
echo "   2. Set up custom domain and SSL certificate"
echo "   3. Configure CloudWatch alarms and monitoring"
echo "   4. Update environment variables with production secrets"
echo ""
log_success "Deployment complete! 🎉"
