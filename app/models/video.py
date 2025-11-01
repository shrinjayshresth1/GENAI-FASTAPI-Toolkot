"""Pydantic models for video processing endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VideoAnalysisRequest(BaseModel):
    """Request model for video analysis."""

    prompt: str = Field(
        "Analyze this video", min_length=1, description="Analysis prompt"
    )
    analysis_type: str = Field(
        "summary",
        pattern="^(summary|detailed|objects|actions)$",
        description="Type of analysis to perform",
    )
    frame_interval: int = Field(
        30, gt=0, description="Process every N frames (1 = process all frames)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What happens in this video?",
                "analysis_type": "summary",
                "frame_interval": 30,
            }
        }


class DetectedObject(BaseModel):
    """Detected object in video frame."""

    name: str = Field(..., description="Object name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    frame_number: int = Field(..., ge=0, description="Frame number")
    timestamp: float = Field(..., ge=0.0, description="Timestamp in seconds")
    bounding_box: Optional[Dict[str, Any]] = Field(
        None, description="Bounding box coordinates"
    )


class DetectedAction(BaseModel):
    """Detected action in video."""

    action: str = Field(..., description="Action description")
    start_time: float = Field(..., ge=0.0, description="Start time in seconds")
    end_time: float = Field(..., ge=0.0, description="End time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Action confidence")


class VideoAnalysisResponse(BaseModel):
    """Response model for video analysis."""

    summary: str = Field(..., description="Video summary")
    objects: List[str] = Field(
        default_factory=list, description="List of detected objects"
    )
    objects_detailed: List[DetectedObject] = Field(
        default_factory=list, description="Detailed object detections"
    )
    actions: List[str] = Field(
        default_factory=list, description="List of detected actions"
    )
    actions_detailed: List[DetectedAction] = Field(
        default_factory=list, description="Detailed action detections"
    )
    timestamps: List[Dict[str, Any]] = Field(
        default_factory=list, description="Key timestamps with descriptions"
    )
    duration: float = Field(..., ge=0.0, description="Video duration in seconds")
    frame_count: int = Field(..., ge=0, description="Total number of frames")
    fps: Optional[float] = Field(None, ge=0.0, description="Frames per second")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "This video shows a person walking through a park...",
                "objects": ["person", "tree", "bench"],
                "actions": ["walking", "sitting"],
                "timestamps": [
                    {"time": 5.0, "description": "Person enters frame"},
                    {"time": 30.0, "description": "Person sits on bench"},
                ],
                "duration": 60.0,
                "frame_count": 1800,
                "fps": 30.0,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class VideoDescribeRequest(BaseModel):
    """Request model for frame-by-frame video description."""

    frame_interval: int = Field(
        30, gt=0, description="Describe every N frames"
    )
    include_timestamps: bool = Field(True, description="Include timestamps in descriptions")

    class Config:
        json_schema_extra = {
            "example": {
                "frame_interval": 30,
                "include_timestamps": True,
            }
        }


class FrameDescription(BaseModel):
    """Description of a single video frame."""

    frame_number: int = Field(..., ge=0, description="Frame number")
    timestamp: float = Field(..., ge=0.0, description="Timestamp in seconds")
    description: str = Field(..., description="Frame description")


class VideoDescribeResponse(BaseModel):
    """Response model for frame-by-frame description."""

    frames: List[FrameDescription] = Field(
        ..., description="Frame descriptions"
    )
    total_frames: int = Field(..., ge=0, description="Total frames processed")
    duration: float = Field(..., ge=0.0, description="Video duration")
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "frames": [
                    {
                        "frame_number": 0,
                        "timestamp": 0.0,
                        "description": "A person standing in a park",
                    },
                    {
                        "frame_number": 30,
                        "timestamp": 1.0,
                        "description": "The person starts walking",
                    },
                ],
                "total_frames": 60,
                "duration": 2.0,
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }


class VideoExtractAudioRequest(BaseModel):
    """Request model for extracting and transcribing audio from video."""

    transcription_language: Optional[str] = Field(
        "auto", description="Language for transcription (auto-detect if 'auto')"
    )
    include_timestamps: bool = Field(True, description="Include timestamps in transcription")

    class Config:
        json_schema_extra = {
            "example": {
                "transcription_language": "en",
                "include_timestamps": True,
            }
        }


class VideoExtractAudioResponse(BaseModel):
    """Response model for extracted audio transcription."""

    transcription: str = Field(..., description="Audio transcription")
    language: str = Field(..., description="Detected language")
    duration: float = Field(..., ge=0.0, description="Audio duration")
    segments: List[Dict[str, Any]] = Field(
        default_factory=list, description="Transcription segments with timestamps"
    )
    model: str = Field(..., description="Model used")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "transcription": "Hello, welcome to this video...",
                "language": "en",
                "duration": 120.0,
                "segments": [
                    {
                        "text": "Hello, welcome",
                        "start": 0.0,
                        "end": 2.5,
                    }
                ],
                "model": "gemini-2.0-flash-exp",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }

