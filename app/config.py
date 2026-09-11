"""
MediKiosk — Application Configuration
Loads settings from .env file with sensible defaults for offline-first operation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Central configuration — all values have offline-safe defaults."""

    # --- Server ---
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # --- Database ---
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./medikiosk.db")

    # --- Ollama (Local Edge LLM) ---
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    OLLAMA_FALLBACK_MODEL: str = os.getenv("OLLAMA_FALLBACK_MODEL", "qwen2.5:3b")

    # --- Groq (Cloud Speed LLM) ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    # --- Google Gemini (Cloud Quality LLM) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # --- Sarvam AI (Cloud ASR) ---
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")

    # --- Model Paths ---
    INDICWHISPER_MODEL_PATH: str = os.getenv("INDICWHISPER_MODEL_PATH", "./models/indicwhisper")
    INDICF5_MODEL_PATH: str = os.getenv("INDICF5_MODEL_PATH", "ai4bharat/IndicF5")
    CONCEPT_BANK_PATH: str = os.getenv("CONCEPT_BANK_PATH", "./app/data/concept_bank.json")

    # --- Security ---
    DOCTOR_PIN: str = os.getenv("DOCTOR_PIN", "1234")
    AUDIO_PURGE_AFTER_SECONDS: int = int(os.getenv("AUDIO_PURGE_AFTER_SECONDS", "300"))

    # --- Deployment Topology ---
    # Options: STANDALONE (single node), CLUSTER (thin-client + GPU edge node), CLOUD (Gemini/Groq/Sarvam)
    DEPLOYMENT_MODE: str = os.getenv("DEPLOYMENT_MODE", "STANDALONE").upper()
    SPEECH_SERVICE_URL: str = os.getenv("SPEECH_SERVICE_URL", "")

    # --- Derived ---
    @property
    def has_groq(self) -> bool:
        return bool(self.GROQ_API_KEY)

    @property
    def has_gemini(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def has_sarvam(self) -> bool:
        return bool(self.SARVAM_API_KEY)

    @property
    def has_remote_speech(self) -> bool:
        return bool(self.SPEECH_SERVICE_URL)

    @property
    def is_cluster(self) -> bool:
        return self.DEPLOYMENT_MODE == "CLUSTER"

    @property
    def is_cloud(self) -> bool:
        return self.DEPLOYMENT_MODE == "CLOUD"


settings = Settings()
