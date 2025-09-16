# Recycling & Sustainability Assistant API Reference

## Overview

The Recycling & Sustainability Assistant API is a FastAPI-based backend service that provides AI-powered chatbot functionality for waste management and sustainability guidance. The API supports conversation management, multimodal chat with image support, and knowledge base operations with semantic search capabilities.

**Version:** 1.0.0

## Base URL

```
http://127.0.0.1:8000
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Global Response Format

All API responses follow a consistent format with appropriate HTTP status codes. Error responses include:

```json
{
  "error": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint"
}
```

## Endpoints

### Health & Status Endpoints

#### GET /health

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0"
}
```

#### GET /

Get API information and available endpoints.

**Response:**
```json
{
  "message": "Recycling & Sustainability Assistant API",
  "version": "1.0.0",
  "documentation": "/docs",
  "health": "/health",
  "endpoints": {
    "chat": "/api/chat",
    "upload": "/api/upload",
    "images": "/api/images"
  }
}
```

#### GET /api/status

Get detailed API status and feature availability.

**Response:**
```json
{
  "api_status": "operational",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "features": {
    "chat": true,
    "image_upload": true,
    "image_classification": true,
    "conversation_history": true,
    "export_data": true
  },
  "ai_services": {
    "gemini_chatbot": true,
    "waste_management_agent": true
  }
}
```

#### POST /api/feedback

Submit user feedback.

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great service!",
  "category": "general"
}
```

**Response:**
```json
{
  "message": "Thank you for your feedback!",
  "received_at": "2024-01-15T10:30:00.000Z"
}
```

### Chat Endpoints

#### POST /chat/new

Create a new conversation.

**Request Body:**
```json
{
  "title": "Recycling Questions"
}
```

**Response:**
```json
{
  "conv_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Recycling Questions",
  "created_at": "2024-01-15T10:30:00.000Z"
}
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

#### GET /chat/list

List all conversations for the current user.

**Response:**
```json
[
  {
    "conv_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Recycling Questions",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

#### DELETE /chat/{conv_id}

Delete a specific conversation.

**Path Parameters:**
- `conv_id` (string, required): UUID of the conversation

**Response:**
```json
{
  "message": "Conversation 550e8400-e29b-41d4-a716-446655440000 deleted"
}
```

**Status Codes:**
- `200`: Success
- `404`: Conversation not found
- `500`: Internal server error

#### GET /chat/{conv_id}/history

Get conversation message history.

**Path Parameters:**
- `conv_id` (string, required): UUID of the conversation

**Response:**
```json
[
  {
    "role": "user",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "type": "text",
    "content": "How do I recycle plastic bottles?",
    "images": null
  },
  {
    "role": "assistant",
    "timestamp": "2024-01-15T10:31:00.000Z",
    "type": "text",
    "content": "To recycle plastic bottles, first remove caps and labels...",
    "images": null
  }
]
```

**Status Codes:**
- `200`: Success
- `404`: Conversation not found
- `500`: Internal server error

#### POST /chat/{conv_id}/send-stream

Send a message with optional images and receive streaming response.

**Path Parameters:**
- `conv_id` (string, required): UUID of the conversation

**Request Body (multipart/form-data):**
- `content` (string, required): Message content
- `images` (file[], optional): Image files (JPG, PNG, etc.)

**Response:** Server-Sent Events (text/event-stream)

Stream format:
```
data: {"token": "Hello"}

data: {"token": " world"}

data: [DONE]
```

Error format:
```
data: {"error": "Error message"}
```

**Headers:**
- `Content-Type: multipart/form-data`

**Example cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/chat/550e8400-e29b-41d4-a716-446655440000/send-stream" \
  -F "content=How do I recycle this item?" \
  -F "images=@recycling_item.jpg"
```

**Status Codes:**
- `200`: Stream started successfully
- `400`: Bad request (no content or images provided)
- `404`: Conversation not found
- `500`: Internal server error

