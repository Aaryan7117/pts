"""
MediKiosk — Speech Recognition (ASR) Adapter
Two-tier: AI4Bharat IndicWhisper (offline CPU floor) ↔ Groq Whisper / Sarvam (cloud).
Uses 50ms network probe for instant route selection.

Ref: MediKiosk_Tech_Stack_Finalized.md Section 3A
"""

import asyncio
import base64
import io
import logging
import socket
import tempfile
from pathlib import Path
from typing import Optional
from app.config import settings

logger = logging.getLogger("medikiosk.asr")


class ASRResult:
    """Result from speech-to-text transcription."""
    def __init__(self, text: str, language: str, confidence: float, provider: str):
        self.text = text
        self.language = language
        self.confidence = confidence
        self.provider = provider

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "language": self.language,
            "confidence": self.confidence,
            "provider": self.provider
        }


class ASRService:
    """
    Two-tier speech recognition with automatic failover.

    Online:  Groq Whisper-Large-v3-Turbo (<250ms) or Sarvam AI
    Offline: AI4Bharat IndicWhisper (ONNX CPU, ~1.4s)

    For hackathon: If IndicWhisper model isn't downloaded yet,
    falls back to Groq Whisper cloud or returns a mock result.
    """

    def __init__(self):
        self._indicwhisper_loaded = False
        self._indicwhisper_model = None

    def is_online(self) -> bool:
        """Quick 50ms network probe."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.05)
            sock.connect(("1.1.1.1", 53))
            sock.close()
            return True
        except (socket.timeout, socket.error, OSError):
            return False

    async def transcribe(self, audio_bytes: bytes, language: str = "hi") -> ASRResult:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio data (WAV, WEBM, M4A)
            language: Language code (en, hi, ta, te, mr)

        Returns:
            ASRResult with transcribed text and metadata.
        """
        # Try cloud first if online
        if self.is_online():
            try:
                if settings.has_groq:
                    return await self._transcribe_groq(audio_bytes, language)
            except Exception as e:
                logger.warning(f"Cloud ASR failed: {e}. Falling back to offline.")

        # Offline floor: IndicWhisper
        try:
            return await self._transcribe_indicwhisper(audio_bytes, language)
        except Exception as e:
            logger.warning(f"IndicWhisper failed: {e}. Using mock transcription for development.")
            return ASRResult(
                text="[ASR: Audio received but model not loaded — install IndicWhisper on the GPU laptop]",
                language=language,
                confidence=0.0,
                provider="mock"
            )

    async def _transcribe_groq(self, audio_bytes: bytes, language: str) -> ASRResult:
        """Cloud ASR via Groq Whisper-Large-v3-Turbo."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )

        # Write audio to a temp file for the API
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        try:
            with open(temp_path, "rb") as audio_file:
                response = await asyncio.wait_for(
                    client.audio.transcriptions.create(
                        model="whisper-large-v3-turbo",
                        file=audio_file,
                        language=self._lang_to_whisper(language),
                        response_format="text"
                    ),
                    timeout=5.0
                )
            return ASRResult(
                text=response.strip(),
                language=language,
                confidence=0.92,
                provider="groq_whisper"
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def _transcribe_indicwhisper(self, audio_bytes: bytes, language: str) -> ASRResult:
        """
        Offline ASR via AI4Bharat IndicWhisper (ONNX CPU).
        Runs in ~1.4s on 8-core CPU, 0 MB VRAM.

        NOTE: Requires model files to be downloaded on the GPU laptop.
        """
        # Lazy load — only import/load when first needed
        if not self._indicwhisper_loaded:
            model_path = Path(settings.INDICWHISPER_MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(
                    f"IndicWhisper model not found at {model_path}. "
                    f"Download it on the GPU laptop first."
                )

            # TODO: Load the actual IndicWhisper ONNX model
            # This will be implemented when running on the friend's laptop
            raise NotImplementedError("IndicWhisper ONNX loading — implement on GPU laptop")

        # Placeholder for actual inference
        raise NotImplementedError("IndicWhisper inference not yet implemented")

    @staticmethod
    def _lang_to_whisper(lang: str) -> str:
        """Map MediKiosk language codes to Whisper language codes."""
        mapping = {
            "en": "en",
            "hi": "hi",
            "ta": "ta",
            "te": "te",
            "mr": "mr"
        }
        return mapping.get(lang, "hi")


# Singleton
_asr_service: Optional[ASRService] = None


def get_asr_service() -> ASRService:
    global _asr_service
    if _asr_service is None:
        _asr_service = ASRService()
    return _asr_service
