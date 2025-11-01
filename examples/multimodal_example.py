"""Multimodal processing example."""

import requests

# API endpoint
url = "http://localhost:8000/api/v1/multimodal/process"

# Multimodal request
data = {
    "prompt": "Analyze this content and provide insights",
    "text": "This is a sample document about artificial intelligence.",
    "images": [],  # Can include image URLs or base64
}

# Make request
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print("Multimodal Analysis:")
    print(result["text"])
    print(f"\nConfidence: {result['confidence']}")
    print(f"Sources used: {result['sources_used']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())

