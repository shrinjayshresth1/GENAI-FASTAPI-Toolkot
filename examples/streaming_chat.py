"""Streaming chat example."""

import requests

# API endpoint
url = "http://localhost:8000/api/v1/text/chat/stream"

# Chat messages
data = {
    "messages": [
        {"role": "user", "content": "Tell me a story about a robot"}
    ],
    "temperature": 0.7,
}

# Make streaming request
response = requests.post(url, json=data, stream=True)

print("Streaming response:")
for line in response.iter_lines():
    if line:
        decoded = line.decode()
        if decoded.startswith("data: "):
            print(decoded[6:], end="", flush=True)

print("\n")

