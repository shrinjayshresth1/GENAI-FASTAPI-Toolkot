"""Multimodal processing API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.gemini_client import GeminiClient
from app.dependencies import get_gemini_client
from app.models.multimodal import (
    MultimodalRequest,
    MultimodalResponse,
    RAGRequest,
    RAGResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/multimodal", tags=["multimodal"])


@router.post("/process", response_model=MultimodalResponse)
async def process_multimodal(
    request: MultimodalRequest,
    client: GeminiClient = Depends(get_gemini_client),
) -> MultimodalResponse:
    """Process multimodal content."""
    try:
        content = []
        if request.text:
            content.append(request.text)
        # Add images, audio, video processing here
        result = await client.process_multimodal(content, request.prompt)
        return MultimodalResponse(
            text=result.text,
            structured_data=None,
            confidence=0.9,
            sources_used=[],
            model=result.model,
            created_at=result.created_at,
        )
    except Exception as e:
        logger.error(f"Multimodal processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag", response_model=RAGResponse)
async def rag(
    request: RAGRequest,
    client: GeminiClient = Depends(get_gemini_client),
) -> RAGResponse:
    """Retrieval Augmented Generation."""
    try:
        # Build context from documents
        context = "\n\n".join(request.context_documents[: request.top_k])
        prompt = f"Based on the following context, answer the question:\n\nContext:\n{context}\n\nQuestion: {request.query}"

        result = await client.generate_text(prompt)

        return RAGResponse(
            answer=result.text,
            relevant_documents=[],
            citations=[],
            confidence=0.9,
            model=result.model,
            created_at=result.created_at,
        )
    except Exception as e:
        logger.error(f"RAG failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

