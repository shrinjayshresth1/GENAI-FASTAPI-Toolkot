# 🤖 Gemini FastAPI Toolkit

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)

**Production-ready FastAPI toolkit for Google Gemini API integration with comprehensive multimodal support**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Usage Examples](#-usage-examples)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Performance & Optimization](#-performance--optimization)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🎯 Overview

The **Gemini FastAPI Toolkit** is a production-grade, enterprise-ready FastAPI application that provides seamless integration with Google's Gemini API. Built with modern Python best practices, it offers comprehensive multimodal AI capabilities including text generation, image analysis, audio processing, video understanding, and advanced streaming support.

### Key Highlights

- 🚀 **Production Ready**: Battle-tested architecture with comprehensive error handling, logging, and monitoring
- 🎨 **Multimodal Support**: Unified API for text, images, audio, and video processing
- ⚡ **High Performance**: Async/await throughout, connection pooling, and intelligent caching
- 🔒 **Secure by Default**: Input validation, rate limiting, and secure file handling
- 📦 **Easy Deployment**: Docker-ready with one-command setup
- 🧪 **Well Tested**: Comprehensive test suite with high coverage
- 📚 **Fully Documented**: Extensive documentation and examples

---

## ✨ Features

### Core Capabilities

- **📝 Text Generation**
  - Advanced text generation with customizable parameters (temperature, top-p, top-k)
  - Multi-turn conversation support with context management
  - Streaming responses via Server-Sent Events (SSE)
  - Text summarization, translation, and information extraction
  - Code completion and text continuation

- **🖼️ Image Processing**
  - Comprehensive image analysis and understanding
  - Optical Character Recognition (OCR) with multi-language support
  - Automatic image captioning with style options
  - Visual question answering
  - Multi-image comparison and analysis

- **🎵 Audio Processing**
  - High-accuracy audio transcription
  - Multi-language audio translation
  - Sentiment analysis and keyword extraction
  - Speaker detection and segmentation
  - Support for WAV, MP3, MPEG formats

- **🎬 Video Analysis**
  - Frame-by-frame video description
  - Object and action detection
  - Video summarization
  - Audio extraction and transcription
  - Timeline analysis with timestamps

- **🔀 Multimodal Operations**
  - Process multiple content types simultaneously
  - Retrieval Augmented Generation (RAG) support
  - Context-aware multimodal understanding
  - Structured data extraction

### Infrastructure Features

- **⚡ Performance**
  - Async/await architecture for high concurrency
  - Intelligent caching (in-memory + Redis support)
  - Connection pooling and request optimization
  - Streaming for large responses

- **🛡️ Reliability**
  - Automatic retry with exponential backoff
  - Comprehensive error handling and recovery
  - Rate limiting with configurable thresholds
  - Health checks and monitoring endpoints

- **🔧 Developer Experience**
  - Interactive API documentation (Swagger UI & ReDoc)
  - Type hints throughout the codebase
  - Comprehensive logging with structured JSON output
  - Extensive code examples and tutorials

---

## 📦 Prerequisites

Before installing, ensure you have:

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Google Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **pip** (Python package manager)
- **Docker** (optional, for containerized deployment)
- **Redis** (optional, for distributed caching)

---

## 🚀 Installation

### Method 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gemini-fastapi-toolkit.git
cd gemini-fastapi-toolkit

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env and add your Google API key
nano .env  # or use your preferred editor
```

### Method 2: Docker Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/gemini-fastapi-toolkit.git
cd gemini-fastapi-toolkit

# Create .env file with your API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Start services with Docker Compose
docker-compose up -d
```

### Method 3: Development Installation

For contributors and developers:

```bash
# Clone and setup
git clone https://github.com/yourusername/gemini-fastapi-toolkit.git
cd gemini-fastapi-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies including dev tools
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pre-commit install

# Run tests to verify installation
pytest
```

---

## 🏃 Quick Start

### 1. Start the Server

**Local:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker:**
```bash
docker-compose up
```

### 2. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### 3. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 4. Make Your First Request

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/text/generate",
    json={
        "prompt": "Explain quantum computing in simple terms",
        "temperature": 0.7,
        "max_tokens": 200
    }
)

print(response.json()["text"])
```

---

## ⚙️ Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and customize:

### Essential Settings

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_api_key_here

# Model Selection
GEMINI_MODEL_TEXT=gemini-2.0-flash-exp
GEMINI_MODEL_VISION=gemini-2.0-flash-exp
GEMINI_MODEL_AUDIO=gemini-2.0-flash-exp
```

