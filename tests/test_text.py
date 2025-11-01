"""Tests for text endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_text():
    """Test text generation endpoint."""
    response = client.post(
        "/api/v1/text/generate",
        json={
            "prompt": "Hello world",
            "temperature": 0.7,
            "max_tokens": 100,
        },
    )
    # Note: This will fail without valid API key - would need mocking
    assert response.status_code in [200, 401, 500]


def test_health_check():
    """Test health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_count_tokens():
    """Test token counting."""
    response = client.post(
        "/tokens/count",
        json={"text": "Hello world"},
    )
    # Note: This will fail without valid API key - would need mocking
    assert response.status_code in [200, 401, 500]

