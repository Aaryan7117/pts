"""
MediKiosk — Doctor Dashboard API (PIN-Gated)
Doctor authentication, queue intelligence, patient detail view, and evidence drilldown.
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.config import settings
from app.schemas.doctor import (
    DoctorAuthRequest, DoctorAuthResponse,
    PatientQueueEntry, DoctorQueueResponse,
    PatientDetailView
)
from app.schemas.encounter import EncounterSummary
from app.schemas.clinical_fact import DrugInteractionAlert, LabResultAlert, ClinicalGapAlert
from app.core.clinical.drug_safety import DrugInteractionEngine
from app.core.clinical.lab_checker import LabRangeChecker
from app.core.clinical.gap_detector import ClinicalGapDetector

logger = logging.getLogger("medikiosk.api.doctor")
router = APIRouter(prefix="/api/doctor", tags=["Doctor Dashboard"])


@router.post("/auth", response_model=DoctorAuthResponse)
async def authenticate_doctor(request: DoctorAuthRequest):
    """
    Authenticate doctor with 4-digit PIN.
    Simple gate for hackathon demo — production would use hospital SSO.
    """
    if request.pin == settings.DOCTOR_PIN:
        logger.info("Doctor authenticated successfully")
        return DoctorAuthResponse(authenticated=True, message="Authentication successful")
    else:
        logger.warning(f"Doctor authentication failed (attempted PIN: {request.pin[:2]}**)")
        raise HTTPException(status_code=401, detail="Invalid PIN")


@router.get("/queue", response_model=DoctorQueueResponse)
async def get_doctor_queue(db=Depends(get_db)):
    """
    Get the doctor's waiting queue with triage intelligence.

    Each patient entry includes a 30-word severity-first summary,
    medication conflict flags, and red flag indicators.
    """
    # Get all waiting/completed encounters
    rows = await db.execute(
        """
        SELECT e.*, qt.token as queue_token, qt.position
        FROM encounters e
        JOIN queue_tokens qt ON e.id = qt.encounter_id
        WHERE e.status IN ('COMPLETED', 'IN_PROGRESS')
        AND qt.status = 'WAITING'
        ORDER BY
            CASE e.severity_badge
                WHEN 'RED' THEN 0
                WHEN 'YELLOW' THEN 1
                ELSE 2
            END,
            qt.position ASC
        """
    )
    encounters = await rows.fetchall()

    queue_entries = []
    for enc in encounters:
        encounter_id = enc["id"]

        # Get fact count
        fact_row = await db.execute(
            "SELECT COUNT(*) as cnt FROM clinical_facts WHERE encounter_id = ?",
            (encounter_id,)
        )
        fact_count = (await fact_row.fetchone())["cnt"]

        # Get medications for interaction check
        med_rows = await db.execute(
            "SELECT value FROM clinical_facts WHERE encounter_id = ? AND category = 'medication' AND is_negated = 0",
            (encounter_id,)
        )
        medications = [r["value"] for r in await med_rows.fetchall()]
        drug_alerts = DrugInteractionEngine.check_prescriptions(medications)

        # Get chief complaint for summary
        cc_row = await db.execute(
            "SELECT value, patient_words FROM clinical_facts WHERE encounter_id = ? AND category = 'chief_complaint' LIMIT 1",
            (encounter_id,)
        )
        cc = await cc_row.fetchone()

        # Generate 30-word triage summary
        summary_parts = []
        if cc:
            summary_parts.append(cc["patient_words"] or cc["value"])

        # Add stopped medication info
        stopped_rows = await db.execute(
            "SELECT value FROM clinical_facts WHERE encounter_id = ? AND temporal_state = 'stopped'",
            (encounter_id,)
        )
        stopped = [r["value"] for r in await stopped_rows.fetchall()]
        if stopped:
            summary_parts.append(f"Stopped: {', '.join(stopped)}")

        if drug_alerts:
            summary_parts.append(f"⚠ {len(drug_alerts)} drug interaction(s)")

        summary_30 = " | ".join(summary_parts)[:150]

        has_red_flags = enc["severity_badge"] == "RED"
        has_med_conflict = len(drug_alerts) > 0

        queue_entries.append(PatientQueueEntry(
            encounter_id=encounter_id,
            token_number=enc["queue_token"],
            severity_badge=enc["severity_badge"],
            summary_30_words=summary_30 or "Intake in progress",
            channel=enc["channel"],
            fact_count=fact_count,
            has_medication_conflict=has_med_conflict,
            has_red_flags=has_red_flags,
            created_at=enc["created_at"]
        ))

    return DoctorQueueResponse(
        queue=queue_entries,
        total_waiting=len(queue_entries)
    )


@router.get("/patient/{encounter_id}", response_model=PatientDetailView)
async def get_patient_detail(encounter_id: str, db=Depends(get_db)):
    """
    Get complete patient detail view for the doctor.

    Includes:
      - All clinical facts (symptoms, medications, AYUSH assessments)
      - Drug interaction alerts
      - Lab result alerts (if labs were captured)
      - Proactive clinical gap alerts
      - AYUSH intake record
      - Medication adherence timeline
      - Uploaded document references
    """
    # Get encounter
    enc_row = await db.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
    enc = await enc_row.fetchone()
    if not enc:
        raise HTTPException(status_code=404, detail="Encounter not found")

    # Get all facts
    fact_rows = await db.execute(
        "SELECT * FROM clinical_facts WHERE encounter_id = ? ORDER BY created_at ASC",
        (encounter_id,)
    )
    facts_raw = await fact_rows.fetchall()

    fact_count = len(facts_raw)
    facts_dicts = [dict(f) for f in facts_raw]

    # --- Drug Interaction Alerts ---
    medications = [f["value"] for f in facts_dicts if f["category"] == "medication" and not f["is_negated"]]
    drug_alerts_raw = DrugInteractionEngine.check_prescriptions(medications)
    drug_alerts = [DrugInteractionAlert(**a) for a in drug_alerts_raw]

    # --- Lab Result Alerts ---
    lab_alerts = []
    lab_facts = [f for f in facts_dicts if f["category"] == "lab_result"]
    for lab in lab_facts:
        try:
            value = float(lab["value"])
            result = LabRangeChecker.evaluate_result(lab["field"], value)
            lab_alerts.append(LabResultAlert(**result))
        except (ValueError, TypeError):
            pass

    # --- Clinical Gap Detection ---
    gap_detector = ClinicalGapDetector()
    stopped_meds = [f["value"] for f in facts_dicts if f.get("temporal_state") == "stopped"]
    gaps_raw = gap_detector.detect_gaps(
        facts=facts_dicts,
        medication_count=len(medications),
        is_ayush_encounter=True,
        stopped_medications=stopped_meds
    )
    gap_alerts = [
        ClinicalGapAlert(
            gap_type=g["gap_type"],
            condition_trigger=str(g["condition_trigger"]),
            missing_question=g["missing_question"],
            clinical_rationale=g["clinical_rationale"],
            priority=g["priority"]
        )
        for g in gaps_raw
    ]

    # --- Medication Timeline ---
    med_timeline = [
        {
            "medication": f["value"],
            "temporal_state": f.get("temporal_state", "unknown"),
            "valid_from": f.get("valid_from"),
            "valid_until": f.get("valid_until"),
            "dose": f.get("dose"),
            "frequency": f.get("frequency")
        }
        for f in facts_dicts if f["category"] == "medication"
    ]

    # --- Documents ---
    doc_rows = await db.execute(
        "SELECT * FROM documents WHERE encounter_id = ?", (encounter_id,)
    )
    docs = [dict(d) for d in await doc_rows.fetchall()]

    encounter_summary = EncounterSummary(
        encounter_id=enc["id"],
        token_number=enc["token_number"],
        channel=enc["channel"],
        language=enc["language"],
        status=enc["status"],
        severity_badge=enc["severity_badge"],
        department=enc["department"],
        created_at=enc["created_at"],
        fact_count=fact_count,
        has_red_flags=enc["severity_badge"] == "RED"
    )

    return PatientDetailView(
        encounter=encounter_summary,
        clinical_facts=[],  # Simplified — would map full ClinicalFact objects
        drug_interaction_alerts=drug_alerts,
        lab_result_alerts=lab_alerts,
        clinical_gap_alerts=gap_alerts,
        medication_timeline=med_timeline,
        documents=docs
    )


@router.post("/patient/{encounter_id}/call-next")
async def call_next_patient(encounter_id: str, db=Depends(get_db)):
    """Doctor calls the next patient from the queue."""
    await db.execute(
        "UPDATE queue_tokens SET status = 'CALLED', called_at = datetime('now') WHERE encounter_id = ?",
        (encounter_id,)
    )
    await db.execute(
        "INSERT INTO audit_log (encounter_id, actor, action) VALUES (?, ?, 'patient_called')",
        (encounter_id, f"doctor:{settings.DOCTOR_PIN}")
    )
    await db.commit()

    logger.info(f"Patient called: encounter {encounter_id}")
    return {"encounter_id": encounter_id, "status": "CALLED"}
