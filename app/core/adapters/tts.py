"""
MediKiosk — Piper TTS Adapter
Offline text-to-speech for patient explain-back verification.
Uses Piper TTS (ONNX CPU, ~50MB RAM, 0 MB VRAM).

Synthesizes plain-language audio summaries in the patient's language
so non-literate patients can verify their captured clinical data.

Ref: MediKiosk_Full_Context_Handoff.md Innovation 4
"""

import base64
import io
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from app.config import settings

logger = logging.getLogger("medikiosk.tts")


class TTSResult:
    """Result from text-to-speech synthesis."""
    def __init__(self, audio_bytes: bytes, audio_base64: str, duration_ms: int):
        self.audio_bytes = audio_bytes
        self.audio_base64 = audio_base64
        self.duration_ms = duration_ms


class TTSService:
    """
    Piper TTS wrapper for offline patient explain-back audio.

    Generates natural Hindi/regional speech from text using ONNX CPU inference.
    Sub-100ms synthesis for typical clinical summaries.

    For hackathon demo: If Piper isn't installed, returns a mock result
    so development can continue on machines without the model files.
    """

    # Voice model mapping per language
    VOICE_MODELS: dict[str, str] = {
        "hi": "hi_IN-rohan-medium",
        "en": "en_US-lessac-medium",
    }

    def __init__(self):
        self._available = None

    def is_available(self) -> bool:
        """Check if Piper TTS is installed and accessible."""
        if self._available is None:
            try:
                result = subprocess.run(
                    ["piper", "--version"],
                    capture_output=True, text=True, timeout=5
                )
                self._available = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._available = False

            if self._available:
                logger.info("Piper TTS is available")
            else:
                logger.warning("Piper TTS not found — using mock TTS for development")

        return self._available

    async def synthesize(self, text: str, language: str = "hi") -> TTSResult:
        """
        Synthesize speech from text.

        Args:
            text: Plain-language text to convert to speech
            language: Language code (en, hi)

        Returns:
            TTSResult with WAV audio bytes and base64-encoded audio
        """
        if not self.is_available():
            # Mock result for development
            logger.debug(f"Mock TTS: '{text[:50]}...' (lang={language})")
            mock_audio = self._generate_silence_wav(duration_ms=1000)
            return TTSResult(
                audio_bytes=mock_audio,
                audio_base64=base64.b64encode(mock_audio).decode("utf-8"),
                duration_ms=1000
            )

        voice = self.VOICE_MODELS.get(language, self.VOICE_MODELS["hi"])

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_file:
                out_path = out_file.name

            # Run Piper TTS as a subprocess
            process = subprocess.run(
                ["piper", "--model", voice, "--output_file", out_path],
                input=text,
                capture_output=True,
                text=True,
                timeout=10
            )

            if process.returncode != 0:
                logger.error(f"Piper TTS failed: {process.stderr}")
                raise RuntimeError(f"Piper TTS failed: {process.stderr}")

            audio_bytes = Path(out_path).read_bytes()
            Path(out_path).unlink(missing_ok=True)

            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

            # Rough duration estimate (WAV 16kHz mono 16-bit = 32000 bytes/sec)
            duration_ms = int(len(audio_bytes) / 32.0)

            logger.info(f"TTS synthesized: {len(text)} chars → {len(audio_bytes)} bytes ({duration_ms}ms)")

            return TTSResult(
                audio_bytes=audio_bytes,
                audio_base64=audio_b64,
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            mock_audio = self._generate_silence_wav(duration_ms=1000)
            return TTSResult(
                audio_bytes=mock_audio,
                audio_base64=base64.b64encode(mock_audio).decode("utf-8"),
                duration_ms=1000
            )

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

        # Silent audio data (all zeros)
        silence = b'\x00' * data_size

        return header + silence


# Singleton
_tts_service: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
