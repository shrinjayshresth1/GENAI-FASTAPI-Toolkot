"""Async wrapper for Google Gemini API."""

import asyncio
import base64
import io
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerateContentResponse
from PIL import Image as PILImage
from pydantic import BaseModel

from app.config import Settings, get_settings
from app.core.exceptions import (
    AuthenticationError,
    GeminiAPIError,
    ModelNotFoundError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class TextResult(BaseModel):
    """Result from text generation."""

    text: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    created_at: datetime


class ImageResult(BaseModel):
    """Result from image analysis."""

    description: str
    model: str
    usage: Dict[str, int]
    created_at: datetime


class VideoResult(BaseModel):
    """Result from video analysis."""

    analysis: str
    model: str
    usage: Dict[str, int]
    created_at: datetime


class MultimodalResult(BaseModel):
    """Result from multimodal processing."""

    text: str
    model: str
    usage: Dict[str, int]
    created_at: datetime


class GeminiClient:
    """Async client for Google Gemini API."""

    def __init__(
        self,
        api_key: str,
        settings: Optional[Settings] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            settings: Application settings (optional)
            session: Optional aiohttp session for connection pooling

        Raises:
            AuthenticationError: If API key is invalid

        Example:
            ```python
            client = GeminiClient(api_key="your-api-key")
            ```
        """
        self.api_key = api_key
        self.settings = settings or get_settings()
        self.session = session

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise AuthenticationError(f"Invalid API key: {str(e)}")

        logger.info("Gemini client initialized")

    async def _retry_with_backoff(
        self,
        func: callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        **kwargs,
    ) -> Any:
        """
        Retry function with exponential backoff.

        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            **kwargs: Arguments to pass to function

        Returns:
            Any: Function result

        Raises:
            GeminiAPIError: If all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await func(**kwargs)
            except google_exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise RateLimitError(
                        f"Rate limit exceeded after {max_retries} attempts",
                        retry_after=int(delay),
                    ) from e
                logger.warning(
                    f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})"
                )
            except google_exceptions.GoogleAPIError as e:
                if attempt == max_retries - 1:
                    raise GeminiAPIError(
                        f"API error after {max_retries} attempts: {str(e)}",
                        status_code=503,
                    ) from e
                logger.warning(
                    f"API error, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {e}"
                )
            except Exception as e:
                last_exception = e
                if attempt == max_retries - 1:
                    break
                logger.warning(
                    f"Unexpected error, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {e}"
                )

            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)

        if last_exception:
            raise GeminiAPIError(
                f"Failed after {max_retries} attempts: {str(last_exception)}",
                status_code=500,
            ) from last_exception

        raise GeminiAPIError(
            f"Failed after {max_retries} attempts", status_code=500
        )

    def _get_model(self, model_name: Optional[str] = None) -> GenerativeModel:
        """
        Get GenerativeModel instance.

        Args:
            model_name: Model name (uses default if None)

        Returns:
            GenerativeModel: Model instance

        Raises:
            ModelNotFoundError: If model doesn't exist
        """
        model_name = model_name or self.settings.GEMINI_MODEL_TEXT
        try:
            return GenerativeModel(model_name)
        except Exception as e:
            logger.error(f"Model not found: {model_name}")
            raise ModelNotFoundError(
                f"Model '{model_name}' not found", model_name=model_name
            ) from e

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
        top_k: int = 40,
        stop_sequences: Optional[List[str]] = None,
        model_name: Optional[str] = None,
    ) -> TextResult:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: Stop sequences
            model_name: Model name (uses default if None)

        Returns:
            TextResult: Generated text result

        Raises:
            GeminiAPIError: If generation fails

        Example:
            ```python
            result = await client.generate_text(
                "Write a poem about AI",
                temperature=0.8,
                max_tokens=500
            )
            print(result.text)
            ```
        """
        logger.info(f"Generating text with prompt length: {len(prompt)}")

        async def _generate():
            model = self._get_model(model_name)
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
            )

            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config,
            )

            return response

        try:
            response = await self._retry_with_backoff(_generate)
            text = response.text if hasattr(response, "text") else str(response)

            usage = {
                "prompt_tokens": self._estimate_tokens(prompt),
                "completion_tokens": self._estimate_tokens(text),
                "total_tokens": self._estimate_tokens(prompt) + self._estimate_tokens(text),
            }

            finish_reason = (
                response.candidates[0].finish_reason
                if hasattr(response, "candidates")
                and response.candidates
                else "COMPLETE"
            )

            return TextResult(
                text=text,
                model=model_name or self.settings.GEMINI_MODEL_TEXT,
                usage=usage,
                finish_reason=str(finish_reason),
                created_at=datetime.utcnow(),
            )
        except (RateLimitError, ModelNotFoundError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Text generation failed: {e}", exc_info=True)
            raise GeminiAPIError(f"Text generation failed: {str(e)}", status_code=500) from e

    async def generate_text_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        model_name: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate text stream from prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            model_name: Model name (uses default if None)

        Yields:
            str: Text chunks

        Raises:
            GeminiAPIError: If generation fails

        Example:
            ```python
            async for chunk in client.generate_text_stream("Tell a story"):
                print(chunk, end="", flush=True)
            ```
        """
        logger.info(f"Streaming text generation with prompt length: {len(prompt)}")

        try:
            model = self._get_model(model_name)
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = await model.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            async for chunk in response:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text
                elif hasattr(chunk, "parts"):
                    for part in chunk.parts:
                        if hasattr(part, "text") and part.text:
                            yield part.text

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}", exc_info=True)
            raise GeminiAPIError(
                f"Streaming generation failed: {str(e)}", status_code=500
            ) from e

    async def analyze_image(
        self,
        image: bytes,
        prompt: str = "Describe this image in detail",
        model_name: Optional[str] = None,
    ) -> ImageResult:
        """
        Analyze image with prompt.

        Args:
            image: Image bytes
            prompt: Analysis prompt
            model_name: Model name (uses default if None)

        Returns:
            ImageResult: Analysis result

        Raises:
            GeminiAPIError: If analysis fails

        Example:
            ```python
            with open("image.jpg", "rb") as f:
                image_bytes = f.read()
            result = await client.analyze_image(image_bytes, "What's in this image?")
            print(result.description)
            ```
        """
        logger.info(f"Analyzing image, size: {len(image)} bytes")

        async def _analyze():
            model = self._get_model(model_name or self.settings.GEMINI_MODEL_VISION)
            pil_image = PILImage.open(io.BytesIO(image))

            response = await model.generate_content_async([prompt, pil_image])
            return response

        try:
            response = await self._retry_with_backoff(_analyze)
            description = response.text if hasattr(response, "text") else str(response)

            usage = {
                "prompt_tokens": self._estimate_tokens(prompt),
                "completion_tokens": self._estimate_tokens(description),
                "total_tokens": self._estimate_tokens(prompt)
                + self._estimate_tokens(description),
            }

            return ImageResult(
                description=description,
                model=model_name or self.settings.GEMINI_MODEL_VISION,
                usage=usage,
                created_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Image analysis failed: {e}", exc_info=True)
            raise GeminiAPIError(f"Image analysis failed: {str(e)}", status_code=500) from e

    async def analyze_video(
        self,
        video_path: str,
        prompt: str = "Analyze this video",
        model_name: Optional[str] = None,
    ) -> VideoResult:
        """
        Analyze video with prompt.

        Args:
            video_path: Path to video file
            prompt: Analysis prompt
            model_name: Model name (uses default if None)

        Returns:
            VideoResult: Analysis result

        Raises:
            GeminiAPIError: If analysis fails

        Example:
            ```python
            result = await client.analyze_video("video.mp4", "What happens in this video?")
            print(result.analysis)
            ```
        """
        logger.info(f"Analyzing video: {video_path}")

        try:
            import google.generativeai as genai

            video_file = genai.upload_file(video_path)
            model = self._get_model(model_name or self.settings.GEMINI_MODEL_VISION)

            async def _analyze():
                response = await model.generate_content_async([prompt, video_file])
                return response

            response = await self._retry_with_backoff(_analyze)
            analysis = response.text if hasattr(response, "text") else str(response)

            usage = {
                "prompt_tokens": self._estimate_tokens(prompt),
                "completion_tokens": self._estimate_tokens(analysis),
                "total_tokens": self._estimate_tokens(prompt)
                + self._estimate_tokens(analysis),
            }

            return VideoResult(
                analysis=analysis,
                model=model_name or self.settings.GEMINI_MODEL_VISION,
                usage=usage,
                created_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Video analysis failed: {e}", exc_info=True)
            raise GeminiAPIError(f"Video analysis failed: {str(e)}", status_code=500) from e

    async def transcribe_audio(
        self, audio: bytes, language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            audio: Audio bytes
            language: Language code (optional)

        Returns:
            str: Transcribed text

        Raises:
            GeminiAPIError: If transcription fails

        Example:
            ```python
            with open("audio.wav", "rb") as f:
                audio_bytes = f.read()
            text = await client.transcribe_audio(audio_bytes)
            print(text)
            ```
        """
        logger.info(f"Transcribing audio, size: {len(audio)} bytes")

        try:
            import google.generativeai as genai

            # Note: Gemini may require audio file upload
            # This is a simplified version - adjust based on actual API
            model = self._get_model(self.settings.GEMINI_MODEL_AUDIO)

            # Convert audio to base64 for API
            audio_b64 = base64.b64encode(audio).decode("utf-8")

            prompt = "Transcribe this audio."
            if language:
                prompt += f" Language: {language}"

            response = await model.generate_content_async([prompt, audio_b64])

            return response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}", exc_info=True)
            raise GeminiAPIError(
                f"Audio transcription failed: {str(e)}", status_code=500
            ) from e

    async def process_multimodal(
        self,
        content: List[Any],
        prompt: str,
        model_name: Optional[str] = None,
    ) -> MultimodalResult:
        """
        Process multimodal content.

        Args:
            content: List of content items (text, images, etc.)
            prompt: Processing prompt
            model_name: Model name (uses default if None)

        Returns:
            MultimodalResult: Processing result

        Raises:
            GeminiAPIError: If processing fails

        Example:
            ```python
            content = ["What's in this image?", image_bytes]
            result = await client.process_multimodal(content, "Analyze and describe")
            print(result.text)
            ```
        """
        logger.info(f"Processing multimodal content with {len(content)} items")

        async def _process():
            model = self._get_model(model_name or self.settings.GEMINI_MODEL_VISION)
            processed_content = []

            for item in content:
                if isinstance(item, bytes):
                    try:
                        import io

                        pil_image = PILImage.open(io.BytesIO(item))
                        processed_content.append(pil_image)
                    except Exception:
                        processed_content.append(item)
                else:
                    processed_content.append(item)

            response = await model.generate_content_async([prompt, *processed_content])
            return response

        try:
            response = await self._retry_with_backoff(_process)
            text = response.text if hasattr(response, "text") else str(response)

            usage = {
                "prompt_tokens": self._estimate_tokens(prompt),
                "completion_tokens": self._estimate_tokens(text),
                "total_tokens": self._estimate_tokens(prompt) + self._estimate_tokens(text),
            }

            return MultimodalResult(
                text=text,
                model=model_name or self.settings.GEMINI_MODEL_VISION,
                usage=usage,
                created_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}", exc_info=True)
            raise GeminiAPIError(
                f"Multimodal processing failed: {str(e)}", status_code=500
            ) from e

    async def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text
            model_name: Model name (uses default if None)

        Returns:
            int: Token count

        Example:
            ```python
            count = await client.count_tokens("Hello world")
            print(f"Token count: {count}")
            ```
        """
        try:
            model = self._get_model(model_name)
            result = await model.count_tokens_async(text)
            return result.total_tokens if hasattr(result, "total_tokens") else 0
        except Exception as e:
            logger.warning(f"Token counting failed, using estimation: {e}")
            return self._estimate_tokens(text)

    async def embed_text(self, text: str, model_name: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Input text
            model_name: Model name (uses default if None)

        Returns:
            List[float]: Embedding vector

        Example:
            ```python
            embedding = await client.embed_text("Hello world")
            print(f"Embedding dimension: {len(embedding)}")
            ```
        """
        logger.info(f"Generating embeddings for text length: {len(text)}")

        try:
            # Note: Adjust based on actual Gemini embedding API
            import google.generativeai as genai

            # This is a placeholder - Gemini may have different embedding API
            model = self._get_model(model_name)
            # Embedding generation would go here
            # For now, return empty list
            logger.warning("Embedding API not fully implemented")
            return []
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}", exc_info=True)
            raise GeminiAPIError(
                f"Embedding generation failed: {str(e)}", status_code=500
            ) from e

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).

        Args:
            text: Input text

        Returns:
            int: Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4

