"""Pydantic models for multimodal processing endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MultimodalRequest(BaseModel):
    """Request model for multimodal processing."""

    prompt: str = Field(..., min_length=1, description="Processing prompt")
    images: Optional[List[str]] = Field(
        None, description="List of image URLs or base64 encoded images"
    )
    audio: Optional[str] = Field(
        None, description="Audio URL or base64 encoded audio"
    )
    video: Optional[str] = Field(
        None, description="Video URL or path"
    )
    documents: Optional[List[str]] = Field(
        None, description="List of document URLs or base64 encoded documents"
    )
    text: Optional[str] = Field(None, description="Additional text input")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Analyze this content and provide insights",
                "images": ["https://example.com/image.jpg"],
                "text": "This is related text",
            }
        }


class MultimodalResponse(BaseModel):
    """Response model for multimodal processing."""

    text: str = Field(..., description="Generated text response")
    structured_data: Optional[Dict[str, Any]] = Field(
        None, description="Structured data extracted from content"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Processing confidence"
    )
    sources_used: List[str] = Field(
        default_factory=list, description="List of sources that were used"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Based on the provided image and text, I can see...",
                "structured_data": {
                    "entities": ["entity1", "entity2"],
                    "topics": ["topic1", "topic2"],
                },
                "confidence": 0.92,
                "sources_used": ["image", "text"],
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class RAGRequest(BaseModel):
    """Request model for Retrieval Augmented Generation."""

    query: str = Field(..., min_length=1, description="Search query")
    context_documents: List[str] = Field(
        ..., min_items=1, description="List of context documents (text or URLs)"
    )
    max_context_length: Optional[int] = Field(
        None, gt=0, description="Maximum context length to use"
    )
    top_k: int = Field(5, gt=0, le=20, description="Number of relevant documents to retrieve")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main topic?",
                "context_documents": [
                    "Document 1 content here...",
                    "Document 2 content here...",
                ],
                "max_context_length": 2000,
                "top_k": 3,
            }
        }


class RAGResponse(BaseModel):
    """Response model for Retrieval Augmented Generation."""

    answer: str = Field(..., description="Generated answer")
    relevant_documents: List[Dict[str, Any]] = Field(
        default_factory=list, description="Relevant documents used"
    )
    citations: List[str] = Field(
        default_factory=list, description="Citation references"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Answer confidence"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Based on the provided documents, the main topic is...",
                "relevant_documents": [
                    {
                        "content": "Document excerpt...",
                        "relevance_score": 0.95,
                        "source": "doc1",
                    }
                ],
                "citations": ["doc1", "doc2"],
                "confidence": 0.88,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }

