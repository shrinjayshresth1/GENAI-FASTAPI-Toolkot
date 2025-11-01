"""Audio processing API endpoints."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import get_settings
from app.core.exceptions import FileProcessingError
from app.dependencies import get_audio_service
from app.models.audio import (
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    AudioTranslateRequest,
    AudioTranslateResponse,
)
from app.services.audio_service import AudioService
from app.utils.file_handler import validate_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/audio", tags=["audio"])


@router.post("/transcribe", response_model=AudioTranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "auto",
    format: str = "text",
    service: AudioService = Depends(get_audio_service),
    settings = Depends(get_settings),
) -> AudioTranscriptionResponse:
    """Transcribe audio to text."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_AUDIO_TYPES, settings)
        audio_bytes = await file.read()
        await file.close()
        request_obj = AudioTranscriptionRequest(language=language, format=format)
        return await service.transcribe(audio_bytes, request_obj)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audio transcription failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    file: UploadFile = File(...),
    request: AudioAnalysisRequest = Depends(),
    service: AudioService = Depends(get_audio_service),
    settings = Depends(get_settings),
) -> AudioAnalysisResponse:
    """Analyze audio."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_AUDIO_TYPES, settings)
        audio_bytes = await file.read()
        await file.close()
        return await service.analyze(audio_bytes, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audio analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=AudioTranslateResponse)
async def translate_audio(
    file: UploadFile = File(...),
    request: AudioTranslateRequest = Depends(),
    service: AudioService = Depends(get_audio_service),
    settings = Depends(get_settings),
) -> AudioTranslateResponse:
    """Translate audio."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_AUDIO_TYPES, settings)
        audio_bytes = await file.read()
        await file.close()
        return await service.translate(audio_bytes, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audio translation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