### Server Configuration

```env
HOST=0.0.0.0          # Server host (0.0.0.0 for all interfaces)
PORT=8000              # Server port
DEBUG=false            # Debug mode (set to true for development)
WORKERS=4              # Number of worker processes
RELOAD=false           # Auto-reload on code changes (development only)
```

### Rate Limiting

```env
RATE_LIMIT_PER_MINUTE=60     # Requests per minute per client
RATE_LIMIT_PER_HOUR=1000     # Requests per hour per client
RATE_LIMIT_ENABLED=true      # Enable/disable rate limiting
```

### File Upload Limits

```env
MAX_FILE_SIZE_MB=10          # Maximum file size in megabytes
```

### Caching

```env
ENABLE_CACHE=true                    # Enable response caching
REDIS_URL=redis://localhost:6379     # Redis connection URL (optional)
CACHE_TTL_SECONDS=3600               # Cache time-to-live
CACHE_MAX_SIZE=1000                  # Maximum cache entries
```

### CORS Configuration

```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=true
```

### Logging

```env
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json          # json or text
```

See `.env.example` for complete configuration reference.

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access:

- **Swagger UI** (`/docs`): Interactive API explorer with "Try it out" functionality
- **ReDoc** (`/redoc`): Beautiful, responsive API documentation
- **OpenAPI Schema** (`/openapi.json`): Machine-readable API specification

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/health/ready` | GET | Readiness probe |
| `/health/live` | GET | Liveness probe |
| `/api/v1/text/generate` | POST | Generate text |
| `/api/v1/text/chat` | POST | Multi-turn chat |
| `/api/v1/text/chat/stream` | POST | Streaming chat |
| `/api/v1/text/summarize` | POST | Summarize text |
| `/api/v1/text/translate` | POST | Translate text |
| `/api/v1/image/analyze` | POST | Analyze image |
| `/api/v1/image/ocr` | POST | Extract text from image |
| `/api/v1/audio/transcribe` | POST | Transcribe audio |
| `/api/v1/video/analyze` | POST | Analyze video |
| `/api/v1/multimodal/process` | POST | Process multimodal content |

For detailed API reference, see [docs/API.md](docs/API.md).

---

## 💡 Usage Examples

### Text Generation

```python
import requests

# Basic text generation
response = requests.post(
    "http://localhost:8000/api/v1/text/generate",
    json={
        "prompt": "Write a professional email to schedule a meeting",
        "temperature": 0.7,
        "max_tokens": 300
    }
)

result = response.json()
print(result["text"])
print(f"Tokens used: {result['usage']['total_tokens']}")
```

### Streaming Chat

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/text/chat/stream",
    json={
        "messages": [
            {"role": "user", "content": "Explain machine learning"}
        ],
        "temperature": 0.7
    },
    stream=True
)

print("Response: ", end="")
for line in response.iter_lines():
    if line:
        decoded = line.decode()
        if decoded.startswith("data: "):
            data = decoded[6:]
            if data:
                print(data, end="", flush=True)
```

### Image Analysis with OCR

```python
import requests

with open("document.jpg", "rb") as image_file:
    files = {"file": image_file}
    data = {"prompt": "Extract all text and analyze the document structure"}
    
    response = requests.post(
        "http://localhost:8000/api/v1/image/analyze",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Description: {result['description']}")
    if result.get('text_detected'):
        print(f"Text found: {result['text_detected']}")
```

### Audio Transcription

```python
import requests

with open("audio.wav", "rb") as audio_file:
    files = {"file": audio_file}
    data = {"language": "en", "format": "text"}
    
    response = requests.post(
        "http://localhost:8000/api/v1/audio/transcribe",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Transcription: {result['text']}")
    print(f"Duration: {result['duration']}s")
    print(f"Language: {result['language']}")
```

### Multimodal Processing

```python
import requests
import base64

# Encode image to base64
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/api/v1/multimodal/process",
    json={
        "prompt": "Analyze this image and provide insights",
        "images": [f"data:image/jpeg;base64,{image_base64}"],
        "text": "This image shows a technical diagram"
    }
)

result = response.json()
print(result["text"])
```

