# Setup Guide

## Prerequisites

- Python 3.10+
- Google Cloud account with Gemini API access
- (Optional) Docker and Docker Compose

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

## Docker Setup

```bash
docker-compose up -d
```

## Troubleshooting

### API Key Issues

- Verify your API key is correct
- Check API key permissions in Google Cloud Console
- Ensure billing is enabled if required

### Port Already in Use

Change the port in `.env`:
```
PORT=8001
```

### Redis Connection Issues

If Redis is not available, the app will fall back to in-memory caching.

