#!/bin/bash

# Production Deployment Validation Script
# This script validates that your Lambda deployment is production-ready

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

# Configuration
FUNCTION_NAME=${LAMBDA_FUNCTION_NAME:-chatbot-backend}
REGION=${AWS_REGION:-us-east-1}

log_info "🔍 Validating production deployment for ${FUNCTION_NAME}..."

# Check if function exists
log_info "Checking if Lambda function exists..."
if aws lambda get-function --function-name ${FUNCTION_NAME} --region ${REGION} >/dev/null 2>&1; then
    log_success "Lambda function exists"
else
    log_error "Lambda function ${FUNCTION_NAME} not found"
    exit 1
fi

# Get function configuration
log_info "Retrieving function configuration..."
FUNCTION_CONFIG=$(aws lambda get-function-configuration --function-name ${FUNCTION_NAME} --region ${REGION})

# Check memory configuration
MEMORY_SIZE=$(echo ${FUNCTION_CONFIG} | jq -r '.MemorySize')
if [ ${MEMORY_SIZE} -lt 1024 ]; then
    log_warning "Memory size is ${MEMORY_SIZE}MB. Recommend at least 1024MB for ML workloads"
else
    log_success "Memory size: ${MEMORY_SIZE}MB"
fi

# Check timeout configuration
TIMEOUT=$(echo ${FUNCTION_CONFIG} | jq -r '.Timeout')
if [ ${TIMEOUT} -lt 30 ]; then
    log_warning "Timeout is ${TIMEOUT}s. Recommend at least 30s for API responses"
else
    log_success "Timeout: ${TIMEOUT}s"
fi

# Check environment variables
log_info "Validating environment variables..."
ENV_VARS=$(echo ${FUNCTION_CONFIG} | jq -r '.Environment.Variables')

# Check critical environment variables
REQUIRED_VARS=("ENVIRONMENT" "GOOGLE_API_KEY" "DATABASE_URL")
for var in "${REQUIRED_VARS[@]}"; do
    if echo ${ENV_VARS} | jq -e "has(\"$var\")" >/dev/null; then
        if [ "$var" = "ENVIRONMENT" ]; then
            ENV_VALUE=$(echo ${ENV_VARS} | jq -r ".${var}")
            if [ "$ENV_VALUE" = "production" ]; then
                log_success "Environment: $ENV_VALUE"
            else
                log_warning "Environment is '$ENV_VALUE', should be 'production'"
            fi
        else
            log_success "$var is configured"
        fi
    else
        log_error "$var is not configured"
    fi
done

# Test health endpoint
log_info "Testing health endpoint..."
if aws lambda invoke \
    --function-name ${FUNCTION_NAME} \
    --payload '{"httpMethod":"GET","path":"/health","headers":{},"requestContext":{"httpMethod":"GET","resourcePath":"/health"}}' \
    --region ${REGION} \
    health_response.json \
    --output text >/dev/null 2>&1; then

    if [ -f "health_response.json" ]; then
        if grep -q '"status":"healthy"' health_response.json 2>/dev/null; then
            log_success "Health check passed"
        else
            log_warning "Health check returned unexpected response:"
            if command -v jq >/dev/null 2>&1; then
                cat health_response.json | jq . 2>/dev/null || cat health_response.json
            else
                cat health_response.json
            fi
        fi
        rm -f health_response.json
    fi
else
    log_warning "Unable to test health endpoint"
fi

# Test API Gateway integration (if configured)
log_info "Checking API Gateway integration..."
API_GATEWAYS=$(aws apigateway get-rest-apis --region ${REGION} --query 'items[?name==`chatbot-api`].id' --output text)

if [ -n "$API_GATEWAYS" ] && [ "$API_GATEWAYS" != "None" ]; then
    log_success "API Gateway found: $API_GATEWAYS"
    
    # Test actual API endpoint if URL is provided
    if [ -n "$API_GATEWAY_URL" ]; then
        log_info "Testing API Gateway endpoint..."
        if curl -s -f "${API_GATEWAY_URL}/health" | grep -q "healthy"; then
            log_success "API Gateway health check passed"
        else
            log_warning "API Gateway health check failed or returned unexpected response"
        fi
    fi
else
    log_warning "No API Gateway found. You'll need to configure API Gateway to route requests to this Lambda"
fi

# Check CloudWatch logs
log_info "Checking CloudWatch logs configuration..."
LOG_GROUP="/aws/lambda/${FUNCTION_NAME}"
if aws logs describe-log-groups --log-group-name-prefix ${LOG_GROUP} --region ${REGION} | grep -q ${LOG_GROUP}; then
    log_success "CloudWatch log group exists: ${LOG_GROUP}"
else
    log_warning "CloudWatch log group not found: ${LOG_GROUP}"
fi

# Security validation
log_info "Performing security validation..."

# Check if docs are disabled in production
if aws lambda invoke \
    --function-name ${FUNCTION_NAME} \
    --payload '{"httpMethod":"GET","path":"/docs","headers":{},"requestContext":{"httpMethod":"GET","resourcePath":"/docs"}}' \
    --region ${REGION} \
    docs_response.json \
    --output text >/dev/null 2>&1; then

    if [ -f "docs_response.json" ]; then
        if grep -q '"statusCode":404' docs_response.json 2>/dev/null; then
            log_success "API docs are properly disabled in production"
        else
            log_warning "API docs may be exposed in production"
        fi
        rm -f docs_response.json
    fi
else
    log_info "Unable to test docs endpoint (this is expected)"
fi

# Final summary
log_info "Validation Summary:"
echo ""
echo "📊 Function Details:"
echo "   Name: ${FUNCTION_NAME}"
echo "   Memory: ${MEMORY_SIZE}MB"
echo "   Timeout: ${TIMEOUT}s"
echo "   Runtime: Container"
echo ""

log_success "✅ Production deployment validation completed!"
echo ""
echo "🔗 Next Steps (if not already done):"
echo "   1. Configure API Gateway with custom domain"
echo "   2. Set up CloudWatch alarms and monitoring"
echo "   3. Configure auto-scaling and provisioned concurrency"
echo "   4. Set up backup and disaster recovery"
echo "   5. Implement proper CI/CD pipeline"
echo ""

# Provide useful commands
echo "🛠️  Useful Commands:"
echo "   View logs: aws logs tail /aws/lambda/${FUNCTION_NAME} --follow --region ${REGION}"
echo "   Update function: ./deploy-lambda.sh"
echo "   Get function info: aws lambda get-function --function-name ${FUNCTION_NAME} --region ${REGION}"
echo ""
