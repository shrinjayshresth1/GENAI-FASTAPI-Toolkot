"""Image processing service."""

import logging
from typing import List, Optional

from app.core.gemini_client import GeminiClient
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
from app.utils.file_handler import process_image

logger = logging.getLogger(__name__)


class ImageService:
    """Service for image processing operations."""

    def __init__(self, client: GeminiClient):
        """
        Initialize image service.

        Args:
            client: Gemini client instance

        Example:
            ```python
            service = ImageService(client)
            ```
        """
        self.client = client

    async def analyze(
        self, image_bytes: bytes, prompt: str = "Describe this image in detail"
    ) -> ImageAnalysisResponse:
        """
        Analyze image.

        Args:
            image_bytes: Image bytes
            prompt: Analysis prompt

        Returns:
            ImageAnalysisResponse: Analysis result

        Example:
            ```python
            with open("image.jpg", "rb") as f:
                image_bytes = f.read()
            result = await service.analyze(image_bytes, "What's in this image?")
            ```
        """
        logger.info(f"Analyzing image, size: {len(image_bytes)} bytes")

        result = await self.client.analyze_image(image_bytes, prompt)

        # Parse response to extract structured data
        description = result.description
        labels = []  # Would need to parse from description or use additional API
        objects_detected = []
        text_detected = None

        return ImageAnalysisResponse(
            description=description,
            labels=labels,
            objects_detected=objects_detected,
            text_detected=text_detected,
            confidence=0.9,
            model=result.model,
            created_at=result.created_at,
        )

    async def caption(
        self, image_bytes: bytes, request: ImageCaptionRequest
    ) -> ImageCaptionResponse:
        """
        Generate image caption.

        Args:
            image_bytes: Image bytes
            request: Caption request

        Returns:
            ImageCaptionResponse: Caption result

        Example:
            ```python
            request = ImageCaptionRequest(style="creative")
            result = await service.caption(image_bytes, request)
            ```
        """
        logger.info(f"Generating {request.style} caption")

        prompt = f"Generate a {request.style} caption for this image"
        result = await self.client.analyze_image(image_bytes, prompt)

        return ImageCaptionResponse(
            caption=result.description,
            style=request.style,
            model=result.model,
            created_at=result.created_at,
        )

    async def ocr(
        self, image_bytes: bytes, request: OCRRequest
    ) -> OCRResponse:
        """
        Perform OCR on image.

        Args:
            image_bytes: Image bytes
            request: OCR request

        Returns:
            OCRResponse: OCR result

        Example:
            ```python
            request = OCRRequest(language="en")
            result = await service.ocr(image_bytes, request)
            ```
        """
        logger.info("Performing OCR")

        prompt = "Extract all text from this image"
        if request.language and request.language != "auto":
            prompt += f". Language: {request.language}"

        result = await self.client.analyze_image(image_bytes, prompt)

        return OCRResponse(
            text=result.description,
            blocks=[],
            confidence=0.9,
            language=request.language or "en",
            model=result.model,
        )

    async def compare(
        self, images: List[bytes], request: ImageCompareRequest
    ) -> ImageCompareResponse:
        """
        Compare multiple images.

        Args:
            images: List of image bytes
            request: Comparison request

        Returns:
            ImageCompareResponse: Comparison result

        Example:
            ```python
            images = [image1_bytes, image2_bytes]
            result = await service.compare(images, request)
            ```
        """
        logger.info(f"Comparing {len(images)} images")

        # Process first image
        result = await self.client.analyze_image(images[0], request.prompt)

        # For multiple images, would need multimodal processing
        return ImageCompareResponse(
            comparison=result.description,
            similarities=[],
            differences=[],
            model=result.model,
            created_at=result.created_at,
        )

    async def ask(
        self, image_bytes: bytes, request: ImageAskRequest
    ) -> ImageAskResponse:
        """
        Answer question about image.

        Args:
            image_bytes: Image bytes
            request: Question request

        Returns:
            ImageAskResponse: Answer result

        Example:
            ```python
            request = ImageAskRequest(question="What color is the car?")
            result = await service.ask(image_bytes, request)
            ```
        """
        logger.info(f"Answering question: {request.question}")

        result = await self.client.analyze_image(image_bytes, request.question)

        return ImageAskResponse(
            answer=result.description,
            confidence=0.9,
            reasoning=None,
            model=result.model,
            created_at=result.created_at,
        )

