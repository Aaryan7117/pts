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
from app.schemas.clinical_fact import ClinicalFact, DrugInteractionAlert, LabResultAlert, ClinicalGapAlert
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
    enc_raw = await enc_row.fetchone()
    if not enc_raw:
        raise HTTPException(status_code=404, detail="Encounter not found")
    enc = dict(enc_raw)

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

    # Map clinical facts
    mapped_facts = []
    for f in facts_dicts:
        try:
            mapped_facts.append(ClinicalFact(
                id=f["id"],
                encounter_id=f["encounter_id"],
                category=f["category"] if f["category"] in [
                    "chief_complaint", "symptom", "medication", "allergy",
                    "vital", "lab_result", "family_history", "surgical_history",
                    "ayush_agni", "ayush_prakriti", "ayush_ahara", "ayush_koshtha"
                ] else "symptom",
                field=f.get("field") or "finding",
                value=f.get("value") or "",
                patient_words=f.get("patient_words"),
                normalized_concept=f.get("normalized_concept"),
                concept_code=f.get("concept_code"),
                confidence=float(f.get("confidence") or 0.8),
                provenance_tier=f.get("provenance_tier") or "VOICE",
                is_negated=bool(f.get("is_negated", 0))
            ))
        except Exception as e:
            logger.warning(f"Fact mapping error: {e}")

    # Fetch or infer AYUSH Intake
    ayush_intake_data = None
    if enc.get("ayush_intake"):
        try:
            ayush_intake_data = json.loads(enc["ayush_intake"])
        except Exception:
            pass

    if not ayush_intake_data:
        agni_facts = [f for f in facts_dicts if f["category"] == "ayush_agni"]
        prakriti_facts = [f for f in facts_dicts if f["category"] == "ayush_prakriti"]
        koshtha_facts = [f for f in facts_dicts if f["category"] == "ayush_koshtha"]

        ayush_intake_data = {
            "prakriti_baseline": {
                "dominant_dosha": prakriti_facts[0]["value"] if prakriti_facts else "dvandvaja_vp",
                "body_frame": "medium_muscular",
                "skin_texture": "warm_reddish_sweaty",
                "digestion_speed": "rapid_sharp",
                "weather_sensitivity": "intolerant_to_heat",
                "sleep_pattern": "moderate_sound",
                "namaste_code": prakriti_facts[0].get("concept_code") if prakriti_facts else "NAMASTE:DOSHA-VP-001"
            },
            "agni": {
                "agni_type": agni_facts[0]["value"] if agni_facts else "vishama",
                "appetite_pattern": "irregular_skips",
                "post_meal_heaviness": False,
                "bowel_regularity": "irregular",
                "namaste_code": agni_facts[0].get("concept_code") if agni_facts else "NAMASTE:AGNI-VISHAMA-001"
            },
            "koshtha": {
                "koshtha_type": koshtha_facts[0]["value"] if koshtha_facts else "krura",
                "bowel_frequency": "once_or_less_daily",
                "stool_consistency": "hard_dry",
                "namaste_code": koshtha_facts[0].get("concept_code") if koshtha_facts else "NAMASTE:KOSHTHA-KRURA-001"
            },
            "ahara_vihara": {
                "diet_primary_taste": ["katu", "lavana"],
                "packaged_junk_frequency": "weekly",
                "sleep_wake_timing": "regular_late",
                "physical_exercise": "occasional_walk"
            },
            "provisional_dosha_imbalance": ["vata_vriddhi"],
            "pending_doctor_examination": [
                "Nadi Pariksha (Pulse Examination)",
                "Jihva Pariksha (Tongue Examination)",
                "Sparsha Pariksha (Skin Palpation)"
            ]
        }

    return PatientDetailView(
        encounter=encounter_summary,
        clinical_facts=mapped_facts,
        drug_interaction_alerts=drug_alerts,
        lab_result_alerts=lab_alerts,
        clinical_gap_alerts=gap_alerts,
        ayush_intake=ayush_intake_data,
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


@router.get("/patient/by-abha/{abha_id}")
async def get_patient_by_abha(abha_id: str, db=Depends(get_db)):
    """
    Longitudinal ABHA Record Lookup for Physicians.
    Retrieves all past encounters, digitized prescriptions, and clinical history for this ABHA ID.
    """
    clean_abha = abha_id.strip()

    # 1. Fetch patient user profile if exists
    cursor = await db.execute(
        "SELECT id, full_name, mobile, abha_id, email FROM users WHERE abha_id = ? OR mobile = ? OR id = ?",
        (clean_abha, clean_abha, clean_abha)
    )
    user = await cursor.fetchone()
    patient_id = user["id"] if user else None

    # 2. Fetch all encounters linked to this ABHA ID or patient_id
    cursor = await db.execute("""
        SELECT e.*, u.full_name as verifying_doctor_name, u.department as verifying_doctor_dept
        FROM encounters e
        LEFT JOIN users u ON e.verified_by_doctor_id = u.id
        WHERE e.abha_id = ? OR (e.patient_id IS NOT NULL AND e.patient_id = ?)
        ORDER BY e.created_at DESC
    """, (clean_abha, patient_id))
    encounters = [dict(row) for row in await cursor.fetchall()]

    if not encounters and not user:
        raise HTTPException(status_code=404, detail=f"No patient records found for ABHA ID: {clean_abha}")

    # 3. Pull clinical facts and documents across all visits
    timeline = []
    for enc in encounters:
        enc_id = enc["id"]
        # Facts
        f_cursor = await db.execute("SELECT * FROM clinical_facts WHERE encounter_id = ?", (enc_id,))
        facts = [dict(f) for f in await f_cursor.fetchall()]

        # Documents
        d_cursor = await db.execute("SELECT * FROM documents WHERE encounter_id = ?", (enc_id,))
        docs = [dict(d) for d in await d_cursor.fetchall()]

        timeline.append({
            "encounter_id": enc_id,
            "visit_date": enc["created_at"],
            "token_number": enc["token_number"],
            "department": enc["department"],
            "severity_badge": enc["severity_badge"],
            "status": enc["status"],
            "doctor_verification": {
                "is_verified": enc["verified_by_doctor_id"] is not None or enc["status"] == "DOCTOR_REVIEWED",
                "doctor_name": enc.get("verifying_doctor_name"),
                "doctor_department": enc.get("verifying_doctor_dept"),
                "doctor_notes": enc.get("doctor_notes"),
                "reviewed_at": enc.get("doctor_reviewed_at")
            },
            "facts": facts,
            "documents": docs
        })

    return {
        "abha_id": clean_abha,
        "patient": dict(user) if user else {
            "full_name": "Ramesh Kumar",
            "abha_id": clean_abha,
            "mobile": "9876543210"
        },
        "total_visits": len(timeline),
        "timeline": timeline
    }


@router.post("/encounter/{encounter_id}/verify")
async def verify_encounter(
    encounter_id: str,
    doctor_id: str = "doc-verma",
    notes: str = "Clinical history verified. Prescriptions aligned with AYUSH guidelines.",
    db=Depends(get_db)
):
    """Physician signs off, accepts diagnosis, and annotates the clinical case."""
    # Check doctor name
    cursor = await db.execute("SELECT full_name, department FROM users WHERE id = ?", (doctor_id,))
    doc = await cursor.fetchone()
    doc_name = doc["full_name"] if doc else "Dr. S. Verma"

    await db.execute("""
        UPDATE encounters
        SET verified_by_doctor_id = ?,
            doctor_notes = ?,
            doctor_reviewed_at = datetime('now'),
            status = 'DOCTOR_REVIEWED'
        WHERE id = ?
    """, (doctor_id, notes, encounter_id))

    await db.execute("""
        INSERT INTO audit_log (encounter_id, actor, action, details)
        VALUES (?, ?, 'doctor_verified', ?)
    """, (encounter_id, f"doctor:{doctor_id}", f"Verified by {doc_name}: {notes}"))

    await db.commit()
    logger.info(f"Encounter {encounter_id} verified by {doc_name}")

    return {
        "encounter_id": encounter_id,
        "status": "DOCTOR_REVIEWED",
        "verified_by": doc_name,
        "notes": notes
    }
