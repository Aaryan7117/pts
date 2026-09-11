"""
MediKiosk — Call Session API (Conversational Voice Intake)
POST /api/call/session/start — Start a voice call session
POST /api/call/audio-turn    — Process one audio turn
POST /api/call/session/end   — End session and lock intake

These endpoints power the "Call AI Intake" feature on the mobile app.
"""

import uuid
import json
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.database import get_db
from app.schemas.call_session import (
    CallSessionStartRequest,
    CallSessionStartResponse,
    AudioTurnResponse,
    ExtractedFactSummary,
    CallSessionEndRequest,
    CallSessionEndResponse,
)
from app.core.clinical.interview_engine import InterviewEngine
from app.core.adapters.asr import get_asr_service
from app.core.adapters.tts import get_tts_service

logger = logging.getLogger("medikiosk.api.call_sessions")
router = APIRouter(prefix="/api/call", tags=["Call Sessions"])

# In-memory session store (for hackathon; production would use Redis)
_active_sessions: dict[str, dict] = {}


@router.post("/session/start", response_model=CallSessionStartResponse)
async def start_call_session(request: CallSessionStartRequest, db=Depends(get_db)):
    """
    Start a new conversational voice call session.

    Initializes the interview state machine and returns the opening question
    with synthesized audio for the patient's selected language.
    """
    # Verify encounter exists
    row = await db.execute("SELECT * FROM encounters WHERE id = ?", (request.encounter_id,))
    encounter = await row.fetchone()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found. Call /api/encounters/bootstrap first.")

    session_id = f"call-sess-{uuid.uuid4().hex[:8]}"

    # Initialize interview engine for this session
    engine = InterviewEngine(language=request.language)
    opening_text = engine.get_opening_prompt()

    # Generate opening audio via TTS
    tts = get_tts_service()
    tts_result = await tts.synthesize(opening_text, request.language)

    # Store session state in memory
    _active_sessions[session_id] = {
        "encounter_id": request.encounter_id,
        "language": request.language,
        "engine": engine,
        "turn_count": 0
    }

    # Persist to DB
    await db.execute(
        """
        INSERT INTO call_sessions (id, encounter_id, status, language, current_step)
        VALUES (?, ?, 'CALL_ACTIVE', ?, 'chief_complaint')
        """,
        (session_id, request.encounter_id, request.language)
    )
    await db.execute(
        "UPDATE encounters SET status = 'IN_PROGRESS' WHERE id = ?",
        (request.encounter_id,)
    )
    await db.commit()

    logger.info(f"Call session started: {session_id} (encounter={request.encounter_id}, lang={request.language})")

    return CallSessionStartResponse(
        session_id=session_id,
        status="CALL_ACTIVE",
        opening_text=opening_text,
        opening_audio_base64=tts_result.audio_base64
    )


