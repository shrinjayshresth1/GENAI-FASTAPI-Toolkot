"""Image processing API endpoints."""

import logging
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.core.exceptions import FileProcessingError
from app.dependencies import get_image_service
from app.models.image import (
    ImageAnalysisResponse,
    ImageAskRequest,
    ImageAskResponse,
    ImageCaptionRequest,
    ImageCaptionResponse,
    ImageCompareRequest,
    ImageCompareResponse,
    OCRRequest,
    OCRResponse,
)
from app.services.image_service import ImageService
from app.utils.file_handler import cleanup_temp_file, validate_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/image", tags=["image"])


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = "Describe this image in detail",
    service: ImageService = Depends(get_image_service),
    settings = Depends(get_settings),
) -> ImageAnalysisResponse:
    """Analyze image."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_IMAGE_TYPES, settings)
        image_bytes = await file.read()
        await file.close()
        return await service.analyze(image_bytes, prompt)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/caption", response_model=ImageCaptionResponse)
async def caption_image(
    file: UploadFile = File(...),
    style: str = "descriptive",
    service: ImageService = Depends(get_image_service),
    settings = Depends(get_settings),
) -> ImageCaptionResponse:
    """Generate image caption."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_IMAGE_TYPES, settings)
        image_bytes = await file.read()
        await file.close()
        request_obj = ImageCaptionRequest(style=style)
        return await service.caption(image_bytes, request_obj)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Caption generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr", response_model=OCRResponse)
async def ocr_image(
    file: UploadFile = File(...),
    request: OCRRequest = Depends(),
    service: ImageService = Depends(get_image_service),
    settings = Depends(get_settings),
) -> OCRResponse:
    """Extract text from image."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_IMAGE_TYPES, settings)
        image_bytes = await file.read()
        await file.close()
        return await service.ocr(image_bytes, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"OCR failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ImageCompareResponse)
async def compare_images(
    files: List[UploadFile] = File(...),
    request: ImageCompareRequest = Depends(),
    service: ImageService = Depends(get_image_service),
    settings = Depends(get_settings),
) -> ImageCompareResponse:
    """Compare multiple images."""
    try:
        images = []
        for file in files:
            await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_IMAGE_TYPES, settings)
            image_bytes = await file.read()
            images.append(image_bytes)
            await file.close()
        return await service.compare(images, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image comparison failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=ImageAskResponse)
async def ask_image(
    file: UploadFile = File(...),
    request: ImageAskRequest = Depends(),
    service: ImageService = Depends(get_image_service),
    settings = Depends(get_settings),
) -> ImageAskResponse:
    """Answer question about image."""
    try:
        await validate_file(file, settings.MAX_FILE_SIZE_MB, settings.ALLOWED_IMAGE_TYPES, settings)
        image_bytes = await file.read()
        await file.close()
        return await service.ask(image_bytes, request)
    except FileProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image Q&A failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