### Knowledge Base Endpoints

#### POST /kb/

Create a new knowledge base entry.

**Request Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content_type": "faq",
  "title": "How to recycle electronic waste",
  "content": "Electronic waste should be taken to certified e-waste recycling centers...",
  "metadata": {
    "category": "electronics",
    "priority": "high"
  },
  "keywords": ["electronics", "e-waste", "recycling"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content_type": "faq",
  "title": "How to recycle electronic waste",
  "content": "Electronic waste should be taken to certified e-waste recycling centers...",
  "metadata": {
    "category": "electronics",
    "priority": "high"
  },
  "keywords": ["electronics", "e-waste", "recycling"],
  "embedding": [0.1, 0.2, 0.3, ...],
  "similarity_score": null
}
```

**Status Codes:**
- `201`: Created successfully
- `400`: Bad request
- `500`: Internal server error

#### GET /kb/{kb_id}

Retrieve a specific knowledge base entry.

**Path Parameters:**
- `kb_id` (string, required): UUID of the KB entry

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content_type": "faq",
  "title": "How to recycle electronic waste",
  "content": "Electronic waste should be taken to certified e-waste recycling centers...",
  "metadata": {
    "category": "electronics",
    "priority": "high"
  },
  "keywords": ["electronics", "e-waste", "recycling"],
  "embedding": [0.1, 0.2, 0.3, ...],
  "similarity_score": null
}
```

**Status Codes:**
- `200`: Success
- `404`: KB entry not found
- `500`: Internal server error

#### GET /kb/

List all knowledge base entries with optional filtering and pagination.

**Query Parameters:**
- `content_type` (string, optional): Filter by content type
- `limit` (integer, optional): Maximum entries to return (1-1000, default: 100)
- `offset` (integer, optional): Number of entries to skip (default: 0)

**Example:**
```
GET /kb/?content_type=faq&limit=50&offset=0
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content_type": "faq",
    "title": "How to recycle electronic waste",
    "content": "Electronic waste should be taken to certified e-waste recycling centers...",
    "metadata": {
      "category": "electronics",
      "priority": "high"
    },
    "keywords": ["electronics", "e-waste", "recycling"],
    "embedding": [0.1, 0.2, 0.3, ...],
    "similarity_score": null
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

#### PUT /kb/{kb_id}

Update an existing knowledge base entry.

**Path Parameters:**
- `kb_id` (string, required): UUID of the KB entry

**Request Body:**
```json
{
  "title": "Updated title",
  "content": "Updated content",
  "keywords": ["updated", "keywords"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content_type": "faq",
  "title": "Updated title",
  "content": "Updated content",
  "metadata": {
    "category": "electronics",
    "priority": "high"
  },
  "keywords": ["updated", "keywords"],
  "embedding": [0.1, 0.2, 0.3, ...],
  "similarity_score": null
}
```

**Status Codes:**
- `200`: Updated successfully
- `400`: Bad request
- `404`: KB entry not found
- `500`: Internal server error

#### DELETE /kb/{kb_id}

Delete a knowledge base entry.

**Path Parameters:**
- `kb_id` (string, required): UUID of the KB entry

**Response:** 204 No Content

**Status Codes:**
- `204`: Deleted successfully
- `400`: Bad request
- `404`: KB entry not found
- `500`: Internal server error

#### POST /kb/search

Perform semantic search across knowledge base entries.

**Query Parameters:**
- `query` (string, required): Search query
- `limit` (integer, optional): Maximum results to return (1-100, default: 10)
- `similarity_threshold` (float, optional): Minimum similarity score (0.0-1.0, default: 0.7)

**Request Body:**
```json
{
  "query": "how to recycle plastic",
  "limit": 10,
  "similarity_threshold": 0.7
}
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content_type": "faq",
    "title": "Plastic recycling guidelines",
    "content": "Different types of plastic require different recycling methods...",
    "metadata": {
      "category": "recycling",
      "priority": "medium"
    },
    "keywords": ["plastic", "recycling", "guidelines"],
    "embedding": [0.1, 0.2, 0.3, ...],
    "similarity_score": 0.85
  }
]
```

**Status Codes:**
- `200`: Success
- `500`: Internal server error

## Data Models

### ConversationCreateDTO
```json
{
  "title": "string (optional)"
}
```

### ConversationResponseDTO
```json
{
  "conv_id": "uuid",
  "title": "string (nullable)",
  "created_at": "datetime"
}
```

### ConversationListDTO
```json
{
  "conv_id": "uuid",
  "title": "string (nullable)",
  "updated_at": "datetime"
}
```

### MessageHistoryDTO
```json
{
  "role": "user | assistant",
  "timestamp": "datetime",
  "type": "text | image",
  "content": "string (nullable)",
  "images": "ImageDTO[] (nullable)"
}
```

### KBEntryCreateDTO
```json
{
  "id": "string (optional, UUID generated if not provided)",
  "content_type": "string (optional)",
  "title": "string (required)",
  "content": "string (required)",
  "metadata": "object (optional)",
  "keywords": "string[] (optional)"
}
```

### KBEntryUpdateDTO
```json
{
  "content_type": "string (optional)",
  "title": "string (optional)",
  "content": "string (optional)",
  "metadata": "object (optional)",
  "keywords": "string[] (optional)"
}
```

### KBEntryResponseDTO
```json
{
  "id": "string",
  "content_type": "string (nullable)",
  "title": "string (nullable)",
  "content": "string (nullable)",
  "metadata": "object (nullable)",
  "keywords": "string[] (nullable)",
  "embedding": "float[] (nullable)",
  "similarity_score": "float (nullable, only in search results)"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint"
}
```

#### 404 Not Found
```json
{
  "error": "Resource not found",
  "status_code": 404,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "status_code": 500,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint"
}
```

### Validation Errors

Pydantic validation errors return detailed field-level error information:

```json
{
  "error": {
    "detail": [
      {
        "loc": ["body", "title"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  },
  "status_code": 422,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "path": "/api/endpoint"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. All endpoints accept unlimited requests.

## CORS Configuration

The API is configured to accept requests from any origin with the following CORS settings:
- `allow_origins`: `["*"]`
- `allow_credentials`: `true`
- `allow_methods`: `["*"]`
- `allow_headers`: `["*"]`

## Example Usage

### Complete Conversation Flow

1. **Create a new conversation:**
```bash
curl -X POST "http://127.0.0.1:8000/chat/new" \
  -H "Content-Type: application/json" \
  -d '{"title": "Recycling Help"}'
```

2. **Send a message with image:**
```bash
curl -X POST "http://127.0.0.1:8000/chat/{conv_id}/send-stream" \
  -F "content=What type of plastic is this?" \
  -F "images=@plastic_bottle.jpg"
```

3. **Get conversation history:**
```bash
curl -X GET "http://127.0.0.1:8000/chat/{conv_id}/history"
```

### Knowledge Base Operations

1. **Create KB entry:**
```bash
curl -X POST "http://127.0.0.1:8000/kb/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Paper Recycling",
    "content": "Clean paper products can be recycled...",
    "content_type": "guide",
    "keywords": ["paper", "recycling", "clean"]
  }'
```

2. **Search KB entries:**
```bash
curl -X POST "http://127.0.0.1:8000/kb/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "paper recycling",
    "limit": 5,
    "similarity_threshold": 0.8
  }'
```

## Interactive Documentation

Visit `http://127.0.0.1:8000/docs` for Swagger UI interactive documentation or `http://127.0.0.1:8000/redoc` for ReDoc documentation.

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Database
- **Pydantic**: Data validation
- **Google Gemini**: AI chatbot model
- **LangSmith**: AI tracing and monitoring
- **Uvicorn**: ASGI server