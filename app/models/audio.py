"""Pydantic models for audio processing endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AudioTranscriptionRequest(BaseModel):
    """Request model for audio transcription."""

    language: Optional[str] = Field(
        "auto", description="Language code (auto-detect if 'auto')"
    )
    format: str = Field(
        "text", pattern="^(text|srt|vtt|json)$", description="Output format"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "format": "text",
            }
        }


class TranscriptionSegment(BaseModel):
    """Single transcription segment."""

    text: str = Field(..., description="Segment text")
    start: float = Field(..., ge=0.0, description="Start time in seconds")
    end: float = Field(..., ge=0.0, description="End time in seconds")
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello world",
                "start": 0.0,
                "end": 2.5,
                "confidence": 0.95,
            }
        }


class AudioTranscriptionResponse(BaseModel):
    """Response model for audio transcription."""

    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    duration: float = Field(..., ge=0.0, description="Audio duration in seconds")
    segments: List[TranscriptionSegment] = Field(
        default_factory=list, description="Transcription segments"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall confidence"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello world, this is a test transcription",
                "language": "en",
                "duration": 5.5,
                "segments": [
                    {
                        "text": "Hello world",
                        "start": 0.0,
                        "end": 2.0,
                        "confidence": 0.95,
                    }
                ],
                "confidence": 0.92,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class AudioAnalysisRequest(BaseModel):
    """Request model for audio analysis."""

    analysis_type: str = Field(
        "full",
        pattern="^(full|sentiment|speakers|keywords)$",
        description="Type of analysis to perform",
    )

    class Config:
        json_schema_extra = {"example": {"analysis_type": "full"}}


class AudioAnalysisResponse(BaseModel):
    """Response model for audio analysis."""

    transcription: str = Field(..., description="Audio transcription")
    sentiment: Optional[str] = Field(
        None, description="Detected sentiment (positive/negative/neutral)"
    )
    sentiment_score: Optional[float] = Field(
        None, ge=-1.0, le=1.0, description="Sentiment score"
    )
    language: str = Field(..., description="Detected language")
    speaker_count: Optional[int] = Field(
        None, ge=1, description="Number of speakers detected"
    )
    keywords: List[str] = Field(
        default_factory=list, description="Extracted keywords"
    )
    duration: float = Field(..., ge=0.0, description="Audio duration")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transcription": "This is a sample audio transcription",
                "sentiment": "positive",
                "sentiment_score": 0.75,
                "language": "en",
                "speaker_count": 1,
                "keywords": ["sample", "audio", "test"],
                "duration": 10.5,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class AudioTranslateRequest(BaseModel):
    """Request model for audio translation."""

    target_language: str = Field(
        ..., min_length=2, max_length=5, description="Target language code"
    )
    source_language: Optional[str] = Field(
        None, description="Source language code (auto-detect if None)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "target_language": "es",
                "source_language": "en",
            }
        }


class AudioTranslateResponse(BaseModel):
    """Response model for audio translation."""

    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language")
    target_language: str = Field(..., description="Target language")
    transcription: str = Field(..., description="Original transcription")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Translation confidence"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "translated_text": "Hola mundo",
                "source_language": "en",
                "target_language": "es",
                "transcription": "Hello world",
                "confidence": 0.95,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }

