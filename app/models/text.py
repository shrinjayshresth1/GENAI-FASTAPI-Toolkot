"""Pydantic models for text generation endpoints."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UsageInfo(BaseModel):
    """Token usage information."""

    prompt_tokens: int = Field(..., ge=0, description="Number of prompt tokens")
    completion_tokens: int = Field(..., ge=0, description="Number of completion tokens")
    total_tokens: int = Field(..., ge=0, description="Total number of tokens")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            }
        }


class TextGenerationRequest(BaseModel):
    """Request model for text generation."""

    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="Input prompt for text generation"
    )
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Sampling temperature (0.0-2.0)"
    )
    max_tokens: Optional[int] = Field(
        None, gt=0, le=8192, description="Maximum number of tokens to generate"
    )
    top_p: Optional[float] = Field(
        0.95, ge=0.0, le=1.0, description="Nucleus sampling parameter"
    )
    top_k: Optional[int] = Field(40, gt=0, description="Top-k sampling parameter")
    stop_sequences: Optional[List[str]] = Field(
        None, description="Stop sequences for generation"
    )
    model: Optional[str] = Field(None, description="Model name to use")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a short story about artificial intelligence",
                "temperature": 0.8,
                "max_tokens": 500,
                "top_p": 0.95,
                "top_k": 40,
            }
        }


class TextGenerationResponse(BaseModel):
    """Response model for text generation."""

    text: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used for generation")
    usage: UsageInfo = Field(..., description="Token usage information")
    finish_reason: str = Field(..., description="Reason for generation completion")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Once upon a time, in a world where artificial intelligence...",
                "model": "gemini-2.0-flash-exp",
                "usage": {"prompt_tokens": 10, "completion_tokens": 200, "total_tokens": 210},
                "finish_reason": "COMPLETE",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class ChatMessage(BaseModel):
    """Single chat message."""

    role: str = Field(
        ..., pattern="^(user|assistant|system)$", description="Message role"
    )
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat/conversation."""

    messages: List[ChatMessage] = Field(
        ..., min_items=1, description="List of chat messages"
    )
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        None, gt=0, le=8192, description="Maximum tokens to generate"
    )
    system_instruction: Optional[str] = Field(
        None, description="System instruction for the conversation"
    )
    model: Optional[str] = Field(None, description="Model name to use")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "What is AI?"},
                    {"role": "assistant", "content": "AI is..."},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat/conversation."""

    message: ChatMessage = Field(..., description="Generated message")
    conversation_id: str = Field(..., description="Conversation identifier")
    usage: UsageInfo = Field(..., description="Token usage information")
    model: str = Field(..., description="Model used")

    class Config:
        json_schema_extra = {
            "example": {
                "message": {
                    "role": "assistant",
                    "content": "AI stands for Artificial Intelligence...",
                    "timestamp": "2024-01-01T00:00:00Z",
                },
                "conversation_id": "conv_123",
                "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                "model": "gemini-2.0-flash-exp",
            }
        }


class SummarizeRequest(BaseModel):
    """Request model for text summarization."""

    text: str = Field(..., min_length=1, description="Text to summarize")
    max_length: Optional[int] = Field(
        None, gt=0, description="Maximum length of summary"
    )
    style: str = Field(
        "concise", pattern="^(concise|detailed|bullets)$", description="Summary style"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Long article text here...",
                "max_length": 200,
                "style": "concise",
            }
        }


class SummarizeResponse(BaseModel):
    """Response model for text summarization."""

    summary: str = Field(..., description="Generated summary")
    original_length: int = Field(..., description="Original text length")
    summary_length: int = Field(..., description="Summary length")
    compression_ratio: float = Field(..., description="Compression ratio")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "This article discusses...",
                "original_length": 1000,
                "summary_length": 200,
                "compression_ratio": 0.2,
            }
        }


class TranslateRequest(BaseModel):
    """Request model for translation."""

    text: str = Field(..., min_length=1, description="Text to translate")
    target_language: str = Field(
        ..., min_length=2, max_length=5, description="Target language code (e.g., 'es', 'fr')"
    )
    source_language: Optional[str] = Field(
        None, min_length=2, max_length=5, description="Source language code (auto-detect if None)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, world!",
                "target_language": "es",
                "source_language": "en",
            }
        }


class TranslateResponse(BaseModel):
    """Response model for translation."""

    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Detected source language")
    target_language: str = Field(..., description="Target language")
    confidence: Optional[float] = Field(None, description="Translation confidence")

    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "¡Hola, mundo!",
                "source_language": "en",
                "target_language": "es",
                "confidence": 0.95,
            }
        }


class ExtractRequest(BaseModel):
    """Request model for information extraction."""

    text: str = Field(..., min_length=1, description="Text to extract information from")
    extraction_type: str = Field(
        "entities",
        pattern="^(entities|keywords|dates|numbers|sentiments)$",
        description="Type of information to extract",
    )
    format: str = Field(
        "json", pattern="^(json|list|text)$", description="Output format"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "John Doe works at Google since 2020...",
                "extraction_type": "entities",
                "format": "json",
            }
        }


class ExtractResponse(BaseModel):
    """Response model for information extraction."""

    extracted_data: dict = Field(..., description="Extracted information")
    extraction_type: str = Field(..., description="Type of extraction performed")
    confidence: Optional[float] = Field(None, description="Extraction confidence")

    class Config:
        json_schema_extra = {
            "example": {
                "extracted_data": {
                    "entities": ["John Doe", "Google"],
                    "dates": ["2020"],
                },
                "extraction_type": "entities",
                "confidence": 0.9,
            }
        }


class CompleteRequest(BaseModel):
    """Request model for text/code completion."""

    prompt: str = Field(..., min_length=1, description="Incomplete text/code to complete")
    context: Optional[str] = Field(None, description="Additional context")
    language: Optional[str] = Field(None, description="Programming language (for code completion)")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "def fibonacci(n):",
                "context": "Python function",
                "language": "python",
            }
        }


class CompleteResponse(BaseModel):
    """Response model for text/code completion."""

    completion: str = Field(..., description="Completed text/code")
    model: str = Field(..., description="Model used")
    usage: UsageInfo = Field(..., description="Token usage")

    class Config:
        json_schema_extra = {
            "example": {
                "completion": "    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "model": "gemini-2.0-flash-exp",
                "usage": {"prompt_tokens": 5, "completion_tokens": 20, "total_tokens": 25},
            }
        }

