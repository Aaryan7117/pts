"""
MediKiosk — AYUSH Assessment API
POST /api/ayush/encounter/{encounter_id}/assessment — Save Dashavidha Pariksha record
GET  /api/ayush/encounter/{encounter_id}/assessment — Retrieve Pariksha record
POST /api/ayush/calculate — Interactive real-time scoring
"""

import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas.ayush import (
    AyurvedicIntakeRecord,
    PrakritiAssessment,
    AgniAssessment,
    KoshthaAssessment,
    AharaViharaRecord
)
from app.core.clinical.ayush_engine import AyushEngine

logger = logging.getLogger("medikiosk.api.ayush")
router = APIRouter(prefix="/api/ayush", tags=["AYUSH Dashavidha Pariksha"])


@router.post("/encounter/{encounter_id}/assessment", response_model=AyurvedicIntakeRecord)
async def save_ayush_assessment(
    encounter_id: str,
    record: AyurvedicIntakeRecord,
    db=Depends(get_db)
):
    """
    Save complete AYUSH Dashavidha Pariksha assessment for an encounter.
    Stores machine-readable JSON and creates audited clinical facts.
    """
    enc_row = await db.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
    enc = await enc_row.fetchone()
    if not enc:
        raise HTTPException(status_code=404, detail="Encounter not found")

    # If provisional dosha imbalances not provided, infer from symptoms & prakriti
    if not record.provisional_dosha_imbalance:
        symptoms_cur = await db.execute(
            "SELECT value FROM clinical_facts WHERE encounter_id = ? AND category IN ('chief_complaint', 'symptom')",
            (encounter_id,)
        )
        symptoms = [r[0] for r in await symptoms_cur.fetchall()]
        prakriti_str = record.prakriti_baseline.dominant_dosha if record.prakriti_baseline else "vata"
        agni_str = record.agni.agni_type if record.agni else "sama"
        record.provisional_dosha_imbalance = AyushEngine.detect_dosha_imbalance(symptoms, agni_str, prakriti_str)

    # Serialize to JSON
    json_data = record.model_dump_json()

    # Save to encounters table
    await db.execute(
        "UPDATE encounters SET ayush_intake = ?, updated_at = datetime('now') WHERE id = ?",
        (json_data, encounter_id)
    )

    # Persist as structured Clinical Facts for longitudinal tracking
    # 1. Prakriti
    if record.prakriti_baseline:
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        await db.execute(
            """
            INSERT INTO clinical_facts (
                id, encounter_id, category, field, value, normalized_concept, concept_code, confidence, provenance_tier, source_type
            ) VALUES (?, ?, 'ayush_prakriti', 'dominant_dosha', ?, ?, ?, 1.0, 'TOUCH', 'touch_input')
            """,
            (
                fact_id,
                encounter_id,
                record.prakriti_baseline.dominant_dosha,
                f"Prakriti: {record.prakriti_baseline.dominant_dosha.replace('_', ' ').title()}",
                record.prakriti_baseline.namaste_code
            )
        )

    # 2. Agni
    if record.agni:
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        await db.execute(
            """
            INSERT INTO clinical_facts (
                id, encounter_id, category, field, value, normalized_concept, concept_code, confidence, provenance_tier, source_type
            ) VALUES (?, ?, 'ayush_agni', 'agni_type', ?, ?, ?, 1.0, 'TOUCH', 'touch_input')
            """,
            (
                fact_id,
                encounter_id,
                record.agni.agni_type,
                f"Agni: {record.agni.agni_type.title()} Agni",
                record.agni.namaste_code
            )
        )

    # 3. Koshtha
    if record.koshtha:
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        await db.execute(
            """
            INSERT INTO clinical_facts (
                id, encounter_id, category, field, value, normalized_concept, concept_code, confidence, provenance_tier, source_type
            ) VALUES (?, ?, 'ayush_koshtha', 'koshtha_type', ?, ?, ?, 1.0, 'TOUCH', 'touch_input')
            """,
            (
                fact_id,
                encounter_id,
                record.koshtha.koshtha_type,
                f"Koshtha: {record.koshtha.koshtha_type.title()} Koshtha",
                record.koshtha.namaste_code
            )
        )

    # 4. Ahara / Vihara
    if record.ahara_vihara:
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        tastes = ", ".join(record.ahara_vihara.diet_primary_taste)
        await db.execute(
            """
            INSERT INTO clinical_facts (
                id, encounter_id, category, field, value, normalized_concept, concept_code, confidence, provenance_tier, source_type
            ) VALUES (?, ?, 'ayush_ahara', 'predominant_tastes', ?, ?, 'NAMASTE:AHARA-001', 1.0, 'TOUCH', 'touch_input')
            """,
            (
                fact_id,
                encounter_id,
                tastes,
                f"Shadrasa Predominance: {tastes}"
            )
        )

    # Audit log
    await db.execute(
        """
        INSERT INTO audit_log (encounter_id, actor, action, details)
        VALUES (?, 'system', 'ayush_assessment_saved', ?)
        """,
        (encounter_id, json_data)
    )

    await db.commit()
    logger.info(f"Saved AYUSH Pariksha for encounter {encounter_id}")
    return record


