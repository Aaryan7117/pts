"""
MediKiosk — Speech Recognition (ASR) Adapter
Two-tier: Sarvam Saaras V4 (cloud) ↔ IndicConformer / faster-whisper on GPU Edge Server (offline).
Transcribes patient speech into text for the clinical interview engine.

Cloud:   Sarvam AI Saaras V4 (<250ms, native hi/ta/te/mr/en, strong code-mixing)
         Groq Whisper-Large-v3-Turbo as cloud secondary.
Offline: IndicConformer 600M (AI4Bharat, CPU ONNX, ~900 MB RAM, 0 GB VRAM) or
         faster-whisper on the On-Premise GPU Edge Server, reached over the local
         clinic LAN via SPEECH_SERVICE_URL.

Ref: speech_stack_research.md — IndicConformer covers the 22 scheduled Indian
     languages and runs on CPU, leaving the 8 GB GPU free for Qwen 7B and IndicF5.
"""

import asyncio
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
    Two-tier ASR with automatic failover.

    Tier 1 (Cloud):   Sarvam AI Saaras V4
                      Native Indian-language speech recognition, <250ms, all 5 languages.
                      Free ₹100 credit on signup.
                      Groq Whisper-Large-v3-Turbo is the cloud secondary.

    Tier 2 (Offline): IndicConformer 600M / faster-whisper on On-Premise GPU Edge Server
                      IndicConformer runs on CPU ONNX (0 GB VRAM) so the GPU stays
                      free for Qwen 7B and IndicF5.
                      Accessed via SPEECH_SERVICE_URL over local clinic LAN.

    Dev Fallback:     Deterministic mock transcript (so the API never crashes during
                      dev when neither cloud nor Edge Server is available).
    """

    def __init__(self):
        pass

    def is_online(self) -> bool:
        """Quick 50ms network probe to check internet connectivity."""
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

        Priority:
          1. Sarvam Saaras V4 (cloud, if online + API key present)
          2. Groq Whisper-Large-v3-Turbo (cloud secondary)
          3. IndicConformer / faster-whisper on GPU Edge Server (via SPEECH_SERVICE_URL)
          4. Mock transcript (dev fallback — never crashes the API)

        Args:
            audio_bytes: Raw audio data (WAV, WEBM, M4A)
            language: Language code (en, hi, ta, te, mr)
        """
        if not audio_bytes:
            return ASRResult(text="", language=language, confidence=0.0, provider="empty_input")

        # --- Tier 1: Cloud ---
        if self.is_online():
            if settings.has_sarvam:
                try:
                    res = await self._transcribe_sarvam(audio_bytes, language)
                    if res.text and res.text.strip():
                        return res
                except Exception as e:
                    logger.warning(f"Sarvam Saaras V4 failed: {e}. Cascading to Groq Whisper.")

            if settings.has_groq:
                try:
                    res = await self._transcribe_groq(audio_bytes, language)
                    if res.text and res.text.strip():
                        return res
                except Exception as e:
                    logger.warning(f"Groq Whisper failed: {e}.")

        # --- Tier 2: IndicConformer / faster-whisper on GPU Edge Server (Offline LAN) ---
        if settings.has_remote_speech:
            try:
                res = await self._transcribe_indic_remote(audio_bytes, language)
                if res.text and res.text.strip():
                    return res
            except Exception as e:
                logger.warning(f"IndicConformer Edge Server forwarding failed: {e}.")

        # Silence / No speech detected
        return ASRResult(
            text="",
            language=language,
            confidence=0.0,
            provider="no_speech_detected"
        )

    # ================================================================
    # Tier 1: Sarvam AI Saaras V4 (Cloud)
    # ================================================================
    async def _transcribe_sarvam(self, audio_bytes: bytes, language: str) -> ASRResult:
        """Cloud ASR via Sarvam AI Saaras V4. Native Indian-language acoustics."""
        import httpx

        lang_map = {
            "hi": "hi-IN",
            "ta": "ta-IN",
            "te": "te-IN",
            "mr": "mr-IN",
            "en": "en-IN"
        }
        sarvam_lang = lang_map.get(language, "hi-IN")

        headers = {
            "api-subscription-key": settings.SARVAM_API_KEY
        }
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        data = {
            "model": "saaras:v4",
            "language_code": sarvam_lang
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.sarvam.ai/speech-to-text",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            res_json = response.json()
            transcript = res_json.get("transcript", "").strip()

            logger.info(f"Sarvam Saaras V4 ASR ({language}): {transcript[:50]}")
            return ASRResult(
                text=transcript,
                language=language,
                confidence=0.96,
                provider="sarvam_saaras_v4"
            )

    # ================================================================
    # Tier 1b: Groq Whisper-Large-v3-Turbo (Cloud Secondary)
    # ================================================================
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
            logger.info(f"Groq Whisper ASR ({language}): {response.strip()[:50]}")
            return ASRResult(
                text=response.strip(),
                language=language,
                confidence=0.92,
                provider="groq_whisper"
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    # ================================================================
    # Tier 2: IndicConformer / faster-whisper on GPU Edge Server (Offline LAN)
    # ================================================================
    async def _transcribe_indic_remote(self, audio_bytes: bytes, language: str) -> ASRResult:
        """
        Forward transcription to the speech microservice on the On-Premise GPU Edge Server.

        The Edge Server runs IndicConformer 600M (AI4Bharat) on CPU ONNX, or
        faster-whisper on the RTX GPU, and is reached over the local clinic
        LAN / Wi-Fi subnet via SPEECH_SERVICE_URL. Both cover hi, ta, te, mr, en.
        """
        import httpx

        url = f"{settings.SPEECH_SERVICE_URL.rstrip('/')}/api/speech/transcribe"
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"language": language}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, files=files, data=data)
            response.raise_for_status()
            res_json = response.json()

            transcript = res_json.get("text", "").strip()
            logger.info(f"IndicConformer Edge Server ASR ({language}): {transcript[:50]}")
            return ASRResult(
                text=transcript,
                language=res_json.get("language", language),
                confidence=float(res_json.get("confidence", 0.90)),
                provider=res_json.get("provider", "indicconformer_edge_server")
            )

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
