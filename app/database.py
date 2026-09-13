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
        -- PATIENTS: Master demographic registry
        -- ============================================================
        CREATE TABLE IF NOT EXISTS patients (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            age             INTEGER,
            gender          TEXT,
            phone           TEXT,
            language        TEXT DEFAULT 'hi',
            abha_id         TEXT,
            hospital_mrn    TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- DOCTORS: Staff directory and consultation rooms
        -- ============================================================
        CREATE TABLE IF NOT EXISTS doctors (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            pin             TEXT DEFAULT '1234',
            department      TEXT NOT NULL,
            specialty       TEXT,
            room_number     TEXT,
            is_available    INTEGER DEFAULT 1,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- DEPARTMENTS: Hospital clinical specialty units
        -- ============================================================
        CREATE TABLE IF NOT EXISTS departments (
            id              TEXT PRIMARY KEY,
            name            TEXT NOT NULL UNIQUE,
            code            TEXT UNIQUE,
            description     TEXT,
            floor           TEXT,
            is_active       INTEGER DEFAULT 1
        );

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

        -- ============================================================
        -- USERS: Patients and Medical Professionals (Doctors/Clinicians)
        -- ============================================================
        CREATE TABLE IF NOT EXISTS users (
            id                  TEXT PRIMARY KEY,              -- 'pat-001' | 'doc-verma'
            role                TEXT NOT NULL,                 -- 'patient' | 'doctor'
            full_name           TEXT NOT NULL,
            email               TEXT,
            mobile              TEXT,                          -- '9876543210'
            abha_id             TEXT UNIQUE,                   -- '91-4821-3910-4819' (for patients)
            password_hash       TEXT NOT NULL,                 -- hashed password / PIN
            department          TEXT,                          -- for doctors: 'General Medicine', 'Kayachikitsa'
            room_number         TEXT,                          -- for doctors: 'Room 102'
            qualification       TEXT,                          -- for doctors: 'MD (Medicine)', 'MD (Ayu)'
            hospital_name       TEXT DEFAULT 'All India Institute of Ayurveda (AIIA), New Delhi',
            hospital_phone      TEXT DEFAULT '+91-11-26950401',
            created_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_users_abha ON users(abha_id);
        CREATE INDEX IF NOT EXISTS idx_users_mobile ON users(mobile);
        CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    """)

    # Run safe migrations for existing tables
    await _run_migrations(db)

    # Seed default staff and demo patient
    await _seed_default_users(db)

    await db.commit()
    logger.info("All database tables and migrations created/verified.")


async def _run_migrations(db: aiosqlite.Connection):
    """Safely apply schema migrations to existing database files."""
    # Migrations on encounters table
    cursor = await db.execute("PRAGMA table_info(encounters)")
    cols = [row[1] for row in await cursor.fetchall()]
    if "abha_id" not in cols:
        await db.execute("ALTER TABLE encounters ADD COLUMN abha_id TEXT")
    if "verified_by_doctor_id" not in cols:
        await db.execute("ALTER TABLE encounters ADD COLUMN verified_by_doctor_id TEXT")
    if "doctor_notes" not in cols:
        await db.execute("ALTER TABLE encounters ADD COLUMN doctor_notes TEXT")
    if "doctor_reviewed_at" not in cols:
        await db.execute("ALTER TABLE encounters ADD COLUMN doctor_reviewed_at TEXT")
    if "ayush_intake" not in cols:
        await db.execute("ALTER TABLE encounters ADD COLUMN ayush_intake TEXT")

    # Migrations on documents table
    cursor = await db.execute("PRAGMA table_info(documents)")
    doc_cols = [row[1] for row in await cursor.fetchall()]
    if "patient_id" not in doc_cols:
        await db.execute("ALTER TABLE documents ADD COLUMN patient_id TEXT")
    if "document_type" not in doc_cols:
        await db.execute("ALTER TABLE documents ADD COLUMN document_type TEXT DEFAULT 'prescription'")
    if "document_date" not in doc_cols:
        await db.execute("ALTER TABLE documents ADD COLUMN document_date TEXT")


async def _seed_default_users(db: aiosqlite.Connection):
    """Seed initial clinical staff and sample patient for instant evaluation."""
    doctors = [
        ("doc-verma", "doctor", "Dr. S. Verma", "verma@aiia.gov.in", "9811001101", None, "1234", "General Medicine", "Room 102", "MD (Internal Medicine)", "All India Institute of Ayurveda (AIIA), New Delhi", "+91-11-26950401"),
        ("doc-sharma", "doctor", "Dr. Ananya Sharma", "sharma@aiia.gov.in", "9811001102", None, "1234", "Kayachikitsa (AYUSH)", "Room 204", "BAMS, MD (Kayachikitsa)", "All India Institute of Ayurveda (AIIA), New Delhi", "+91-11-26950402"),
        ("doc-gupta", "doctor", "Dr. Rajesh Gupta", "gupta@aiia.gov.in", "9811001103", None, "1234", "Shalya Tantra (Surgery)", "Room 108", "MS (Ayu - Shalya)", "All India Institute of Ayurveda (AIIA), New Delhi", "+91-11-26950403"),
        ("doc-nair", "doctor", "Dr. Priya Nair", "nair@aiia.gov.in", "9811001104", None, "1234", "Kaumarbhritya (Pediatrics)", "Room 112", "MD (Kaumarbhritya)", "All India Institute of Ayurveda (AIIA), New Delhi", "+91-11-26950404"),
    ]
    for d in doctors:
        await db.execute("""
            INSERT OR IGNORE INTO users (id, role, full_name, email, mobile, abha_id, password_hash, department, room_number, qualification, hospital_name, hospital_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, d)

    # Seed sample patient Ramesh Kumar
    await db.execute("""
        INSERT OR IGNORE INTO users (id, role, full_name, email, mobile, abha_id, password_hash, department, room_number, qualification, hospital_name, hospital_phone)
        VALUES ('pat-001', 'patient', 'Ramesh Kumar', 'ramesh@example.com', '9876543210', '91-4821-3910-4819', 'patient123', NULL, NULL, NULL, 'All India Institute of Ayurveda (AIIA), New Delhi', '+91-11-26950401')
    """)
