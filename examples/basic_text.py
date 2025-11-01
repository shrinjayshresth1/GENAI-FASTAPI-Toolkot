"""Basic text generation example."""

import requests

# API endpoint
url = "http://localhost:8000/api/v1/text/generate"

# Request data
data = {
    "prompt": "Write a short poem about artificial intelligence",
    "temperature": 0.8,
    "max_tokens": 200,
}

# Make request
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print("Generated text:")
    print(result["text"])
    print(f"\nModel: {result['model']}")
    print(f"Tokens used: {result['usage']['total_tokens']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())

