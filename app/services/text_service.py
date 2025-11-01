"""Text generation service."""

import hashlib
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.gemini_client import GeminiClient
from app.models.text import (
    ChatMessage,
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
from app.services.cache_service import CacheService, get_cache_service

logger = logging.getLogger(__name__)


class TextService:
    """Service for text generation operations."""

    def __init__(
        self,
        client: GeminiClient,
        cache: Optional[CacheService] = None,
    ):
        """
        Initialize text service.

        Args:
            client: Gemini client instance
            cache: Cache service instance (optional)

        Example:
            ```python
            service = TextService(client)
            ```
        """
        self.client = client
        self.cache = cache or get_cache_service()
        self._conversations: Dict[str, List[ChatMessage]] = {}

    def _get_cache_key(self, prompt: str, **kwargs: Any) -> str:
        """Generate cache key from prompt and parameters."""
        key_data = {"prompt": prompt, **kwargs}
        key_str = str(sorted(key_data.items()))
        return hashlib.md5(key_str.encode()).hexdigest()

    async def generate(
        self, request: TextGenerationRequest
    ) -> TextGenerationResponse:
        """
        Generate text from prompt.

        Args:
            request: Text generation request

        Returns:
            TextGenerationResponse: Generated text response

        Example:
            ```python
            request = TextGenerationRequest(prompt="Write a story")
            response = await service.generate(request)
            ```
        """
        logger.info(f"Generating text, prompt length: {len(request.prompt)}")

        # Check cache
        cache_key = self._get_cache_key(
            request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model=request.model,
        )
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info("Returning cached result")
            return TextGenerationResponse(**cached)

        # Generate text
        result = await self.client.generate_text(
            request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            top_k=request.top_k,
            stop_sequences=request.stop_sequences,
            model_name=request.model,
        )

        # Create response
        response = TextGenerationResponse(
            text=result.text,
            model=result.model,
            usage=result.usage,
            finish_reason=result.finish_reason,
            created_at=result.created_at,
        )

        # Cache result
        await self.cache.set(cache_key, response.model_dump())

        return response

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Handle chat conversation.

        Args:
            request: Chat request

        Returns:
            ChatResponse: Chat response

        Example:
            ```python
            request = ChatRequest(messages=[ChatMessage(role="user", content="Hello")])
            response = await service.chat(request)
            ```
        """
        logger.info(f"Processing chat with {len(request.messages)} messages")

        # Build conversation context
        conversation_text = ""
        for msg in request.messages:
            conversation_text += f"{msg.role}: {msg.content}\n"

        # Add system instruction if provided
        if request.system_instruction:
            conversation_text = f"System: {request.system_instruction}\n{conversation_text}"

        # Generate response
        result = await self.client.generate_text(
            conversation_text,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model_name=request.model,
        )

        # Create response
        conversation_id = str(uuid.uuid4())
        response_message = ChatMessage(
            role="assistant",
            content=result.text,
        )

        # Store conversation
        self._conversations[conversation_id] = request.messages + [response_message]

        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            usage=result.usage,
            model=result.model,
        )

    async def summarize(
        self, request: SummarizeRequest
    ) -> SummarizeResponse:
        """
        Summarize text.

        Args:
            request: Summarization request

        Returns:
            SummarizeResponse: Summary response

        Example:
            ```python
            request = SummarizeRequest(text="Long text...")
            response = await service.summarize(request)
            ```
        """
        logger.info(f"Summarizing text, length: {len(request.text)}")

        prompt = f"Summarize the following text in a {request.style} style"
        if request.max_length:
            prompt += f" in approximately {request.max_length} words"

        prompt += f":\n\n{request.text}"

        result = await self.client.generate_text(prompt)

        original_length = len(request.text)
        summary_length = len(result.text)
        compression_ratio = summary_length / original_length if original_length > 0 else 0

        return SummarizeResponse(
            summary=result.text,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
        )

    async def translate(
        self, request: TranslateRequest
    ) -> TranslateResponse:
        """
        Translate text.

        Args:
            request: Translation request

        Returns:
            TranslateResponse: Translation response

        Example:
            ```python
            request = TranslateRequest(text="Hello", target_language="es")
            response = await service.translate(request)
            ```
        """
        logger.info(
            f"Translating text from {request.source_language or 'auto'} to {request.target_language}"
        )

        source_lang = request.source_language or "auto"
        prompt = f"Translate the following text from {source_lang} to {request.target_language}: {request.text}"

        result = await self.client.generate_text(prompt)

        # Detect source language (simplified)
        detected_source = request.source_language or "en"

        return TranslateResponse(
            translated_text=result.text,
            source_language=detected_source,
            target_language=request.target_language,
            confidence=0.9,
        )

    async def extract(
        self, request: ExtractRequest
    ) -> ExtractResponse:
        """
        Extract information from text.

        Args:
            request: Extraction request

        Returns:
            ExtractResponse: Extraction response

        Example:
            ```python
            request = ExtractRequest(text="John works at Google", extraction_type="entities")
            response = await service.extract(request)
            ```
        """
        logger.info(f"Extracting {request.extraction_type} from text")

        prompt = f"Extract {request.extraction_type} from the following text and return in {request.format} format:\n\n{request.text}"

        result = await self.client.generate_text(prompt)

        # Parse extracted data (simplified - would need proper parsing)
        try:
            import json

            extracted_data = json.loads(result.text)
        except Exception:
            extracted_data = {"raw": result.text}

        return ExtractResponse(
            extracted_data=extracted_data,
            extraction_type=request.extraction_type,
            confidence=0.85,
        )

    async def complete(
        self, request: CompleteRequest
    ) -> CompleteResponse:
        """
        Complete text/code.

        Args:
            request: Completion request

        Returns:
            CompleteResponse: Completion response

        Example:
            ```python
            request = CompleteRequest(prompt="def fibonacci(n):")
            response = await service.complete(request)
            ```
        """
        logger.info("Completing text/code")

        prompt = request.prompt
        if request.context:
            prompt = f"Context: {request.context}\n\n{prompt}"
        if request.language:
            prompt = f"Complete the following {request.language} code:\n\n{prompt}"

        result = await self.client.generate_text(prompt, temperature=0.3)

        return CompleteResponse(
            completion=result.text,
            model=result.model,
            usage=result.usage,
        )

