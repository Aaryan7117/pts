"""
MediKiosk — Resilient Multi-Provider LLM Service
Hybrid failover: Gemini Flash (quality) → Groq Llama 3.1 70B (speed) → Ollama Qwen 7B (offline).
150ms socket connectivity probe — zero offline TCP stalls.

Ref: MediKiosk_Tech_Stack_Finalized.md Section 6
"""

import os
import json
import asyncio
import socket
import logging
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar
from pydantic import BaseModel, Field
from app.config import settings

logger = logging.getLogger("medikiosk.llm")
T = TypeVar("T", bound=BaseModel)


# ============================================================
# Schema for LLM-extracted medications from OCR text
# ============================================================
class ExtractedMedication(BaseModel):
    name: str = Field(description="Medication name")
    dose: Optional[str] = Field(default=None, description="Dosage (e.g. 500mg)")
    frequency: Optional[str] = Field(default=None, description="e.g. 1-0-1 or twice daily")
    source_lines: list[int] = Field(default_factory=list, description="Line citations from OCR output (offline)")
    box_2d: Optional[list[int]] = Field(
        default=None,
        description="[ymin, xmin, ymax, xmax] 0-1000 normalized coordinates for doctor UI visual grounding (cloud)"
    )
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


class ExtractedMedicationList(BaseModel):
    medications: list[ExtractedMedication] = Field(default_factory=list)


# ============================================================
# Abstract LLM Provider
# ============================================================
class LLMProvider(ABC):
    timeout_seconds: float = 3.5
    provider_name: str = "unknown"

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        """Generate a structured response matching the given Pydantic schema."""
        pass

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        """Generate a free-form text response (for interview follow-up questions)."""
        pass


# ============================================================
# Gemini Flash Provider (Cloud Quality Tier)
# ============================================================
class GeminiFlashProvider(LLMProvider):
    """Cloud Quality Tier: Gemini Flash using official modern google-genai SDK."""

    def __init__(self, api_key: str):
        self.timeout_seconds = 15.0
        self.provider_name = "GeminiFlash"
        self._api_key = api_key
        self._client = None
        self._model = getattr(settings, "GEMINI_MODEL", "gemini-flash-latest")

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        from google.genai import types

        client = self._get_client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.1
        )
        models_to_try = [self._model]
        for alt in ["gemini-3.5-flash-lite", "gemini-flash-latest"]:
            if alt not in models_to_try:
                models_to_try.append(alt)

        last_err = None
        for m in models_to_try:
            try:
                response = await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=config
                    ),
                    timeout=self.timeout_seconds
                )
                return schema.model_validate_json(response.text)
            except Exception as e:
                last_err = e
                if "NOT_FOUND" in str(e) or "404" in str(e):
                    logger.warning(f"Gemini model {m} not found, trying fallback...")
                    continue
                raise e
        raise last_err

    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        from google.genai import types

        client = self._get_client()
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3
        )
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config
            ),
            timeout=self.timeout_seconds
        )
        return response.text

    async def generate_prescription_vision(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> ExtractedMedicationList:
        """Multimodal Vision OCR: Directly extract medications with 2D bounding boxes from image."""
        from google.genai import types

        client = self._get_client()
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        system_prompt = (
            "You are an expert clinical pharmacologist and prescription vision specialist. "
            "Examine this handwritten or printed doctor prescription. Extract all medications, "
            "their dosages, frequency of intake (e.g. 1-0-1, OD, BD, TDS), and detect the 2D bounding box "
            "for each medication in normalized coordinates [ymin, xmin, ymax, xmax] on a 0-1000 scale. "
            "Return JSON matching the schema."
        )
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=ExtractedMedicationList,
            temperature=0.1
        )
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=self._model,
                contents=[
                    image_part,
                    "Extract all medications and their 2D bounding boxes [ymin, xmin, ymax, xmax] from this prescription."
                ],
                config=config
            ),
            timeout=15.0
        )
        return ExtractedMedicationList.model_validate_json(response.text)


