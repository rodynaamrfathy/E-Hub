"""
Production-ready AWS Lambda handler for FastAPI application.
Optimized for API Gateway integration with proper error handling and monitoring.
"""

import os
import logging
import json
from typing import Dict, Any
from mangum import Mangum
from mangum.adapter import LambdaContext

# Configure logging for Lambda
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

# Import the FastAPI app
try:
    from main import app
    logger.info("✅ FastAPI app imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import FastAPI app: {e}")
    raise

# Configure Mangum adapter for API Gateway
handler = Mangum(
    app, 
    lifespan="off",  # Disable lifespan for Lambda (cold starts)
    api_gateway_base_path="/",  # Set base path for API Gateway
    text_mime_types=[
        "application/json",
        "application/javascript",
        "application/xml",
        "application/vnd.api+json",
        "text/css",
        "text/html",
        "text/plain",
        "text/xml",
    ],
)

def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Production Lambda handler with comprehensive error handling and logging.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    # Log request details for debugging (remove sensitive data in production)
    logger.info(f"Lambda invocation - Request ID: {context.aws_request_id}")
    logger.info(f"HTTP Method: {event.get('httpMethod', 'UNKNOWN')}")
    logger.info(f"Path: {event.get('path', 'UNKNOWN')}")
    
    # Add correlation ID for request tracing
    correlation_id = context.aws_request_id
    event['headers'] = event.get('headers', {})
    event['headers']['X-Correlation-ID'] = correlation_id
    
    try:
        # Process the request through Mangum
        response = handler(event, context)
        
        # Ensure CORS headers are present for API Gateway
        if 'headers' not in response:
            response['headers'] = {}
            
        response['headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Correlation-ID',
            'X-Correlation-ID': correlation_id,
        })
        
        logger.info(f"✅ Request processed successfully - Status: {response.get('statusCode', 'UNKNOWN')}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Unhandled error in Lambda handler: {str(e)}", exc_info=True)
        
        # Return a proper API Gateway error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Correlation-ID',
                'X-Correlation-ID': correlation_id,
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred',
                'correlationId': correlation_id,
                'statusCode': 500
            })
        }

# For backwards compatibility
handler_legacy = handler
