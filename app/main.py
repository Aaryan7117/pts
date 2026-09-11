"""
MediKiosk — FastAPI Application Entry Point
Unified backend serving Kiosk, Mobile App, and Doctor Dashboard.

Endpoints:
  /api/encounters/*     — Encounter bootstrap & management
  /api/call/*           — Conversational voice call intake
  /api/documents/*      — Prescription/document upload & OCR
  /api/queue/*          — Live OPD queue tracker
  /api/doctor/*         — Doctor dashboard (PIN-gated)
  /api/health           — System health check
  /docs                 — Interactive Swagger UI

Run: python run.py
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("medikiosk")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # === STARTUP ===
    logger.info("=" * 60)
    logger.info("  MediKiosk Backend — Starting Up")
    logger.info("  SIH26047 — Patient Case-Taking Software")
    logger.info("  Ministry of AYUSH / AIIA")
    logger.info("=" * 60)

    # Initialize database
    await init_db()

    # Create static file directories
    Path("./static/uploads").mkdir(parents=True, exist_ok=True)
    Path("./static/evidence").mkdir(parents=True, exist_ok=True)

    # Log provider availability
    from app.core.adapters.llm import get_llm_service
    llm = get_llm_service()
    status = llm.get_status()
    logger.info(f"Network: {'ONLINE' if status['is_online'] else 'OFFLINE'}")
    logger.info(f"Cloud LLM providers: {status['cloud_providers'] or 'None (offline mode)'}")
    logger.info(f"Edge LLM providers: {status['edge_providers']}")
    logger.info(f"Total providers: {status['total_providers']}")

    logger.info("")
    logger.info(f"  Swagger UI:  http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"  Health:      http://{settings.HOST}:{settings.PORT}/api/health")
    logger.info("")
    logger.info("=" * 60)

    yield

    # === SHUTDOWN ===
    logger.info("MediKiosk shutting down...")
    await close_db()
    logger.info("Shutdown complete.")


# Create FastAPI app
app = FastAPI(
    title="MediKiosk API",
    description=(
        "Edge-first clinical intake backend for SIH26047 — "
        "Patient Case-Taking Software (Ministry of AYUSH / AIIA). "
        "Serves Kiosk Web UI, Mobile BYOD App, and Doctor Dashboard."
    ),
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for hackathon (mobile app + kiosk on same LAN)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (uploaded prescriptions & evidence-boxed images)
Path("./static").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# === Register API Routers ===
from app.api.encounters import router as encounters_router
from app.api.call_sessions import router as call_sessions_router
from app.api.documents import router as documents_router
from app.api.queue import router as queue_router
from app.api.doctor import router as doctor_router

app.include_router(encounters_router)
app.include_router(call_sessions_router)
app.include_router(documents_router)
app.include_router(queue_router)
app.include_router(doctor_router)


# === Health Check ===
@app.get("/api/health", tags=["System"])
async def health_check():
    """
    System health check — shows provider availability and system status.
    Use this to verify the backend is running before connecting mobile apps.
    """
    from app.core.adapters.llm import get_llm_service

    llm = get_llm_service()
    llm_status = llm.get_status()

    return {
        "status": "healthy",
        "service": "MediKiosk Backend",
        "version": "3.0.0",
        "sih_problem_id": "SIH26047",
        "network": "ONLINE" if llm_status["is_online"] else "OFFLINE",
        "llm_providers": {
            "cloud": llm_status["cloud_providers"],
            "edge": llm_status["edge_providers"],
            "total": llm_status["total_providers"]
        },
        "endpoints": {
            "swagger": f"http://{settings.HOST}:{settings.PORT}/docs",
            "encounters": "/api/encounters/bootstrap",
            "call_start": "/api/call/session/start",
            "audio_turn": "/api/call/audio-turn",
            "call_end": "/api/call/session/end",
            "document_upload": "/api/documents/upload",
            "queue_status": "/api/queue/status/{token}",
            "doctor_auth": "/api/doctor/auth",
            "doctor_queue": "/api/doctor/queue",
            "doctor_patient": "/api/doctor/patient/{encounter_id}"
        }
    }