# ============================================================
# Groq Llama Provider (Cloud Speed Tier)
# ============================================================
class GroqLlamaProvider(LLMProvider):
    """Cloud Speed Tier: Fast LLM on Groq LPUs (~280 tok/s)."""

    def __init__(self, api_key: str):
        self.timeout_seconds = 10.0
        self.provider_name = "GroqLlama"
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self._api_key
            )
        return self._client

    async def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        client = self._get_client()
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": f"{system_prompt}\nStrictly output valid JSON matching this schema:\n{json.dumps(schema.model_json_schema(), indent=2)}"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            ),
            timeout=self.timeout_seconds
        )
        return schema.model_validate_json(response.choices[0].message.content)

    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        client = self._get_client()
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            ),
            timeout=self.timeout_seconds
        )
        return response.choices[0].message.content


# ============================================================
# Ollama Edge Provider (Offline Core)
# ============================================================
class OllamaEdgeProvider(LLMProvider):
    """Offline Edge Core: Qwen 2.5 7B Q4 on Single 8GB RTX GPU."""

    def __init__(self, base_url: str = None, model: str = None):
        self.timeout_seconds = 120.0  # Local inference / model cold loading on 8GB GPU
        self.provider_name = "OllamaEdge"
        self._base_url = base_url or settings.OLLAMA_BASE_URL
        self._model = model or settings.OLLAMA_MODEL
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=self._base_url,
                api_key="ollama"  # Ollama doesn't need a real key
            )
        return self._client

    async def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        client = self._get_client()
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{system_prompt}\n"
                            f"Return JSON strictly matching this schema:\n"
                            f"{json.dumps(schema.model_json_schema(), indent=2)}"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            ),
            timeout=self.timeout_seconds
        )
        return schema.model_validate_json(response.choices[0].message.content)

    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        client = self._get_client()
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            ),
            timeout=self.timeout_seconds
        )
        return response.choices[0].message.content