More examples available in the [`examples/`](examples/) directory.

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (Main Layer)  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
┌───▼───┐ ┌──▼──┐  ┌────▼───┐ ┌────▼────┐
│Router │ │Service│ │Gemini  │ │  Cache  │
│Layer  │ │Layer │ │Client  │ │ Service │
└───┬───┘ └──┬──┘ └────┬───┘ └────┬────┘
    │        │         │          │
    └────────┴─────────┴──────────┘
                │
        ┌───────▼────────┐
        │  Google Gemini │
        │      API       │
        └───────────────┘
```

### Design Principles

- **Separation of Concerns**: Clear separation between routers, services, and core logic
- **Dependency Injection**: All dependencies injected for testability
- **Async-First**: All I/O operations are asynchronous
- **Type Safety**: Comprehensive type hints throughout
- **Error Resilience**: Graceful error handling with proper exceptions
- **Performance**: Optimized for high throughput and low latency

---

## 📁 Project Structure

```
gemini-fastapi-toolkit/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── dependencies.py          # Dependency injection
│   ├── middleware.py             # Custom middleware
│   │
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── gemini_client.py     # Gemini API client wrapper
│   │   ├── exceptions.py         # Custom exception classes
│   │   ├── validators.py         # Input validation utilities
│   │   └── rate_limiter.py      # Rate limiting implementation
│   │
│   ├── models/                   # Pydantic data models
│   │   ├── __init__.py
│   │   ├── text.py               # Text generation models
│   │   ├── image.py              # Image processing models
│   │   ├── audio.py              # Audio processing models
│   │   ├── video.py              # Video processing models
│   │   └── multimodal.py        # Multimodal models
│   │
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py             # Health check endpoints
│   │   ├── text.py                # Text generation routes
│   │   ├── image.py               # Image processing routes
│   │   ├── audio.py               # Audio processing routes
│   │   ├── video.py               # Video processing routes
│   │   ├── multimodal.py         # Multimodal routes
│   │   └── streaming.py          # Streaming endpoints
│   │
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── text_service.py       # Text processing service
│   │   ├── image_service.py       # Image processing service
│   │   ├── audio_service.py       # Audio processing service
│   │   ├── video_service.py       # Video processing service
│   │   └── cache_service.py      # Caching service
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── file_handler.py        # File upload/processing utilities
│       ├── logger.py              # Logging configuration
│       └── formatters.py          # Response formatting utilities
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_text.py               # Text endpoint tests
│   ├── test_image.py              # Image endpoint tests
│   └── test_integration.py       # Integration tests
│
├── examples/                      # Example scripts
│   ├── basic_text.py              # Basic text generation example
│   ├── image_analysis.py           # Image analysis example
│   ├── streaming_chat.py          # Streaming chat example
│   └── multimodal_example.py      # Multimodal example
│
├── docs/                          # Documentation
│   ├── API.md                     # API reference
│   ├── SETUP.md                   # Setup guide
│   └── QUICKSTART.md              # Quick start guide
│
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker Compose configuration
├── pyproject.toml                  # Project metadata and tool configs
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
└── README.md                      # This file
```

---

## 🚢 Deployment

### Production Deployment

#### Using Docker

```bash
# Build production image
docker build -t gemini-fastapi-toolkit:latest .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  -e WORKERS=4 \
  -e DEBUG=false \
  --name gemini-api \
  gemini-fastapi-toolkit:latest
```

#### Using Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f api

# Scale workers
docker-compose up -d --scale api=4
```

#### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY=your_key
export WORKERS=4
export DEBUG=false

# Run with Gunicorn (recommended for production)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Environment-Specific Configuration

- **Development**: Use `RELOAD=true` for hot-reloading
- **Staging**: Enable detailed logging, disable caching for testing
- **Production**: Use multiple workers, enable caching, disable debug mode

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_text.py

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Test Structure

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints end-to-end
- **Mocked External APIs**: Gemini API calls are mocked in tests

### Writing Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_text_generation(client: TestClient):
    """Test text generation endpoint."""
    response = client.post(
        "/api/v1/text/generate",
        json={"prompt": "Hello", "max_tokens": 10}
    )
    assert response.status_code == 200
    assert "text" in response.json()
