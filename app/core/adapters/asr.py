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

import os
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
        self._indic_models = {}
        self._whisper_model = None

    def is_online(self) -> bool:
        """Network probe to check internet connectivity with 0.8s timeout."""
        for target, port in [("api.sarvam.ai", 443), ("1.1.1.1", 443), ("8.8.8.8", 53)]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.8)
                sock.connect((target, port))
                sock.close()
                return True
            except (socket.timeout, socket.error, OSError):
                continue
        return False

    async def transcribe(self, audio_bytes: bytes, language: str = "hi") -> ASRResult:
        """
        Transcribe audio bytes to text.

        Priority:
          1. Sarvam Saaras V4 (cloud, if online + not STANDALONE)
          2. Groq Whisper-Large-v3-Turbo (cloud secondary)
          3. Local faster-whisper (for English or Indic fallback)
          4. IndicConformer (for native Indic hi/ta/te/mr)
          5. No speech detected

        Args:
            audio_bytes: Raw audio data (WAV, WEBM, M4A)
            language: Language code (en, hi, ta, te, mr)
        """
        if not audio_bytes:
            return ASRResult(text="", language=language, confidence=0.0, provider="empty_input")

        is_english = language.lower().startswith("en")

        # --- Tier 1: Cloud (if online and not forced OFFLINE) ---
        deployment_mode = os.getenv("DEPLOYMENT_MODE", settings.DEPLOYMENT_MODE).upper()
        if self.is_online() and deployment_mode != "OFFLINE":
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

        # --- Tier 2: Local AI4Bharat Speech Models ---
        # For English: use Whisper directly (NEVER use IndicConformer-Hindi for English speech)
        if is_english:
            try:
                res = await self._transcribe_whisper_local(audio_bytes, "en")
                if res.text and res.text.strip():
                    return res
            except Exception as e:
                logger.warning(f"Local Whisper transcription error for English: {repr(e)}")
        else:
            # 1. AI4Bharat IndicConformer (IIT Madras 12,000h Vistaar dataset on CPU ONNX)
            try:
                res = await self._transcribe_indicconformer_local(audio_bytes, language)
                if res.text and len(res.text.strip()) > 1:
                    return res
            except Exception as e:
                logger.warning(f"Local AI4Bharat IndicConformer transcription error: {repr(e)}")

            # 2. AI4Bharat IndicWhisper / faster-whisper (Offline CPU INT8, 0 MB VRAM)
            try:
                res = await self._transcribe_whisper_local(audio_bytes, language)
                if res.text and res.text.strip():
                    return res
            except Exception as e:
                logger.warning(f"Local IndicWhisper transcription error: {repr(e)}")

        # --- Tier 3: IndicConformer on Remote GPU Edge Server (LAN) ---
        if settings.has_remote_speech:
            try:
                res = await self._transcribe_indic_remote(audio_bytes, language)
                if res.text and res.text.strip():
                    return res
            except Exception as e:
                logger.warning(f"IndicConformer Edge Server forwarding failed: {repr(e)}")

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

    def _get_indicconformer_model(self, language: str = "hi"):
        """
        Lazy-load AI4Bharat IndicConformer ONNX model for the requested language.
        Purpose-built by IIT Madras on 12,000h Vistaar dataset.
        Runs purely on CPU via ONNX Runtime (0 MB VRAM), leaving GPU free for Qwen 7B & IndicF5.
        """
        lang_code = language.lower().strip()
        if lang_code.startswith("en"):
            raise ValueError("IndicConformer does not support English. Use Whisper.")

        if lang_code not in self._indic_models:
            import onnx_asr
            repo_map = {
                "hi": "OpenVoiceOS/ai4bharat-indicconformer-hi-onnx",
                "ta": "OpenVoiceOS/ai4bharat-indicconformer-ta-onnx",
                "te": "OpenVoiceOS/ai4bharat-indicconformer-te-onnx",
                "mr": "OpenVoiceOS/ai4bharat-indicconformer-mr-onnx",
                "bn": "OpenVoiceOS/ai4bharat-indicconformer-bn-onnx",
                "gu": "OpenVoiceOS/ai4bharat-indicconformer-gu-onnx",
                "kn": "OpenVoiceOS/ai4bharat-indicconformer-kn-onnx",
                "ml": "OpenVoiceOS/ai4bharat-indicconformer-ml-onnx",
                "pa": "OpenVoiceOS/ai4bharat-indicconformer-pa-onnx",
                "ur": "OpenVoiceOS/ai4bharat-indicconformer-ur-onnx",
            }
            repo_id = repo_map.get(lang_code, "OpenVoiceOS/ai4bharat-indicconformer-hi-onnx")
            logger.info(f"Initializing AI4Bharat IndicConformer for '{lang_code}' from {repo_id}...")
            self._indic_models[lang_code] = onnx_asr.load_model(repo_id)
            logger.info(f"AI4Bharat IndicConformer ({lang_code}) initialized successfully on CPU")

        return self._indic_models[lang_code]

    @staticmethod
    def _ensure_pcm_wav(audio_bytes: bytes) -> bytes:
        """
        Normalize incoming audio (WebM/Opus from browser, MP3, AAC, WAV)
        into standard 16kHz mono 16-bit PCM WAV for AI4Bharat IndicConformer.
        """
        import io
        import av
        import soundfile as sf
        import numpy as np

        try:
            container = av.open(io.BytesIO(audio_bytes))
            resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
            frames = []
            for frame in container.decode(audio=0):
                resampled = resampler.resample(frame)
                for rf in resampled:
                    frames.append(rf.to_ndarray())
            if not frames:
                return audio_bytes
            pcm_data = np.concatenate(frames, axis=1)
            buf = io.BytesIO()
            sf.write(buf, pcm_data.T, 16000, format='WAV', subtype='PCM_16')
            return buf.getvalue()
        except Exception as e:
            logger.warning(f"Audio normalization to 16kHz PCM WAV failed: {e}. Passing raw bytes.")
            return audio_bytes

    async def _transcribe_indicconformer_local(self, audio_bytes: bytes, language: str) -> ASRResult:
        """Offline local ASR via AI4Bharat IndicConformer ONNX on CPU (0 MB VRAM)."""
        model = self._get_indicconformer_model(language)
        if not model:
            return ASRResult(text="", language=language, confidence=0.0, provider="indicconformer_unavailable")

        # Convert browser WebM / Opus to clean 16kHz mono PCM WAV
        wav_bytes = self._ensure_pcm_wav(audio_bytes)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_bytes)
            temp_path = f.name

        try:
            loop = asyncio.get_running_loop()
            transcript = await loop.run_in_executor(None, model.recognize, temp_path)
            transcript = transcript.strip() if transcript else ""

            safe_txt = transcript.encode('ascii', errors='backslashreplace').decode('ascii')[:60]
            logger.info(f"AI4Bharat IndicConformer ASR ({language}): '{safe_txt}'")

            return ASRResult(
                text=transcript,
                language=language,
                confidence=0.95 if transcript else 0.0,
                provider="ai4bharat_indicconformer"
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def _get_whisper_model(self):
        """
        Lazy-load faster-whisper (IndicWhisper) on CPU INT8.
        Uses 0 MB VRAM, runs in ~0.5s on modern multi-core CPU.
        """
        if self._whisper_model is None:
            from faster_whisper import WhisperModel
            logger.info("Initializing faster-whisper (IndicWhisper) on CPU INT8...")
            self._whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
            logger.info("faster-whisper (IndicWhisper) initialized successfully")
        return self._whisper_model

    async def _transcribe_whisper_local(self, audio_bytes: bytes, language: str) -> ASRResult:
        """Offline local ASR via faster-whisper / IndicWhisper on CPU INT8."""
        model = self._get_whisper_model()
        if not model:
            return ASRResult(text="", language=language, confidence=0.0, provider="whisper_unavailable")

        wav_bytes = self._ensure_pcm_wav(audio_bytes)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_bytes)
            temp_path = f.name

        try:
            loop = asyncio.get_running_loop()

            def _infer():
                lang = language if language in ["hi", "ta", "te", "mr", "bn", "gu", "kn", "ml", "pa", "ur", "en"] else None
                segments, info = model.transcribe(
                    temp_path,
                    language=lang,
                    beam_size=5,
                    temperature=0.0,
                    initial_prompt="नमस्ते, मुझे बुखार, दर्द, खांसी या कोई स्वास्थ्य समस्या है।" if lang == "hi" else None
                )
                return " ".join(s.text.strip() for s in segments if s.text).strip()

            transcript = await loop.run_in_executor(None, _infer)
            safe_txt = transcript.encode('ascii', errors='backslashreplace').decode('ascii')[:60]
            logger.info(f"IndicWhisper (faster-whisper) ASR ({language}): '{safe_txt}'")

            return ASRResult(
                text=transcript,
                language=language,
                confidence=0.92 if transcript else 0.0,
                provider="ai4bharat_indicwhisper"
            )
        finally:
            Path(temp_path).unlink(missing_ok=True)


# Singleton
_asr_service: Optional[ASRService] = None


def get_asr_service() -> ASRService:
    global _asr_service
    if _asr_service is None:
        _asr_service = ASRService()
    return _asr_service
