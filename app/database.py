"""
MediKiosk — Async SQLite Database Manager
Uses aiosqlite with WAL mode for concurrent read/write on the edge laptop.
Tables: encounters, clinical_facts, documents, queue_tokens, call_sessions, audit_log
"""

import aiosqlite
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger("medikiosk.database")

# Global connection reference (set during lifespan)
_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    """FastAPI dependency — returns the active database connection."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db


async def init_db() -> aiosqlite.Connection:
    """Initialize the database: create file, enable WAL, create tables."""
    global _db

    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    _db = await aiosqlite.connect(str(db_path))
    _db.row_factory = aiosqlite.Row

    # Enable WAL mode for concurrent reads during writes (critical for kiosk + doctor dashboard)
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")

    await _create_tables(_db)
    logger.info(f"Database initialized at {db_path} (WAL mode)")
    return _db


async def close_db():
    """Gracefully close the database connection."""
    global _db
    if _db:
        await _db.close()
        _db = None
        logger.info("Database connection closed.")


async def _create_tables(db: aiosqlite.Connection):
    """Create all MediKiosk tables if they don't exist."""

    await db.executescript("""
        -- ============================================================
        -- ENCOUNTERS: Each patient visit / kiosk session
        -- ============================================================
        CREATE TABLE IF NOT EXISTS encounters (
            id              TEXT PRIMARY KEY,
            patient_id      TEXT,
            token_number    TEXT UNIQUE,
            language        TEXT DEFAULT 'hi',
            channel         TEXT DEFAULT 'kiosk',          -- kiosk | android_byod | ivr_phone
            status          TEXT DEFAULT 'BOOTSTRAPPED',   -- BOOTSTRAPPED | IN_PROGRESS | COMPLETED | DOCTOR_REVIEWED
            department      TEXT DEFAULT 'General Medicine',
            severity_badge  TEXT DEFAULT 'GREEN',          -- GREEN | YELLOW | RED
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- CLINICAL FACTS: Immutable, audited fact table (core data model)
        -- ============================================================
        CREATE TABLE IF NOT EXISTS clinical_facts (
            id                  TEXT PRIMARY KEY,
            encounter_id        TEXT NOT NULL REFERENCES encounters(id),
            category            TEXT NOT NULL,   -- chief_complaint | medication | allergy | vital | lab_result | ayush_agni | ayush_prakriti | ayush_ahara | symptom
            field               TEXT NOT NULL,
            value               TEXT NOT NULL,
            dose                TEXT,
            frequency           TEXT,
            patient_words       TEXT,
            normalized_concept  TEXT,
            concept_code        TEXT,            -- SNOMED:xxxxx or NAMASTE:xxxxx
            provenance_tier     TEXT NOT NULL,   -- TOUCH | LOOKUP | EMBEDDING | LLM | OCR
            source_type         TEXT,            -- patient_voice | document_ocr | explain_back_verified | touch_input
            source_reference    TEXT,            -- JSON blob: {document_id, line_indices, bbox, ocr_confidence, raw_text}
            confidence          REAL DEFAULT 0.0,
            confidence_breakdown TEXT,           -- JSON blob: {tier_score, input_quality, completeness}
            temporal_state      TEXT,            -- prescribed | taking | stopped | dose_changed
            valid_from          TEXT,
            valid_until         TEXT,
            is_negated          INTEGER DEFAULT 0,
            status              TEXT DEFAULT 'pending',  -- pending | patient_confirmed | explain_back_verified | doctor_reviewed
            created_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_facts_encounter ON clinical_facts(encounter_id);
        CREATE INDEX IF NOT EXISTS idx_facts_category ON clinical_facts(category);

        -- ============================================================
        -- DOCUMENTS: Scanned prescriptions and lab reports
        -- ============================================================
        CREATE TABLE IF NOT EXISTS documents (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            file_path       TEXT NOT NULL,
            ocr_status      TEXT DEFAULT 'PENDING',   -- PENDING | SUCCESS | LOW_CONFIDENCE | FAILED
            ocr_raw_text    TEXT,
            ocr_lines       TEXT,            -- JSON array of {line_index, text, bbox, confidence}
            highlighted_path TEXT,           -- Path to the evidence-boxed image
            created_at      TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- CALL SESSIONS: Conversational voice call intake sessions
        -- ============================================================
        CREATE TABLE IF NOT EXISTS call_sessions (
            id              TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            status          TEXT DEFAULT 'CALL_ACTIVE',  -- CALL_ACTIVE | CALL_ENDED | COMPLETED
            language        TEXT DEFAULT 'hi',
            current_step    TEXT DEFAULT 'chief_complaint',
            turn_count      INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now')),
            ended_at        TEXT
        );

        -- ============================================================
        -- QUEUE TOKENS: OPD waiting queue management
        -- ============================================================
        CREATE TABLE IF NOT EXISTS queue_tokens (
            token           TEXT PRIMARY KEY,
            encounter_id    TEXT NOT NULL REFERENCES encounters(id),
            department      TEXT DEFAULT 'General Medicine',
            status          TEXT DEFAULT 'WAITING',      -- WAITING | CALLED | IN_CONSULTATION | COMPLETED
            position        INTEGER DEFAULT 0,
            doctor_room     TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            called_at       TEXT
        );

        -- ============================================================
        -- AUDIT LOG: Immutable record of all doctor actions (DPDP compliance)
        -- ============================================================
        CREATE TABLE IF NOT EXISTS audit_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            encounter_id    TEXT REFERENCES encounters(id),
            actor           TEXT NOT NULL,        -- 'system' | 'doctor:<pin>' | 'patient'
            action          TEXT NOT NULL,        -- 'fact_created' | 'fact_confirmed' | 'encounter_reviewed' | 'audio_purged'
            details         TEXT,                 -- JSON blob with action-specific details
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_audit_encounter ON audit_log(encounter_id);
    """)

    await db.commit()
    logger.info("All database tables created/verified.")