# ============================================================
# Resilient LLM Service (Failover Chain)
# ============================================================
class ResilientLLMService:
    """
    Intelligent failover with 150ms socket connectivity probe.
    Zero offline TCP stalls during the live Wi-Fi unplug demo.

    Chain: Online? → [Gemini Flash → Groq Llama] → [Ollama Qwen 7B → Ollama Qwen 3B]
    """

    def __init__(self):
        self.cloud_providers: list[LLMProvider] = []
        self.edge_providers: list[LLMProvider] = []

        # Build cloud providers (only if API keys are available)
        if settings.has_gemini:
            self.cloud_providers.append(GeminiFlashProvider(settings.GEMINI_API_KEY))
            logger.info("Gemini Flash provider registered (cloud quality tier)")

        if settings.has_groq:
            self.cloud_providers.append(GroqLlamaProvider(settings.GROQ_API_KEY))
            logger.info("Groq Llama 3.1 70B provider registered (cloud speed tier)")

        # Build edge providers (always available)
        self.edge_providers.append(
            OllamaEdgeProvider(model=settings.OLLAMA_MODEL)
        )
        logger.info(f"Ollama Edge provider registered (primary: {settings.OLLAMA_MODEL})")

        # Fallback 3B model
        if settings.OLLAMA_FALLBACK_MODEL:
            self.edge_providers.append(
                OllamaEdgeProvider(model=settings.OLLAMA_FALLBACK_MODEL)
            )
            logger.info(f"Ollama Fallback provider registered ({settings.OLLAMA_FALLBACK_MODEL})")

    def is_online(self) -> bool:
        """150ms socket probe — instantly detects offline state."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.15)
            sock.connect(("1.1.1.1", 53))
            sock.close()
            return True
        except (socket.timeout, socket.error, OSError):
            return False

    async def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        """Execute structured generation with automatic failover."""
        return await self._execute(
            lambda provider: provider.generate_structured(prompt, schema, system_prompt)
        )

    async def generate_text(self, prompt: str, system_prompt: str) -> str:
        """Execute text generation with automatic failover."""
        return await self._execute(
            lambda provider: provider.generate_text(prompt, system_prompt)
        )

    async def generate_intake_turn(self, prompt: str, schema: Type[T], system_prompt: str) -> T:
        """
        Execute context-aware OPD intake question generation.
        Strict Routing:
          ONLINE  → Gemini Flash
          OFFLINE → Qwen 2.5 7B → Qwen 2.5 3B
        Strictly excludes Groq/Llama or any other external models.
        """
        candidates: list[LLMProvider] = []

        # 1. ONLINE tier: Gemini Flash (if configured and online)
        if settings.has_gemini and self.is_online():
            for provider in self.cloud_providers:
                if isinstance(provider, GeminiFlashProvider):
                    candidates.append(provider)
                    break

        # 2. OFFLINE / Fallback tier: Qwen 2.5 7B -> Qwen 2.5 3B
        for provider in self.edge_providers:
            if isinstance(provider, OllamaEdgeProvider):
                candidates.append(provider)

        if not candidates:
            candidates.extend(self.edge_providers)

        last_error = None
        for provider in candidates:
            try:
                logger.info(f"Generating OPD intake turn via {provider.provider_name}...")
                result = await provider.generate_structured(prompt, schema, system_prompt)
                logger.info(f"OPD intake turn successfully generated via {provider.provider_name}")
                return result
            except Exception as e:
                logger.warning(
                    f"Intake provider {provider.provider_name} failed ({type(e).__name__}: {e}). "
                    f"Cascading to next provider..."
                )
                last_error = e
                continue

        raise RuntimeError(
            f"All OPD intake LLM providers exhausted. Last error: {last_error}"
        )


    async def _execute(self, task_fn):
        """Run task across provider chain with failover."""
        candidates = []

        if settings.DEPLOYMENT_MODE == "STANDALONE":
            logger.info("Deployment mode STANDALONE: routing strictly to local Edge (Ollama GPU)")
            candidates.extend(self.edge_providers)
        else:
            if self.is_online():
                candidates.extend(self.cloud_providers)
                logger.debug("Network probe: ONLINE — cloud providers available")
            else:
                logger.info("Network probe: OFFLINE — routing to edge providers only")
            candidates.extend(self.edge_providers)

        if not candidates:
            raise RuntimeError(
                "No LLM providers available. Ensure Ollama is running: `ollama serve`"
            )

        last_error = None
        for provider in candidates:
            try:
                logger.debug(f"Attempting provider: {provider.provider_name}")
                result = await task_fn(provider)
                logger.info(f"Provider {provider.provider_name} succeeded")
                return result
            except Exception as e:
                logger.warning(
                    f"Provider {provider.provider_name} failed: {type(e).__name__}: {e}. "
                    f"Cascading to next provider..."
                )
                last_error = e
                continue

        raise RuntimeError(
            f"All {len(candidates)} LLM providers exhausted. Last error: {last_error}"
        )

    async def extract_prescription_vision(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg"
    ) -> Optional[ExtractedMedicationList]:
        """Attempt zero-shot prescription vision extraction via Gemini Flash if online."""
        if settings.DEPLOYMENT_MODE == "STANDALONE" or not self.is_online():
            return None

        for provider in self.cloud_providers:
            if isinstance(provider, GeminiFlashProvider):
                try:
                    logger.info("Extracting prescription via Gemini Flash Vision...")
                    result = await provider.generate_prescription_vision(image_bytes, mime_type)
                    logger.info(f"Gemini Flash Vision extracted {len(result.medications)} medications")
                    return result
                except Exception as e:
                    logger.warning(f"Gemini Flash Vision failed: {e}. Falling back to OCR.")
                    return None
        return None

    def get_status(self) -> dict:
        """Return current provider availability status (for health check endpoint)."""
        return {
            "is_online": self.is_online(),
            "cloud_providers": [p.provider_name for p in self.cloud_providers],
            "edge_providers": [p.provider_name for p in self.edge_providers],
            "total_providers": len(self.cloud_providers) + len(self.edge_providers)
        }


# ============================================================
# Singleton instance — initialized in main.py lifespan
# ============================================================
llm_service: Optional[ResilientLLMService] = None


def get_llm_service(force_new: bool = True) -> ResilientLLMService:
    """Get the LLM service instance, freshly initialized to pick up current settings."""
    global llm_service
    if force_new or llm_service is None:
        llm_service = ResilientLLMService()
    return llm_service
