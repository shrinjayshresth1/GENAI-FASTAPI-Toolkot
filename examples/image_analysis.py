"""Image analysis example."""

import requests

# API endpoint
url = "http://localhost:8000/api/v1/image/analyze"

# Image file
image_path = "image.jpg"  # Replace with your image path

# Prompt
prompt = "What objects and actions are visible in this image?"

# Make request
with open(image_path, "rb") as f:
    files = {"file": f}
    data = {"prompt": prompt}
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    result = response.json()
    print("Image Description:")
    print(result["description"])
    print(f"\nConfidence: {result['confidence']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())

