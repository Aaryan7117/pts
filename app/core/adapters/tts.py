"""
MediKiosk — Text-to-Speech (TTS) Adapter
Multi-tier: Sarvam Bulbul V3 (cloud quality) ↔ Remote Microservice Forwarding ↔ Local pyttsx3 / Piper (offline) ↔ Mock.
Generates plain-language explain-back audio for patient verification.

Ref: MediKiosk_Tech_Stack_Finalized.md Section 3A
"""

import asyncio
import base64
import logging
import os
import socket
import subprocess
import tempfile
from pathlib import Path
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
    Multi-tier TTS service with automatic failover and microservice forwarding.

    1. Cloud Primary: Sarvam AI Bulbul V3 (<250ms, near-human Indian accent across 5 languages)
    2. Remote Microservice: Forward to dedicated GPU Edge Server if SPEECH_SERVICE_URL configured
    3. Offline Local: pyttsx3 (SAPI5 on Windows / OS native, 0 VRAM, 0 lag) or Piper CLI if on PATH
    4. Fallback: Deterministic silence WAV generator
    """

    VOICE_MODELS: dict[str, str] = {
        "hi": "hi_IN-rohan-medium",
        "en": "en_US-lessac-medium",
    }

    def __init__(self):
        self._piper_available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if standalone Piper CLI executable is installed on PATH."""
        if self._piper_available is None:
            try:
                result = subprocess.run(
                    ["piper", "--version"],
                    capture_output=True, text=True, timeout=5
                )
                self._piper_available = (result.returncode == 0)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._piper_available = False

            if self._piper_available:
                logger.info("Piper CLI is available on system PATH")
            else:
                logger.info("Piper CLI not on PATH — pyttsx3 / Sarvam will be primary TTS")

        return self._piper_available

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
        Synthesize speech from text across available providers with graceful degradation.
        """
        if not text or not text.strip():
            silence = self._generate_silence_wav(duration_ms=500)
            return TTSResult(silence, base64.b64encode(silence).decode("utf-8"), 500, provider="empty_input")

        # 1. Cloud Primary: Sarvam AI Bulbul V3
        if self.is_online() and settings.has_sarvam:
            try:
                return await self._synthesize_sarvam(text, language)
            except Exception as e:
                logger.warning(f"Sarvam Bulbul TTS failed: {e}. Cascading to next tier.")

        # 2. Remote Microservice Forwarding (GPU Edge Server)
        if settings.has_remote_speech:
            try:
                return await self._synthesize_remote(text, language)
            except Exception as e:
                logger.warning(f"Remote speech service forwarding failed: {e}. Falling back to local offline.")

        # 3. Offline Tier A: Standalone Piper CLI (if installed)
        if self.is_available():
            try:
                return await self._synthesize_piper(text, language)
            except Exception as e:
                logger.warning(f"Piper TTS synthesis failed: {e}. Trying pyttsx3.")

        # 3. Offline Tier B: pyttsx3 (Native OS TTS, 0 VRAM, instant)
        try:
            return await self._synthesize_pyttsx3(text, language)
        except Exception as e:
            logger.warning(f"pyttsx3 synthesis failed: {e}. Falling back to silence WAV.")

        # 4. Ultimate Fallback: Valid silence WAV
        silence = self._generate_silence_wav(duration_ms=1000)
        return TTSResult(
            audio_bytes=silence,
            audio_base64=base64.b64encode(silence).decode("utf-8"),
            duration_ms=1000,
            provider="silence_fallback"
        )

    async def _synthesize_sarvam(self, text: str, language: str) -> TTSResult:
        """Cloud TTS via Sarvam AI Bulbul V3."""
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
                raise ValueError("No audio returned from Sarvam Bulbul")

            audio_b64 = audios[0]
            audio_bytes = base64.b64decode(audio_b64)
            duration_ms = int(len(audio_bytes) / 16.0)

            logger.info(f"Sarvam Bulbul TTS generated ({language}): {len(audio_bytes)} bytes")
            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=audio_b64,
                duration_ms=duration_ms,
                provider="sarvam_bulbul_v3"
            )

    async def _synthesize_remote(self, text: str, language: str) -> TTSResult:
        """Forward TTS synthesis to remote GPU Edge Microservice."""
        import httpx

        url = f"{settings.SPEECH_SERVICE_URL.rstrip('/')}/api/speech/synthesize"
        payload = {"text": text, "language": language}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            audio_b64 = data.get("audio_base64", "")
            audio_bytes = base64.b64decode(audio_b64)
            duration_ms = data.get("duration_ms", int(len(audio_bytes) / 32.0))

            logger.info(f"Remote Edge Microservice TTS generated: {len(audio_bytes)} bytes")
            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=audio_b64,
                duration_ms=duration_ms,
                provider="remote_edge_microservice"
            )

    async def _synthesize_piper(self, text: str, language: str) -> TTSResult:
        """Synthesize speech using standalone Piper CLI subprocess."""
        voice = self.VOICE_MODELS.get(language, self.VOICE_MODELS["hi"])

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
            out_path = out_file.name

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    ["piper", "--model", voice, "--output_file", out_path],
                    input=text,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True
                )
            )

            audio_bytes = Path(out_path).read_bytes()
            duration_ms = int(len(audio_bytes) / 32.0)

            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
                duration_ms=duration_ms,
                provider="piper_cli"
            )
        finally:
            Path(out_path).unlink(missing_ok=True)

    async def _synthesize_pyttsx3(self, text: str, language: str) -> TTSResult:
        """Offline Native TTS via pyttsx3 (SAPI5 on Windows / OS native)."""
        import pyttsx3

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
            out_path = out_file.name

        def _run_pyttsx3():
            engine = pyttsx3.init()
            engine.setProperty("rate", 145)  # Slightly slower for clear clinical comprehension
            engine.save_to_file(text, out_path)
            engine.runAndWait()

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, _run_pyttsx3)

            audio_bytes = Path(out_path).read_bytes()
            if not audio_bytes:
                raise ValueError("pyttsx3 generated empty audio file")

            duration_ms = int(len(audio_bytes) / 32.0)
            logger.info(f"pyttsx3 synthesized: {len(text)} chars → {len(audio_bytes)} bytes")

            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=base64.b64encode(audio_bytes).decode("utf-8"),
                duration_ms=duration_ms,
                provider="pyttsx3_native"
            )
        finally:
            Path(out_path).unlink(missing_ok=True)

    @staticmethod
    def _generate_silence_wav(duration_ms: int = 1000) -> bytes:
        """Generate a minimal silent WAV file for mock responses."""
        import struct

        sample_rate = 16000
        num_samples = int(sample_rate * duration_ms / 1000)
        data_size = num_samples * 2  # 16-bit = 2 bytes per sample

        # WAV header
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
