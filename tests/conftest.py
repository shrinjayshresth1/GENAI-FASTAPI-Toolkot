"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_gemini_client(monkeypatch):
    """Mock Gemini client."""
    class MockGeminiClient:
        def __init__(self, *args, **kwargs):
            pass

        async def generate_text(self, *args, **kwargs):
            class Result:
                text = "Mocked text"
                model = "gemini-2.0-flash-exp"
                usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
                finish_reason = "COMPLETE"
                created_at = None

            return Result()

        async def generate_text_stream(self, *args, **kwargs):
            async def stream():
                yield "chunk1"
                yield "chunk2"

            return stream()

        async def analyze_image(self, *args, **kwargs):
            class Result:
                description = "Mocked image description"
                model = "gemini-2.0-flash-exp"
                usage = {"prompt_tokens": 5, "completion_tokens": 15, "total_tokens": 20}
                created_at = None

            return Result()

        async def count_tokens(self, *args, **kwargs):
            return 10

    monkeypatch.setattr("app.core.gemini_client.GeminiClient", MockGeminiClient)
    return MockGeminiClient

