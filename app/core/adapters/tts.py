"""
MediKiosk — Text-to-Speech (TTS) Adapter
Two-tier: Sarvam Bulbul V3 (cloud) ↔ IndicF5 on GPU Edge Server (offline).
Generates natural explain-back audio for patient verification in 5 Indian languages.

Cloud:   Sarvam AI Bulbul V3 (<250ms, near-human, hi/ta/te/mr/en)
Offline: IndicF5 (AI4Bharat) on On-Premise GPU Edge Server via SPEECH_SERVICE_URL
         (~3.5 GB VRAM, sequential GPU sharing with Qwen 7B LLM)

Ref: speech_stack_research.md — IndicF5 is the ONLY offline TTS
     supporting all 5 target languages. Piper/Kokoro/XTTS/pyttsx3 are ELIMINATED.
"""

import asyncio
import base64
import logging
import socket
from typing import Optional

from app.config import settings

logger = logging.getLogger("medikiosk.tts")


class TTSResult:
    """Result from text-to-speech synthesis."""
    def __init__(self, audio_bytes: bytes, audio_base64: str, duration_ms: int, provider: str = "mock"):
        self.audio_bytes = audio_bytes
        self.audio_base64 = audio_base64
        self.duration_ms = duration_ms
        self.provider = provider


class TTSService:
    """
    Two-tier TTS with automatic failover.

    Tier 1 (Cloud):   Sarvam AI Bulbul V3
                      Near-human Indian accent, <250ms, all 5 languages.
                      Free ₹100 credit on signup.

    Tier 2 (Offline): IndicF5 (AI4Bharat) on On-Premise GPU Edge Server
                      State-of-the-art diffusion TTS, ~3.5 GB VRAM (sequential with LLM).
                      Accessed via SPEECH_SERVICE_URL over local clinic LAN.
                      Supports hi, ta, te, mr, en natively.

    Dev Fallback:     Deterministic silence WAV (so API never crashes during dev
                      when neither cloud nor GPU server is available).
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

    async def synthesize(self, text: str, language: str = "hi") -> TTSResult:
        """
        Synthesize speech from text.

        Priority:
          1. Sarvam Bulbul V3 (cloud, if online + API key present)
          2. IndicF5 on GPU Edge Server (offline, via SPEECH_SERVICE_URL)
          3. Silence WAV (dev fallback — never crashes the API)
        """
        if not text or not text.strip():
            silence = self._generate_silence_wav(duration_ms=500)
            return TTSResult(silence, base64.b64encode(silence).decode("utf-8"), 500, provider="empty_input")

        # --- Tier 1: Sarvam AI Bulbul V3 (Cloud) ---
        if self.is_online() and settings.has_sarvam:
            try:
                return await self._synthesize_sarvam(text, language)
            except Exception as e:
                logger.warning(f"Sarvam Bulbul V3 failed: {e}. Cascading to IndicF5 Edge Server.")

        # --- Tier 2: IndicF5 on GPU Edge Server (Offline LAN) ---
        if settings.has_remote_speech:
            try:
                return await self._synthesize_indicf5_remote(text, language)
            except Exception as e:
                logger.warning(f"IndicF5 Edge Server forwarding failed: {e}. Falling back to silence.")

        # --- Dev Fallback: Silence WAV ---
        logger.warning(
            "No TTS provider available (no Sarvam API key + no SPEECH_SERVICE_URL for IndicF5). "
            "Returning silence WAV. Set SARVAM_API_KEY or SPEECH_SERVICE_URL in .env."
        )
        silence = self._generate_silence_wav(duration_ms=1000)
        return TTSResult(
            audio_bytes=silence,
            audio_base64=base64.b64encode(silence).decode("utf-8"),
            duration_ms=1000,
            provider="silence_dev_fallback"
        )

    # ================================================================
    # Tier 1: Sarvam AI Bulbul V3 (Cloud)
    # ================================================================
    async def _synthesize_sarvam(self, text: str, language: str) -> TTSResult:
        """Cloud TTS via Sarvam AI Bulbul V3. Near-human Indian voice."""
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
            "api-subscription-key": settings.SARVAM_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text],
            "target_language_code": sarvam_lang,
            "speaker": "meera",
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v3"
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://api.sarvam.ai/text-to-speech",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            res_json = response.json()
            audios = res_json.get("audios", [])
            if not audios:
                raise ValueError("No audio returned from Sarvam Bulbul V3")

            audio_b64 = audios[0]
            audio_bytes = base64.b64decode(audio_b64)
            duration_ms = int(len(audio_bytes) / 16.0)

            logger.info(f"Sarvam Bulbul V3 TTS ({language}): {len(audio_bytes)} bytes")
            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=audio_b64,
                duration_ms=duration_ms,
                provider="sarvam_bulbul_v3"
            )

    # ================================================================
    # Tier 2: IndicF5 on GPU Edge Server (Offline LAN Forwarding)
    # ================================================================
    async def _synthesize_indicf5_remote(self, text: str, language: str) -> TTSResult:
        """
        Forward TTS request to IndicF5 running on the On-Premise GPU Edge Server.

        The Edge Server runs IndicF5 (AI4Bharat) on the RTX GPU, accessed over
        the local clinic LAN / Wi-Fi subnet via SPEECH_SERVICE_URL.
        IndicF5 natively supports hi, ta, te, mr, en with near-human quality.
        """
        import httpx

        url = f"{settings.SPEECH_SERVICE_URL.rstrip('/')}/api/speech/synthesize"
        payload = {"text": text, "language": language}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            audio_b64 = data.get("audio_base64", "")
            audio_bytes = base64.b64decode(audio_b64)
            duration_ms = data.get("duration_ms", int(len(audio_bytes) / 32.0))

            logger.info(f"IndicF5 Edge Server TTS ({language}): {len(audio_bytes)} bytes")
            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=audio_b64,
                duration_ms=duration_ms,
                provider="indicf5_edge_server"
            )

    # ================================================================
    # Dev Fallback: Silence WAV Generator
    # ================================================================
    @staticmethod
    def _generate_silence_wav(duration_ms: int = 1000) -> bytes:
        """Generate a minimal valid silent WAV file for dev/mock responses."""
        import struct

        sample_rate = 16000
        num_samples = int(sample_rate * duration_ms / 1000)
        data_size = num_samples * 2  # 16-bit = 2 bytes per sample

        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + data_size,
            b'WAVE',
            b'fmt ',
            16,           # chunk size
            1,            # PCM format
            1,            # mono
            sample_rate,
            sample_rate * 2,
            2,            # block align
            16,           # bits per sample
            b'data',
            data_size
        )

        silence = b'\x00' * data_size
        return header + silence


# Singleton
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
