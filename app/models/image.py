"""Pydantic models for image processing endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImageAnalysisRequest(BaseModel):
    """Request model for image analysis."""

    prompt: str = Field(
        "Describe this image in detail",
        min_length=1,
        description="Analysis prompt",
    )
    detail_level: str = Field(
        "auto", pattern="^(low|high|auto)$", description="Detail level for analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What objects are visible in this image?",
                "detail_level": "high",
            }
        }


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis."""

    description: str = Field(..., description="Image description")
    labels: List[str] = Field(default_factory=list, description="Detected labels")
    objects_detected: List[Dict[str, Any]] = Field(
        default_factory=list, description="Detected objects with metadata"
    )
    text_detected: Optional[str] = Field(None, description="Text found in image")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Analysis confidence"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "description": "A beautiful sunset over the ocean...",
                "labels": ["sunset", "ocean", "sky"],
                "objects_detected": [{"name": "sun", "confidence": 0.95}],
                "text_detected": None,
                "confidence": 0.92,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class ImageCaptionRequest(BaseModel):
    """Request model for image captioning."""

    style: str = Field(
        "descriptive",
        pattern="^(descriptive|creative|technical)$",
        description="Caption style",
    )

    class Config:
        json_schema_extra = {"example": {"style": "creative"}}


class ImageCaptionResponse(BaseModel):
    """Response model for image captioning."""

    caption: str = Field(..., description="Generated caption")
    style: str = Field(..., description="Caption style used")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "caption": "A serene sunset painting the sky in hues of orange and pink",
                "style": "creative",
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class OCRRequest(BaseModel):
    """Request model for optical character recognition."""

    language: Optional[str] = Field(
        "auto", description="Language code for OCR (auto-detect if 'auto')"
    )

    class Config:
        json_schema_extra = {"example": {"language": "en"}}


class OCRResponse(BaseModel):
    """Response model for optical character recognition."""

    text: str = Field(..., description="Extracted text")
    blocks: List[Dict[str, Any]] = Field(
        default_factory=list, description="Text blocks with positions"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="OCR confidence"
    )
    language: str = Field(..., description="Detected language")
    model: str = Field(..., description="Model used")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello World",
                "blocks": [
                    {
                        "text": "Hello",
                        "position": {"x": 10, "y": 20, "width": 50, "height": 30},
                    }
                ],
                "confidence": 0.98,
                "language": "en",
                "model": "gemini-2.0-flash-exp",
            }
        }


class ImageCompareRequest(BaseModel):
    """Request model for comparing multiple images."""

    prompt: str = Field(
        "Compare these images",
        min_length=1,
        description="Comparison prompt",
    )

    class Config:
        json_schema_extra = {
            "example": {"prompt": "What are the differences between these images?"}
        }


class ImageCompareResponse(BaseModel):
    """Response model for image comparison."""

    comparison: str = Field(..., description="Comparison analysis")
    similarities: List[str] = Field(
        default_factory=list, description="List of similarities"
    )
    differences: List[str] = Field(
        default_factory=list, description="List of differences"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "comparison": "Both images show sunsets, but image 1 has more clouds...",
                "similarities": ["Both contain sunset", "Both have ocean views"],
                "differences": ["Different cloud formations", "Different color palettes"],
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class ImageAskRequest(BaseModel):
    """Request model for visual question answering."""

    question: str = Field(..., min_length=1, description="Question about the image")

    class Config:
        json_schema_extra = {"example": {"question": "What color is the car?"}}


class ImageAskResponse(BaseModel):
    """Response model for visual question answering."""

    answer: str = Field(..., description="Answer to the question")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Answer confidence"
    )
    reasoning: Optional[str] = Field(None, description="Reasoning for the answer")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The car is red",
                "confidence": 0.95,
                "reasoning": "The image clearly shows a red colored vehicle",
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }

