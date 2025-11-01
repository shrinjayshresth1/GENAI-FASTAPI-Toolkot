"""Text generation API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.exceptions import GeminiAPIError, RateLimitError
from app.dependencies import get_gemini_client, get_text_service
from app.models.text import (
    ChatRequest,
    ChatResponse,
    CompleteRequest,
    CompleteResponse,
    ExtractRequest,
    ExtractResponse,
    SummarizeRequest,
    SummarizeResponse,
    TextGenerationRequest,
    TextGenerationResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.services.text_service import TextService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/text", tags=["text"])


@router.post("/generate", response_model=TextGenerationResponse)
async def generate_text(
    request: TextGenerationRequest,
    service: TextService = Depends(get_text_service),
) -> TextGenerationResponse:
    """
    Generate text from prompt.

    Args:
        request: Text generation request
        service: Text service

    Returns:
        TextGenerationResponse: Generated text

    Example:
        ```python
        import requests
        response = requests.post(
            "http://localhost:8000/api/v1/text/generate",
            json={
                "prompt": "Write a story about AI",
                "temperature": 0.8,
                "max_tokens": 500
            }
        )
        ```
    """
    try:
        return await service.generate(request)
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except GeminiAPIError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Text generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: TextService = Depends(get_text_service),
) -> ChatResponse:
    """
    Multi-turn conversation endpoint.

    Args:
        request: Chat request
        service: Text service

    Returns:
        ChatResponse: Chat response

    Example:
        ```python
        response = requests.post(
            "http://localhost:8000/api/v1/text/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ],
                "temperature": 0.7
            }
        )
        ```
    """
    try:
        return await service.chat(request)
    except Exception as e:
        logger.error(f"Chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    client = Depends(get_gemini_client),
):
    """
    Streaming chat endpoint (SSE).

    Args:
        request: Chat request
        client: Gemini client

    Returns:
        StreamingResponse: SSE stream

    Example:
        ```python
        response = requests.post(
            "http://localhost:8000/api/v1/text/chat/stream",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            stream=True
        )
        ```
    """
    try:
        from fastapi.responses import StreamingResponse
        from app.utils.formatters import format_stream_chunk

        # Build conversation text
        conversation_text = "\n".join(
            [f"{msg.role}: {msg.content}" for msg in request.messages]
        )

        async def generate_stream():
            async for chunk in client.generate_text_stream(
                conversation_text,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield format_stream_chunk(chunk, finish=False)
            yield format_stream_chunk("", finish=True)

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"Streaming chat failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming failed: {str(e)}",
        )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(
    request: SummarizeRequest,
    service: TextService = Depends(get_text_service),
) -> SummarizeResponse:
    """Summarize text."""
    try:
        return await service.summarize(request)
    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    service: TextService = Depends(get_text_service),
) -> TranslateResponse:
    """Translate text."""
    try:
        return await service.translate(request)
    except Exception as e:
        logger.error(f"Translation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract", response_model=ExtractResponse)
async def extract(
    request: ExtractRequest,
    service: TextService = Depends(get_text_service),
) -> ExtractResponse:
    """Extract information from text."""
    try:
        return await service.extract(request)
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/complete", response_model=CompleteResponse)
async def complete(
    request: CompleteRequest,
    service: TextService = Depends(get_text_service),
) -> CompleteResponse:
    """Complete text/code."""
    try:
        return await service.complete(request)
    except Exception as e:
        logger.error(f"Completion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

