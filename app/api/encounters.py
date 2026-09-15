"""
MediKiosk — Encounter Bootstrap API
POST /api/encounters/bootstrap — Initializes a new patient encounter.
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas.encounter import (
    EncounterBootstrapRequest,
    EncounterBootstrapResponse,
    EncounterSummary,
    EncounterFullStateResponse,
    EncounterStatusUpdate,
    EncounterLanguageUpdate,
    ConsentRequest,
    ConsentResponse,
    SUPPORTED_LANGUAGES
)

logger = logging.getLogger("medikiosk.api.encounters")
router = APIRouter(prefix="/api/encounters", tags=["Encounters"])


async def _generate_unique_token(db, requested_token: str | None = None) -> str:
    """Generate a guaranteed unique human-readable OPD token number."""
    import random
    if requested_token:
        cursor = await db.execute("SELECT 1 FROM encounters WHERE token_number = ?", (requested_token,))
        if not await cursor.fetchone():
            return requested_token
        # If collision on requested token, append a random 2-digit suffix
        suffix_token = f"{requested_token}-{random.randint(10, 99)}"
        return suffix_token

    for _ in range(50):
        prefix = random.choice(["A", "B", "C", "D", "K"])
        number = random.randint(100, 999)
        candidate = f"{prefix}-{number}"
        cursor = await db.execute("SELECT 1 FROM encounters WHERE token_number = ?", (candidate,))
        if not await cursor.fetchone():
            return candidate

    return f"T-{uuid.uuid4().hex[:6].upper()}"


@router.post("/bootstrap", response_model=EncounterBootstrapResponse)
async def bootstrap_encounter(request: EncounterBootstrapRequest, db=Depends(get_db)):
    """
    Initialize a new patient encounter.

    Creates an encounter record, assigns an encounter bearer token (B1),
    and returns supported languages. This is the first API call from any intake channel.
    """
    encounter_id = f"enc-{uuid.uuid4().hex[:8]}"
    patient_id = request.patient_id or f"pat-{uuid.uuid4().hex[:8]}"
    token = await _generate_unique_token(db, request.qr_token)
    bearer_token = f"enc_sec_{uuid.uuid4().hex}"
    token_expires_at = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    channel = request.get_channel()

    await db.execute(
        """
        INSERT INTO encounters (id, patient_id, token_number, language, channel, status, bearer_token, token_expires_at)
        VALUES (?, ?, ?, ?, ?, 'BOOTSTRAPPED', ?, ?)
        """,
        (encounter_id, patient_id, token, request.language, channel, bearer_token, token_expires_at)
    )

    await db.execute(
        """
        INSERT INTO queue_tokens (token, encounter_id, department, status, position)
        VALUES (?, ?, 'General Medicine', 'WAITING', (SELECT COALESCE(MAX(position), 0) + 1 FROM queue_tokens))
        """,
        (token, encounter_id)
    )

    await db.execute(
        """
        INSERT INTO audit_log (encounter_id, actor, action, details)
        VALUES (?, 'system', 'encounter_bootstrapped', ?)
        """,
        (encounter_id, json.dumps({"channel": channel, "language": request.language, "bearer_token_issued": True}))
    )

    await db.commit()

    logger.info(f"Encounter bootstrapped: {encounter_id} (token={token}, channel={channel})")

    return EncounterBootstrapResponse(
        encounter_id=encounter_id,
        patient_id=patient_id,
        token_number=token,
        bearer_token=bearer_token,
        status="BOOTSTRAPPED",
        supported_languages=SUPPORTED_LANGUAGES
    )


@router.post("/{encounter_id}/consent", response_model=ConsentResponse)
async def record_encounter_consent(encounter_id: str, request: ConsentRequest, db=Depends(get_db)):
    """Record patient informed consent for DPDP compliance (B7)."""
    cursor = await db.execute("SELECT id FROM encounters WHERE id = ?", (encounter_id,))
    if not await cursor.fetchone():
        raise HTTPException(status_code=404, detail="Encounter not found")

    consent_id = f"cst-{uuid.uuid4().hex[:8]}"
    granted_at = request.granted_at or datetime.utcnow().isoformat()

    await db.execute(
        """
        INSERT INTO consents (id, encounter_id, granted_at, language, consent_version, channel)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (consent_id, encounter_id, granted_at, request.language, request.consent_version, request.channel)
    )
    await db.execute(
        """
        INSERT INTO audit_log (encounter_id, actor, action, details)
        VALUES (?, 'patient', 'consent_granted', ?)
        """,
        (encounter_id, json.dumps({
            "consent_id": consent_id,
            "version": request.consent_version,
            "language": request.language,
            "channel": request.channel
        }))
    )
    await db.commit()
    logger.info(f"Consent recorded for encounter {encounter_id} (version={request.consent_version})")

    return ConsentResponse(
        encounter_id=encounter_id,
        status="CONSENT_RECORDED",
        consent_version=request.consent_version,
        recorded_at=granted_at
    )


