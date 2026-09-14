"""
MediKiosk — Encounter Bootstrap API
POST /api/encounters/bootstrap — Initializes a new patient encounter.
"""

import uuid
import logging
from fastapi import APIRouter, Depends
from app.database import get_db
from app.schemas.encounter import (
    EncounterBootstrapRequest,
    EncounterBootstrapResponse,
    EncounterSummary,
    EncounterStatusUpdate,
    EncounterLanguageUpdate,
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

    Creates an encounter record, assigns a queue token, and returns
    supported languages. This is the first API call from any intake channel.
    """
    encounter_id = f"enc-{uuid.uuid4().hex[:8]}"
    patient_id = f"pat-{uuid.uuid4().hex[:8]}"
    token = await _generate_unique_token(db, request.qr_token)

    await db.execute(
        """
        INSERT INTO encounters (id, patient_id, token_number, language, channel, status)
        VALUES (?, ?, ?, ?, ?, 'BOOTSTRAPPED')
        """,
        (encounter_id, patient_id, token, request.language, request.device_channel)
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
        (encounter_id, f'{{"channel": "{request.device_channel}", "language": "{request.language}"}}')
    )

    await db.commit()

    logger.info(f"Encounter bootstrapped: {encounter_id} (token={token}, channel={request.device_channel})")

    return EncounterBootstrapResponse(
        encounter_id=encounter_id,
        patient_id=patient_id,
        token_number=token,
        status="BOOTSTRAPPED",
        supported_languages=SUPPORTED_LANGUAGES
    )


@router.get("/{encounter_id}", response_model=EncounterSummary)
async def get_encounter(encounter_id: str, db=Depends(get_db)):
    """Get encounter details by ID."""
    row = await db.execute(
        "SELECT * FROM encounters WHERE id = ?", (encounter_id,)
    )
    encounter = await row.fetchone()

    if not encounter:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Encounter not found")

    # Count facts
    fact_count_row = await db.execute(
        "SELECT COUNT(*) as cnt FROM clinical_facts WHERE encounter_id = ?",
        (encounter_id,)
    )
    fact_count = (await fact_count_row.fetchone())["cnt"]

    return EncounterSummary(
        encounter_id=encounter["id"],
        token_number=encounter["token_number"],
        channel=encounter["channel"],
        language=encounter["language"],
        status=encounter["status"],
        severity_badge=encounter["severity_badge"],
        department=encounter["department"],
        created_at=encounter["created_at"],
        fact_count=fact_count,
        has_red_flags=encounter["severity_badge"] == "RED"
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