```

---

## ⚡ Performance & Optimization

### Performance Best Practices

1. **Enable Caching**: Use Redis for distributed caching in production
   ```env
   ENABLE_CACHE=true
   REDIS_URL=redis://your-redis-host:6379
   ```

2. **Optimize Workers**: Adjust worker count based on CPU cores
   ```env
   WORKERS=4  # Typically 2-4x CPU cores
   ```

3. **Use Streaming**: For long responses, use streaming endpoints
   ```python
   # Use /api/v1/text/chat/stream instead of /api/v1/text/chat
   ```

4. **Connection Pooling**: Already enabled in the Gemini client

5. **Batch Processing**: For multiple requests, use async batching
   ```python
   import asyncio
   
   async def batch_generate(prompts):
       tasks = [generate_text(p) for p in prompts]
       return await asyncio.gather(*tasks)
   ```

### Monitoring

- **Health Endpoints**: Use `/health/ready` and `/health/live` for monitoring
- **Logging**: Structured JSON logs for easy parsing
- **Metrics**: Request timing in response headers (`X-Process-Time`)

---

## 🔒 Security

### Security Features

- ✅ Input validation on all endpoints
- ✅ File type and size validation
- ✅ Rate limiting to prevent abuse
- ✅ Secure file handling with cleanup
- ✅ Environment variable protection
- ✅ CORS configuration
- ✅ Error message sanitization

### Security Best Practices

1. **API Key Protection**
   ```bash
   # Never commit .env files
   # Use environment variables or secret management
   ```

2. **Rate Limiting**
   ```env
   # Configure appropriate limits
   RATE_LIMIT_PER_MINUTE=60
   RATE_LIMIT_PER_HOUR=1000
   ```

3. **File Upload Security**
   ```env
   # Set appropriate file size limits
   MAX_FILE_SIZE_MB=10
   ```

4. **CORS Configuration**
   ```env
   # Restrict to specific origins in production
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

5. **HTTPS**: Always use HTTPS in production with a reverse proxy

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: API Key Not Working

**Symptoms**: `401 Unauthorized` or `AuthenticationError`

**Solutions**:
```bash
# Verify API key in .env
echo $GOOGLE_API_KEY

# Check API key in Google AI Studio
# Ensure billing is enabled if required
```

#### Issue: Rate Limit Exceeded

**Symptoms**: `429 Too Many Requests`

**Solutions**:
```env
# Increase rate limits in .env
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=2000

# Or disable for development
RATE_LIMIT_ENABLED=false
```

#### Issue: File Upload Fails

**Symptoms**: `FileProcessingError` or `413 Payload Too Large`

**Solutions**:
```env
# Increase file size limit
MAX_FILE_SIZE_MB=20

# Check file format is supported
# Verify MIME type is allowed
```

#### Issue: Redis Connection Error

**Symptoms**: Cache warnings in logs

**Solutions**:
```env
# Disable Redis if not available
ENABLE_CACHE=false

# Or fix Redis connection
REDIS_URL=redis://localhost:6379
```

#### Issue: Port Already in Use

**Symptoms**: `Address already in use`

**Solutions**:
```bash
# Change port in .env
PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

### Debug Mode

Enable debug mode for detailed error messages:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Getting Help

- 📖 Check [docs/SETUP.md](docs/SETUP.md) for detailed setup
- 📚 Review [docs/API.md](docs/API.md) for API issues
- 🐛 Open an issue on GitHub
- 💬 Join our community discussions

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Contribution Process

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** following our coding standards
4. **Write or update tests**
5. **Ensure all tests pass**
   ```bash
   pytest
   ```
6. **Commit with descriptive messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Coding Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for all public functions
- Maintain test coverage above 80%
- Use `black` for code formatting
- Run `ruff` for linting

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

### Getting Help

- 📖 **Documentation**: Check the [`docs/`](docs/) directory
- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/gemini-fastapi-toolkit/issues)
- 💡 **Feature Requests**: [Open a discussion](https://github.com/yourusername/gemini-fastapi-toolkit/discussions)
- 📧 **Email**: support@yourdomain.com (if applicable)

### Resources

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- Powered by [Google Gemini](https://ai.google.dev/) - Advanced AI capabilities
- Inspired by the open-source community

### Special Thanks

- Contributors and developers who made this project possible
- Early adopters and beta testers
- The open-source community for amazing tools and libraries

---

<div align="center">

**Made with ❤️ by Shrinjay Shresth**

⭐ Star this repo if you find it useful!

[⬆ Back to Top](#-gemini-fastapi-toolkit)

</div>
