"""Streaming endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.gemini_client import GeminiClient
from app.dependencies import get_gemini_client
from app.models.text import TextGenerationRequest
from app.utils.formatters import format_stream_chunk

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/streaming", tags=["streaming"])


@router.post("/text")
async def stream_text(
    request: TextGenerationRequest,
    client: GeminiClient = Depends(get_gemini_client),
):
    """Stream text generation."""
    try:
        async def generate_stream():
            async for chunk in client.generate_text_stream(
                request.prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model_name=request.model,
            ):
                yield format_stream_chunk(chunk, finish=False)
            yield format_stream_chunk("", finish=True)

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"Streaming failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

