"""Video processing API endpoints."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import get_settings
from app.core.exceptions import FileProcessingError
from app.dependencies import get_video_service
from app.models.video import (
    VideoAnalysisRequest,
    VideoAnalysisResponse,
    VideoDescribeRequest,
    VideoDescribeResponse,
    VideoExtractAudioRequest,
    VideoExtractAudioResponse,
)
from app.services.video_service import VideoService
from app.utils.file_handler import cleanup_temp_file, save_temp_file, validate_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video", tags=["video"])


@router.post("/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    request: VideoAnalysisRequest = Depends(),
    service: VideoService = Depends(get_video_service),
    settings = Depends(get_settings),
) -> VideoAnalysisResponse:
    """Analyze video."""
    temp_path = None
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_VIDEO_TYPES, settings)
        temp_path = await save_temp_file(file)
        result = await service.analyze(temp_path, request)
        return result
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path:
            await cleanup_temp_file(temp_path)


@router.post("/describe", response_model=VideoDescribeResponse)
async def describe_video(
    file: UploadFile = File(...),
    request: VideoDescribeRequest = Depends(),
    service: VideoService = Depends(get_video_service),
    settings = Depends(get_settings),
) -> VideoDescribeResponse:
    """Describe video frame-by-frame."""
    temp_path = None
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_VIDEO_TYPES, settings)
        temp_path = await save_temp_file(file)
        return await service.describe(temp_path, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video description failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path:
            await cleanup_temp_file(temp_path)


@router.post("/extract-audio", response_model=VideoExtractAudioResponse)
async def extract_audio(
    file: UploadFile = File(...),
    request: VideoExtractAudioRequest = Depends(),
    service: VideoService = Depends(get_video_service),
    settings = Depends(get_settings),
) -> VideoExtractAudioResponse:
    """Extract and transcribe audio from video."""
    temp_path = None
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_VIDEO_TYPES, settings)
        temp_path = await save_temp_file(file)
        return await service.extract_audio(temp_path, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path:
            await cleanup_temp_file(temp_path)

