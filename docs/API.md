# API Documentation

Complete API reference for Gemini FastAPI Toolkit.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, authentication is optional. API key can be provided via `X-API-Key` header.

## Endpoints

### Text Generation

#### POST `/api/v1/text/generate`

Generate text from a prompt.

**Request:**
```json
{
  "prompt": "Write a story",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "text": "Generated text...",
  "model": "gemini-2.0-flash-exp",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 200,
    "total_tokens": 210
  }
}
```

### Image Analysis

#### POST `/api/v1/image/analyze`

Analyze an uploaded image.

**Request:** Multipart form data
- `file`: Image file
- `prompt`: Analysis prompt (optional)

**Response:**
```json
{
  "description": "Image description...",
  "confidence": 0.92,
  "model": "gemini-2.0-flash-exp"
}
```

### Health Check

#### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z",
  "details": {}
}
```

### Error Codes

- `GEMINI_API_ERROR`: Gemini API error
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INVALID_INPUT`: Invalid input validation
- `FILE_PROCESSING_ERROR`: File processing error
- `VALIDATION_ERROR`: Request validation error

## Rate Limits

Default: 60 requests/minute, 1000 requests/hour

Rate limit headers:
- `Retry-After`: Seconds to wait before retrying

## Full Documentation

Visit http://localhost:8000/docs for interactive API documentation.

