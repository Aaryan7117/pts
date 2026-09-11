"""
MediKiosk — Document Upload & OCR API
POST /api/documents/upload — Upload prescription photo, run OCR, extract medications.
"""

import uuid
import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.database import get_db
from app.schemas.document import DocumentUploadResponse, ExtractedMedication
from app.schemas.clinical_fact import DrugInteractionAlert
from app.core.adapters.ocr import get_ocr_service
from app.core.adapters.llm import get_llm_service, ExtractedMedicationList
from app.core.clinical.drug_safety import DrugInteractionEngine

logger = logging.getLogger("medikiosk.api.documents")
router = APIRouter(prefix="/api/documents", tags=["Documents"])

# Static file directory for uploaded and processed images
UPLOAD_DIR = Path("./static/uploads")
EVIDENCE_DIR = Path("./static/evidence")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    encounter_id: str = Form(...),
    document: UploadFile = File(...),
    db=Depends(get_db)
):
    """
    Upload a prescription/lab document photo and process it.

    Pipeline:
      1. Save uploaded image
      2. Run RapidOCR to extract text lines with bounding polygons
      3. Send line-indexed text to LLM for structured medication extraction
      4. Run drug interaction check on extracted medications
      5. Generate evidence-boxed image with highlighted line regions
      6. Return extracted medications + alerts + evidence image URL
    """
    # Verify encounter exists
    row = await db.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
    encounter = await row.fetchone()
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    document_id = f"doc-{uuid.uuid4().hex[:8]}"

    # Save uploaded file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / f"{document_id}_{document.filename}"
    image_bytes = await document.read()
    file_path.write_bytes(image_bytes)

    logger.info(f"Document saved: {file_path} ({len(image_bytes)} bytes)")

    # Step 1: Run OCR
    ocr_service = get_ocr_service()
    try:
        ocr_result = ocr_service.process_image(image_bytes)
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        # Save document record as failed
        await db.execute(
            "INSERT INTO documents (id, encounter_id, file_path, ocr_status) VALUES (?, ?, ?, 'FAILED')",
            (document_id, encounter_id, str(file_path))
        )
        await db.commit()
        return DocumentUploadResponse(
            document_id=document_id,
            ocr_status="FAILED",
            raw_ocr_text="",
            overall_ocr_confidence=0.0
        )

    # Check OCR confidence — refuse if too low
    if ocr_result.overall_confidence < 0.50:
        logger.warning(f"OCR confidence too low: {ocr_result.overall_confidence:.2f}")
        await db.execute(
            """
            INSERT INTO documents (id, encounter_id, file_path, ocr_status, ocr_raw_text, ocr_lines)
            VALUES (?, ?, ?, 'LOW_CONFIDENCE', ?, ?)
            """,
            (document_id, encounter_id, str(file_path), ocr_result.raw_text,
             json.dumps(ocr_result.to_dict()["lines"]))
        )
        await db.commit()
        return DocumentUploadResponse(
            document_id=document_id,
            ocr_status="LOW_CONFIDENCE",
            raw_ocr_text=ocr_result.raw_text,
            overall_ocr_confidence=ocr_result.overall_confidence
        )

    # Step 2: Send line-indexed text to LLM for medication extraction
    extracted_meds: list[ExtractedMedication] = []

    try:
        llm = get_llm_service()
        system_prompt = (
            "You are a clinical prescription parser. Extract all medications from the OCR text below. "
            "For each medication, provide: name, dose, frequency, and the exact source line numbers "
            "from the OCR output (source_lines). Only extract what is explicitly written. "
            "Do NOT invent or guess medications."
        )
        prompt = f"OCR Text (line-indexed):\n{ocr_result.indexed_text}"

        med_list = await llm.generate_structured(prompt, ExtractedMedicationList, system_prompt)
        extracted_meds = [
            ExtractedMedication(
                name=m.name,
                dose=m.dose,
                frequency=m.frequency,
                source_lines=m.source_lines,
                confidence=ocr_result.overall_confidence
            )
            for m in med_list.medications
        ]

        logger.info(f"LLM extracted {len(extracted_meds)} medications from document")
    except Exception as e:
        logger.warning(f"LLM extraction failed: {e}. Returning raw OCR only.")

    # Step 3: Run drug interaction check
    med_names = [m.name for m in extracted_meds]

    # Also check against existing encounter medications
    existing_meds_row = await db.execute(
        "SELECT value FROM clinical_facts WHERE encounter_id = ? AND category = 'medication' AND is_negated = 0",
        (encounter_id,)
    )
    existing_meds = [row["value"] for row in await existing_meds_row.fetchall()]
    all_meds = med_names + existing_meds

    drug_alerts_raw = DrugInteractionEngine.check_prescriptions(all_meds)
    drug_alerts = [
        DrugInteractionAlert(**alert) for alert in drug_alerts_raw
    ]

    # Step 4: Generate evidence-boxed image
    highlighted_path = ""
    if extracted_meds:
        all_source_lines = []
        for m in extracted_meds:
            all_source_lines.extend(m.source_lines)

        evidence_file = str(EVIDENCE_DIR / f"{document_id}-boxed.jpg")
        try:
            highlighted_path = ocr_service.generate_evidence_image(
                image_bytes, all_source_lines, evidence_file
            )
        except Exception as e:
            logger.warning(f"Evidence image generation failed: {e}")

    # Step 5: Save to database
    await db.execute(
        """
        INSERT INTO documents
        (id, encounter_id, file_path, ocr_status, ocr_raw_text, ocr_lines, highlighted_path)
        VALUES (?, ?, ?, 'SUCCESS', ?, ?, ?)
        """,
        (
            document_id, encounter_id, str(file_path),
            ocr_result.raw_text,
            json.dumps(ocr_result.to_dict()["lines"]),
            highlighted_path
        )
    )

    # Save extracted medications as clinical facts
    for med in extracted_meds:
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        source_ref = json.dumps({
            "type": "document_ocr",
            "document_id": document_id,
            "line_indices": med.source_lines,
            "ocr_confidence": med.confidence,
            "raw_text": med.name
        })
        await db.execute(
            """
            INSERT INTO clinical_facts
            (id, encounter_id, category, field, value, dose, frequency,
             provenance_tier, source_type, source_reference, confidence,
             temporal_state, status)
            VALUES (?, ?, 'medication', 'current_medication', ?, ?, ?,
                    'OCR', 'document_ocr', ?, ?, 'prescribed', 'pending')
            """,
            (
                fact_id, encounter_id, med.name, med.dose, med.frequency,
                source_ref, med.confidence
            )
        )

    await db.commit()

    # Build response URL for highlighted image
    highlighted_url = ""
    if highlighted_path:
        highlighted_url = f"http://localhost:8000/static/evidence/{document_id}-boxed.jpg"

    return DocumentUploadResponse(
        document_id=document_id,
        ocr_status="SUCCESS",
        extracted_medications=extracted_meds,
        flagged_interactions=drug_alerts,
        highlighted_image_url=highlighted_url,
        raw_ocr_text=ocr_result.raw_text,
        overall_ocr_confidence=ocr_result.overall_confidence
    )
