# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install

```bash
pip install -r requirements.txt
```

## Step 2: Configure

```bash
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

## Step 3: Run

```bash
uvicorn app.main:app --reload
```

## Step 4: Test

```bash
curl http://localhost:8000/health
```

## First API Call

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/text/generate",
    json={"prompt": "Hello, world!"}
)

print(response.json())
```

## Next Steps

- Explore API docs at http://localhost:8000/docs
- Check out examples in `examples/` directory
- Read full API documentation in `docs/API.md`

