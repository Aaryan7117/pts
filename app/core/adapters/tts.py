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

import os
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
        self._indicf5_model = None

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
          1. Sarvam Bulbul V3 (cloud, if online + not STANDALONE + API key present)
          2. AI4Bharat IndicF5 (offline local near-human diffusion TTS on GPU)
          3. IndicF5 on GPU Edge Server (offline LAN microservice via SPEECH_SERVICE_URL)
          4. Silence WAV (dev fallback)
        """
        if not text or not text.strip():
            silence = self._generate_silence_wav(duration_ms=500)
            return TTSResult(silence, base64.b64encode(silence).decode("utf-8"), 500, provider="empty_input")

        # --- Tier 1 / Tier 2 Priority based on DEPLOYMENT_MODE ---
        deployment_mode = os.getenv("DEPLOYMENT_MODE", settings.DEPLOYMENT_MODE).upper()

        # In STANDALONE / OFFLINE mode: prioritize local IndicF5 first
        if deployment_mode in ("STANDALONE", "OFFLINE"):
            try:
                return await self._synthesize_indicf5_local(text, language)
            except Exception as e:
                logger.warning(f"Local AI4Bharat IndicF5 failed: {e}. Falling back to cloud/remote...")

            if self.is_online() and settings.has_sarvam:
                try:
                    return await self._synthesize_sarvam(text, language)
                except Exception as e:
                    logger.warning(f"Sarvam Bulbul V3 fallback failed: {e}.")
        else:
            # Cloud-first mode
            if self.is_online() and settings.has_sarvam:
                try:
                    return await self._synthesize_sarvam(text, language)
                except Exception as e:
                    logger.warning(f"Sarvam Bulbul V3 failed: {e}. Cascading to local IndicF5.")

            try:
                return await self._synthesize_indicf5_local(text, language)
            except Exception as e:
                logger.warning(f"Local AI4Bharat IndicF5 failed: {e}.")

        # --- Tier 3: IndicF5 on GPU Edge Server (Offline LAN Forwarding) ---
        if settings.has_remote_speech:
            try:
                return await self._synthesize_indicf5_remote(text, language)
            except Exception as e:
                logger.warning(f"IndicF5 Edge Server forwarding failed: {e}.")

        # --- Fallback: Empty audio signals the browser to use native Web Speech API offline ---
        logger.warning(
            "No TTS provider available. Returning empty audio for client-side Web Speech fallback."
        )
        return TTSResult(
            audio_bytes=b"",
            audio_base64="",
            duration_ms=0,
            provider="browser_native_fallback"
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
            "speaker": "aditya",
            "pitch": 0,
            "pace": 1.0,
            "loudness": 1.5,
            "speech_sample_rate": 16000,
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
            duration_ms = int(len(audio_bytes) / 32.0)

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
    # Tier 2b: Local AI4Bharat IndicF5 (Near-Human Diffusion TTS on GPU)
    # ================================================================
    def _get_indicf5_model(self):
        """Lazy load AI4Bharat IndicF5 Near-Human Diffusion TTS model on GPU."""
        if self._indicf5_model is None:
            logger.info("Initializing AI4Bharat IndicF5 Near-Human Diffusion TTS on GPU...")
            import torch
            import f5_tts.infer.utils_infer as utils_infer

            # Monkey-patch load_checkpoint to enforce float32 precision on CUDA
            # This prevents ODE solver and attention layer NaN numerical instability
            orig_load_checkpoint = utils_infer.load_checkpoint

            def patched_load_checkpoint(model, ckpt_path, device, dtype=None, use_ema=True):
                return orig_load_checkpoint(model, ckpt_path, device, dtype=torch.float32, use_ema=use_ema)

            utils_infer.load_checkpoint = patched_load_checkpoint

            from f5_tts.api import F5TTS
            from pathlib import Path
            from huggingface_hub import hf_hub_download
            from safetensors.torch import load_file, save_file

            repo_id = getattr(settings, "INDICF5_MODEL_PATH", "rsolanki1822/IndicF5-mirror")
            if not repo_id or "ai4bharat/IndicF5" in repo_id:
                repo_id = "rsolanki1822/IndicF5-mirror"

            device = "cuda" if torch.cuda.is_available() else "cpu"
            try:
                raw_ckpt_path = hf_hub_download(repo_id, "model.safetensors", local_files_only=True)
            except Exception:
                raw_ckpt_path = hf_hub_download(repo_id, "model.safetensors")

            try:
                vocab_path = hf_hub_download(repo_id, "checkpoints/vocab.txt", local_files_only=True)
            except Exception:
                vocab_path = hf_hub_download(repo_id, "checkpoints/vocab.txt")

            # Clean compiled _orig_mod. state_dict keys if not already done
            cleaned_ckpt_path = str(Path(raw_ckpt_path).parent / "model_cleaned.safetensors")
            if not Path(cleaned_ckpt_path).exists():
                sd = load_file(raw_ckpt_path)
                cleaned = {k.replace('_orig_mod.', ''): v for k, v in sd.items() if not k.startswith('vocoder.')}
                save_file(cleaned, cleaned_ckpt_path)

            self._indicf5_model = F5TTS(
                model="F5TTS_Base",
                ckpt_file=cleaned_ckpt_path,
                vocab_file=vocab_path,
                device=device
            )
            logger.info(f"AI4Bharat IndicF5 initialized successfully on {device}")
        return self._indicf5_model

    async def _synthesize_indicf5_local(self, text: str, language: str = "hi") -> TTSResult:
        """
        Synthesize speech using local AI4Bharat IndicF5 Diffusion TTS on GPU.
        Yields near-human audio across Indian languages.
        Includes disk-based caching for zero-latency prompt playback.
        """
        import tempfile
        import hashlib
        from pathlib import Path
        from importlib.resources import files

        # 1. Check disk cache
        cache_dir = Path("data/tts_cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_key = hashlib.md5(f"{language}_{text.strip()}".encode("utf-8")).hexdigest()
        cache_file = cache_dir / f"{cache_key}.wav"

        if cache_file.exists():
            with open(cache_file, "rb") as f:
                audio_bytes = f.read()
            if len(audio_bytes) > 1000:
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                duration_ms = int(len(audio_bytes) / 48.0)
                logger.info(f"AI4Bharat IndicF5 TTS ({language}): loaded from cache ({len(audio_bytes)} bytes)")
                return TTSResult(
                    audio_bytes=audio_bytes,
                    audio_base64=audio_b64,
                    duration_ms=duration_ms,
                    provider="ai4bharat_indicf5_cached"
                )

        model = self._get_indicf5_model()
        if not model:
            raise RuntimeError("AI4Bharat IndicF5 could not be loaded")

        ref_file = str(files("f5_tts").joinpath("infer/examples/basic/basic_ref_en.wav"))
        ref_text = "Some call me nature, others call me mother nature."

        def _run_synthesis():
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_f:
                out_path = out_f.name

            try:
                wav, sr, _ = model.infer(
                    ref_file=ref_file,
                    ref_text=ref_text,
                    gen_text=text,
                    nfe_step=16,
                    speed=1.0,
                    file_wave=out_path,
                    show_info=lambda *a: None
                )
                with open(out_path, "rb") as f:
                    audio_bytes = f.read()

                # Cache valid audio to disk
                if len(audio_bytes) > 1000:
                    try:
                        with open(cache_file, "wb") as cf:
                            cf.write(audio_bytes)
                    except Exception as ce:
                        logger.warning(f"Could not write TTS cache: {ce}")

                return audio_bytes
            finally:
                Path(out_path).unlink(missing_ok=True)

        loop = asyncio.get_running_loop()
        audio_bytes = await loop.run_in_executor(None, _run_synthesis)

        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        duration_ms = int(len(audio_bytes) / 48.0)

        safe_text = text.encode("ascii", errors="backslashreplace").decode("ascii")[:30]
        logger.info(f"AI4Bharat IndicF5 TTS ({language}): generated {len(audio_bytes)} bytes for '{safe_text}'")
        return TTSResult(
            audio_bytes=audio_bytes,
            audio_base64=audio_b64,
            duration_ms=duration_ms,
            provider="ai4bharat_indicf5"
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