@router.get("/{encounter_id}", response_model=EncounterFullStateResponse)
async def get_encounter(encounter_id: str, db=Depends(get_db)):
    """Get full encounter details and rehydration state (B6)."""
    row = await db.execute(
        "SELECT * FROM encounters WHERE id = ?", (encounter_id,)
    )
    encounter = await row.fetchone()

    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    encounter_dict = dict(encounter)

    # Fetch facts
    facts_cursor = await db.execute(
        "SELECT * FROM clinical_facts WHERE encounter_id = ? ORDER BY created_at ASC",
        (encounter_id,)
    )
    facts = [dict(r) for r in await facts_cursor.fetchall()]

    # Fetch documents
    docs_cursor = await db.execute(
        "SELECT id, document_type, ocr_status, highlighted_path, created_at FROM documents WHERE encounter_id = ?",
        (encounter_id,)
    )
    documents = [dict(r) for r in await docs_cursor.fetchall()]

    # Fetch active call session
    session_cursor = await db.execute(
        "SELECT * FROM call_sessions WHERE encounter_id = ? ORDER BY created_at DESC LIMIT 1",
        (encounter_id,)
    )
    session_row = await session_cursor.fetchone()
    call_session = dict(session_row) if session_row else None

    # Fetch queue status
    queue_cursor = await db.execute(
        "SELECT position FROM queue_tokens WHERE encounter_id = ? AND status = 'WAITING'",
        (encounter_id,)
    )
    queue_row = await queue_cursor.fetchone()
    queue_pos = queue_row["position"] if queue_row else None
    wait_est = queue_pos * 5 if queue_pos else None

    # Parse ayush_intake if present
    ayush_data = None
    if "ayush_intake" in encounter_dict and encounter_dict["ayush_intake"]:
        try:
            ayush_data = json.loads(encounter_dict["ayush_intake"])
        except Exception:
            ayush_data = None

    return EncounterFullStateResponse(
        encounter_id=encounter_dict["id"],
        patient_id=encounter_dict.get("patient_id"),
        token_number=encounter_dict["token_number"],
        channel=encounter_dict.get("channel", "kiosk"),
        language=encounter_dict.get("language", "hi"),
        status=encounter_dict["status"],
        severity_badge=encounter_dict.get("severity_badge", "GREEN"),
        department=encounter_dict.get("department", "General Medicine"),
        created_at=encounter_dict.get("created_at"),
        fact_count=len(facts),
        has_red_flags=encounter_dict.get("severity_badge") == "RED",
        clinical_facts=facts,
        documents=documents,
        active_call_session=call_session,
        ayush_intake=ayush_data,
        queue_position=queue_pos,
        estimated_wait_minutes=wait_est
    )


@router.patch("/{encounter_id}/status")
async def update_encounter_status(
    encounter_id: str,
    update: EncounterStatusUpdate,
    db=Depends(get_db)
):
    """Update encounter status."""
    await db.execute(
        "UPDATE encounters SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (update.status, encounter_id)
    )
    await db.execute(
        "INSERT INTO audit_log (encounter_id, actor, action, details) VALUES (?, 'system', 'status_updated', ?)",
        (encounter_id, f'{{"new_status": "{update.status}"}}')
    )
    await db.commit()

    return {"encounter_id": encounter_id, "status": update.status}


@router.patch("/{encounter_id}/language")
async def update_encounter_language(
    encounter_id: str,
    update: EncounterLanguageUpdate,
    db=Depends(get_db)
):
    """Update encounter preferred language."""
    cursor = await db.execute("SELECT 1 FROM encounters WHERE id = ?", (encounter_id,))
    if not await cursor.fetchone():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Encounter not found")

    await db.execute(
        "UPDATE encounters SET language = ?, updated_at = datetime('now') WHERE id = ?",
        (update.language, encounter_id)
    )
    await db.execute(
        "INSERT INTO audit_log (encounter_id, actor, action, details) VALUES (?, 'system', 'language_updated', ?)",
        (encounter_id, f'{{"new_language": "{update.language}"}}')
    )
    await db.commit()

    return {"encounter_id": encounter_id, "language": update.language}