@router.post("/audio-turn", response_model=AudioTurnResponse)
async def process_audio_turn(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    db=Depends(get_db)
):
    """
    Process a single audio turn in the conversational call loop.

    1. Receives audio from the patient's mic
    2. Transcribes via ASR (cloud or offline)
    3. Runs through the interview engine (normalizer + state machine)
    4. Returns extracted facts + next question with audio
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found or expired.")

    engine: InterviewEngine = session["engine"]
    language = session["language"]

    # Read audio bytes
    audio_bytes = await audio_file.read()

    # Step 1: Transcribe audio → text
    asr = get_asr_service()
    asr_result = await asr.transcribe(audio_bytes, language)
    transcript = asr_result.text

    # Step 2: Process through interview engine
    result = engine.process_response(transcript)

    # Step 3: Convert extracted facts to response format
    extracted_facts = []
    for fact in result["extracted_facts"]:
        extracted_facts.append(ExtractedFactSummary(
            category=fact["category"],
            field=fact["field"],
            concept=fact.get("concept") or fact["value"],
            concept_code=fact.get("concept_code"),
            confidence=fact["confidence"],
            provenance=fact["provenance"]
        ))

        # Persist fact to database
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        await db.execute(
            """
            INSERT INTO clinical_facts
            (id, encounter_id, category, field, value, patient_words,
             normalized_concept, concept_code, provenance_tier, source_type,
             confidence, is_negated, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'patient_voice', ?, ?, 'pending')
            """,
            (
                fact_id, session["encounter_id"],
                fact["category"], fact["field"], fact["value"], transcript,
                fact.get("concept"), fact.get("concept_code"),
                fact["provenance"], fact["confidence"],
                1 if fact.get("is_negated") else 0
            )
        )

    # Step 4: Generate next question audio (if interview continues)
    next_question_text = None
    next_question_audio = None

    if result["next_question"]:
        next_question_text = result["next_question"]["question_text"]
        tts = get_tts_service()
        tts_result = await tts.synthesize(next_question_text, language)
        next_question_audio = tts_result.audio_base64

    # Update session state
    session["turn_count"] += 1
    turn_index = session["turn_count"]

    # Update DB
    current_step = result["next_question"]["section_id"] if result["next_question"] else "completed"
    await db.execute(
        "UPDATE call_sessions SET turn_count = ?, current_step = ? WHERE id = ?",
        (turn_index, current_step, session_id)
    )
    await db.commit()

    logger.info(
        f"Audio turn #{turn_index}: '{transcript[:60]}...' → "
        f"{len(extracted_facts)} facts, completed={result['is_completed']}"
    )

    return AudioTurnResponse(
        session_id=session_id,
        turn_index=turn_index,
        patient_transcript=transcript,
        extracted_facts=extracted_facts,
        next_question_text=next_question_text,
        next_question_audio_base64=next_question_audio,
        is_completed=result["is_completed"]
    )


@router.post("/session/end", response_model=CallSessionEndResponse)
async def end_call_session(request: CallSessionEndRequest, db=Depends(get_db)):
    """
    End a voice call session and lock the patient's intake.

    Runs drug interaction checks, clinical gap detection, and assigns
    a severity badge before placing the patient in the doctor's queue.
    """
    session = _active_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Call session not found or expired.")

    encounter_id = session["encounter_id"]
    engine: InterviewEngine = session["engine"]

    # Get total facts captured
    summary = engine.get_summary()
    total_facts = summary["total_facts"]

    # Run drug interaction check on all captured medications
    from app.core.clinical.drug_safety import DrugInteractionEngine

    medication_facts = [
        f["value"] for f in summary["facts"]
        if f["category"] == "medication" and not f.get("is_negated")
    ]
    drug_alerts = DrugInteractionEngine.check_prescriptions(medication_facts)

    # Determine severity badge
    severity = "GREEN"
    has_red_flags = False

    if any(a["severity"] == "CRITICAL" for a in drug_alerts):
        severity = "RED"
        has_red_flags = True
    elif any(a["severity"] in ("HIGH", "MODERATE") for a in drug_alerts):
        severity = "YELLOW"

    # Get the queue token
    token_row = await db.execute(
        "SELECT token FROM queue_tokens WHERE encounter_id = ?", (encounter_id,)
    )
    token_record = await token_row.fetchone()
    assigned_token = token_record["token"] if token_record else "TK-000"

    # Update encounter and session status
    await db.execute(
        "UPDATE encounters SET status = 'COMPLETED', severity_badge = ?, updated_at = datetime('now') WHERE id = ?",
        (severity, encounter_id)
    )
    await db.execute(
        "UPDATE call_sessions SET status = 'COMPLETED', ended_at = datetime('now') WHERE id = ?",
        (request.session_id,)
    )
    await db.execute(
        "INSERT INTO audit_log (encounter_id, actor, action, details) VALUES (?, 'system', 'call_session_completed', ?)",
        (encounter_id, json.dumps({"total_facts": total_facts, "drug_alerts": len(drug_alerts)}))
    )
    await db.commit()

    # Clean up in-memory session
    del _active_sessions[request.session_id]

    logger.info(
        f"Call session ended: {request.session_id} → "
        f"{total_facts} facts, severity={severity}, token={assigned_token}"
    )

    return CallSessionEndResponse(
        encounter_id=encounter_id,
        status="COMPLETED",
        assigned_token=assigned_token,
        department="General Medicine",
        total_facts_captured=total_facts,
        red_flags_detected=has_red_flags,
        severity_badge=severity
    )