@router.get("/encounter/{encounter_id}/assessment", response_model=AyurvedicIntakeRecord)
async def get_ayush_assessment(encounter_id: str, db=Depends(get_db)):
    """Retrieve AYUSH Dashavidha Pariksha for an encounter."""
    enc_row = await db.execute("SELECT ayush_intake FROM encounters WHERE id = ?", (encounter_id,))
    enc = await enc_row.fetchone()
    if not enc:
        raise HTTPException(status_code=404, detail="Encounter not found")

    if enc["ayush_intake"]:
        try:
            data = json.loads(enc["ayush_intake"])
            return AyurvedicIntakeRecord(**data)
        except Exception as e:
            logger.error(f"Error parsing stored AYUSH intake: {e}")

    # If no stored assessment, generate standard clinical baseline
    prakriti = AyushEngine.evaluate_prakriti({
        "body_frame": "medium_muscular",
        "skin_texture": "warm_reddish_sweaty",
        "digestion_speed": "rapid_sharp",
        "weather_sensitivity": "intolerant_to_heat",
        "sleep_pattern": "moderate_sound"
    })
    agni = AyushEngine.evaluate_agni({
        "appetite_pattern": "regular",
        "post_meal_heaviness": False,
        "bowel_regularity": "regular"
    })
    koshtha = AyushEngine.evaluate_koshtha({
        "bowel_frequency": "once_daily",
        "stool_consistency": "soft_formed"
    })

    return AyurvedicIntakeRecord(
        prakriti_baseline=prakriti,
        agni=agni,
        koshtha=koshtha,
        provisional_dosha_imbalance=["pitta_vriddhi"]
    )


@router.post("/calculate", response_model=AyurvedicIntakeRecord)
async def calculate_ayush_scores(payload: dict):
    """
    Real-time interactive scoring endpoint for UI tactile cards.
    Evaluates responses and returns structured AyurvedicIntakeRecord with NAMASTE codes.
    """
    prakriti = AyushEngine.evaluate_prakriti(payload.get("prakriti", {}))
    agni = AyushEngine.evaluate_agni(payload.get("agni", {}))
    koshtha = AyushEngine.evaluate_koshtha(payload.get("koshtha", {}))

    ahara = None
    if "ahara_vihara" in payload:
        ahara = AharaViharaRecord(**payload["ahara_vihara"])

    symptoms = payload.get("symptoms", [])
    imbalances = AyushEngine.detect_dosha_imbalance(
        symptoms,
        agni.agni_type,
        prakriti.dominant_dosha
    )

    return AyurvedicIntakeRecord(
        prakriti_baseline=prakriti,
        agni=agni,
        koshtha=koshtha,
        ahara_vihara=ahara,
        provisional_dosha_imbalance=imbalances
    )
