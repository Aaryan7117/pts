"""
MediKiosk — Document Upload & Clinical Extraction API
Supports single and batch uploads for Prescriptions, Lab Reports, and Discharge Summaries.
Integrates RapidOCR/Gemini Vision, Drug Interaction Engine, and Physiological Lab Range Checker.
"""

import uuid
import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from app.database import get_db
from app.schemas.document import (
    DocumentUploadResponse,
    BatchDocumentUploadResponse,
    ExtractedMedication
)
from app.schemas.clinical_fact import DrugInteractionAlert
from app.core.adapters.ocr import get_ocr_service
from app.core.adapters.llm import get_llm_service, ExtractedMedicationList
from app.core.clinical.drug_safety import DrugInteractionEngine
from app.core.clinical.lab_checker import LabRangeChecker

logger = logging.getLogger("medikiosk.api.documents")
router = APIRouter(prefix="/api/documents", tags=["Documents"])

UPLOAD_DIR = Path("./static/uploads")
EVIDENCE_DIR = Path("./static/evidence")


def _extract_medications_rule_based(ocr_lines: list) -> list[ExtractedMedication]:
    """
    Deterministic rule-based medical entity extractor for offline prescriptions.
    Guarantees extraction even if local LLM is cold, slow, or times out.
    Accurately extracts brand names, generic formulations, doses, and frequencies.
    """
    import re
    extracted = []

    # Common medication names in India and worldwide
    COMMON_MEDS = {
        "paracetamol", "dolo", "crocin", "calpol", "pcm", "combiflam",
        "azithromycin", "azithral", "amoxicillin", "amox", "augmentin", "moxikind", "clavum",
        "pantoprazole", "pantocid", "pan", "pan-d", "pantop", "omez", "omeprazole", "rabeprazole", "rabicer",
        "metformin", "glycomet", "glyciphage", "glimepiride", "amaryl", "vildagliptin", "galvus", "teneligliptin",
        "cetirizine", "cetzine", "allegra", "fexofenadine", "levocetirizine", "montek", "montair",
        "telmisartan", "telma", "telmikind", "amlodipine", "amlong", "stamlo", "losartan", "atenolol",
        "atorvastatin", "atorva", "atorlip", "rosuvastatin", "rosuvas", "ecosprin", "aspirin", "clopidogrel",
        "thyronorm", "eltroxin", "levothyroxine",
        "ciprofloxacin", "ofloxacin", "cefixime", "zifi", "taxim",
        "ibuprofen", "brufen", "aceclofenac", "zerodol", "diclofenac", "voveran", "tramadol",
        "shelcal", "calcium", "limcee", "vitamin", "vit", "becosules", "supradyn", "neurobion",
        "ranitidine", "zantac", "rantac", "ondansetron", "emset", "vomikind", "domperidone",
        "salbutamol", "asthalin", "budecort", "foracort", "duolin", "montair-lc", "montek-lc"
    }

    # Drug class suffix patterns
    DRUG_SUFFIXES = (
        r'(?:cillin|mycin|micin|zole|statin|sartan|olol|pril|dipine|floxacin|fenac|'
        r'mab|gliptin|glitazone|tidine|prazole|sone|nide|xacin|profen|mide|zide|parin)\b'
    )

    skip_words = {
        'patient', 'clinic', 'hospital', 'doctor', 'date', 'dr.', 'dr', 'consultant',
        'reg.', 'reg', 'mbbs', 'md', 'ms', 'diagnosis', 'advice', 'follow up', 'followup',
        'duration', 'take', 'signature', 'sign', 'chief', 'complaint', 'history',
        'examination', 'investigation', 'rx', 'name', 'age', 'sex', 'gender', 'weight'
    }

    for idx, line_obj in enumerate(ocr_lines):
        if isinstance(line_obj, str):
            line_str = line_obj.strip()
            line_idx = idx
        elif isinstance(line_obj, dict):
            line_str = line_obj.get("text", "").strip()
            line_idx = line_obj.get("line_index", idx)
        else:
            line_str = getattr(line_obj, "text", "").strip()
            line_idx = getattr(line_obj, "line_index", idx)

        if not line_str or len(line_str) < 3:
            continue

        # Intelligent OCR token ungluing (common when RapidOCR groups words together)
        line_str = re.sub(r'^(Tab|Cap|Syp|Inj|Drops|Ointment|Tablet|Capsule)\.?(?=[a-zA-Z])', r'\1 ', line_str, flags=re.I)
        line_str = re.sub(r'([a-zA-Z]{3,})(\d+)', r'\1 \2', line_str)
        line_str = re.sub(r'(mg|mcg|gm|ml|iu)(?=[0-9a-zA-Z])', r'\1 ', line_str, flags=re.I)

        # Ignore obvious headers and administrative lines
        if re.match(r'^(?:Take|Apply|Use|Give|Duration|Advice|Diagnosis|Date|Age|UHID|Ph|Reg|Consultation|Follow|Name|Sex|Weight)\b', line_str, re.I):
            continue

        num_match = re.match(r'^(?:\d+[\.\)]\s*|(?:Tab|Cap|Syp|Inj|Drops|Ointment|Tablet|Capsule)\.?\s+)(.+)$', line_str, re.I)
        candidate = num_match.group(1).strip() if num_match else line_str

        # Dose regex: e.g. 500mg, 650 mg, 40mg, 10 mg, 500, 650, 0.5mg, 50mcg, 5ml
        dose_m = re.search(r'(\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|iu|%)\b)', candidate, re.I)
        if not dose_m:
            dose_num_m = re.search(r'\b(650|625|500|250|100|40|20|10|5|2\.5)\b', candidate)
            if dose_num_m and any(w in candidate.lower() for w in ["dolo", "pan", "augmentin", "glycomet", "telma", "atorva", "calpol", "crocin"]):
                dose_val = f"{dose_num_m.group(1)}mg"
            else:
                dose_val = None
        else:
            dose_val = dose_m.group(1)

        has_form = bool(re.search(r'\b(?:Tab|Cap|Syp|Suspension|Inj|Tablet|Capsule|Drops|Ointment)\b', line_str, re.I))
        has_freq = bool(re.search(r'\b(?:OD|BD|TDS|QID|1-0-1|1-0-0|0-0-1|1-1-1|0-1-0|HS|SOS|daily|twice|thrice|times|meals|bedtime)\b', line_str, re.I))

        # Check if line contains a known medication or medical drug suffix
        words_in_line = set(re.findall(r'[a-zA-Z\-]+', candidate.lower()))
        matched_common_med = bool(words_in_line.intersection(COMMON_MEDS)) or any(med in candidate.lower() for med in COMMON_MEDS)
        matched_suffix = bool(re.search(DRUG_SUFFIXES, candidate, re.I))

        is_med_candidate = (
            num_match is not None or
            (dose_val is not None and (has_form or has_freq or matched_common_med or matched_suffix or len(candidate.split()) <= 4)) or
            matched_common_med or
            (has_form and (matched_suffix or len(candidate.split()) <= 3))
        )

        if not is_med_candidate:
            continue

        clean_name = re.sub(r'\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|ml|iu|%)\b', '', candidate, flags=re.I)
        clean_name = re.sub(r'\((?:Tab|Cap|Syp|Suspension|Inj|Tablet|Capsule)\)', '', clean_name, flags=re.I).strip()
        clean_name = re.sub(r'^(?:Tab|Cap|Syp|Inj|Tablet|Capsule)\.?\s+', '', clean_name, flags=re.I).strip()
        clean_name = re.sub(r'\b(?:OD|BD|TDS|QID|HS|SOS|daily|meals|bedtime)\b', '', clean_name, flags=re.I).strip()
        clean_name = re.sub(r'\b\d+-\d+(?:-\d+)?\b', '', clean_name).strip()
        clean_name = re.sub(r'\b(?:x\s*)?\d+\s*(?:days?|weeks?|months?)\b', '', clean_name, flags=re.I).strip()
        clean_name = re.sub(r'\b(?:before|after)(?:\s*(?:food|meals?))?\b', '', clean_name, flags=re.I).strip()
        clean_name = re.sub(r'\s+', ' ', clean_name).strip(' -.,')

        if not clean_name or len(clean_name) < 3 or clean_name.lower() in skip_words:
            continue

        if any(skip in clean_name.lower() for skip in ['hospital', 'clinic', 'diagnosis', 'doctor', 'patient']):
            continue

        freq_val = None
        freq_m = re.search(r'\b(OD|BD|TDS|QID|1-0-1|1-0-0|0-0-1|1-1-1|0-1-0|HS|SOS|once daily|twice daily|thrice daily)\b', line_str, re.I)
        if freq_m:
            freq_val = freq_m.group(1).upper()

        source_lines = [line_idx]

        if not freq_val:
            for next_offset in [1, 2]:
                if idx + next_offset < len(ocr_lines):
                    next_l = ocr_lines[idx + next_offset]
                    if isinstance(next_l, str):
                        next_text = next_l.strip()
                        next_idx = idx + next_offset
                    elif isinstance(next_l, dict):
                        next_text = next_l.get("text", "").strip()
                        next_idx = next_l.get("line_index", idx + next_offset)
                    else:
                        next_text = getattr(next_l, "text", "").strip()
                        next_idx = getattr(next_l, "line_index", idx + next_offset)

                    next_freq_m = re.search(r'\b(OD|BD|TDS|QID|1-0-1|1-0-0|0-0-1|1-1-1|0-1-0|HS|SOS|daily|after meals|before meals|times)\b', next_text, re.I)
                    if next_freq_m and not re.match(r'^\d+[\.\)]', next_text):
                        freq_val = next_text
                        source_lines.append(next_idx)
                        break

        conf = getattr(line_obj, "confidence", 0.9) if not isinstance(line_obj, dict) else line_obj.get("confidence", 0.9)
        extracted.append(ExtractedMedication(
            name=clean_name.title(),
            dose=dose_val,
            frequency=freq_val or "OD",
            source_lines=source_lines,
            confidence=round(float(conf), 2)
        ))

    return extracted


async def _process_single_document(
    encounter_id: str,
    document: UploadFile,
    document_type: str,
    document_date: Optional[str],
    patient_id: Optional[str],
    db
) -> DocumentUploadResponse:
    """Internal helper to process an individual prescription or lab report document."""
    # Verify encounter exists or auto-provision
    row = await db.execute("SELECT * FROM encounters WHERE id = ?", (encounter_id,))
    enc_raw = await row.fetchone()
    if not enc_raw:
        logger.info(f"Auto-provisioning encounter for document upload: {encounter_id}")
        token = f"T-{uuid.uuid4().hex[:4].upper()}"
        await db.execute(
            """
            INSERT OR IGNORE INTO encounters (id, token_number, language, channel, status)
            VALUES (?, ?, 'hi', 'mobile_byod', 'IN_PROGRESS')
            """,
            (encounter_id, token)
        )
        await db.commit()
        enc_raw = {"id": encounter_id, "token_number": token}
    encounter = dict(enc_raw)

    linked_patient_id = patient_id or encounter.get("patient_id")

    document_id = f"doc-{uuid.uuid4().hex[:8]}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / f"{document_id}_{document.filename}"
    image_bytes = await document.read()
    file_path.write_bytes(image_bytes)

    logger.info(f"Document saved: {file_path} ({len(image_bytes)} bytes), type={document_type}")

    llm = get_llm_service()
    ocr_service = get_ocr_service()
    extracted_meds: list[ExtractedMedication] = []
    ocr_status = "SUCCESS"
    raw_ocr_text = ""
    overall_conf = 0.95
    ocr_lines_data = []
    highlighted_path = ""
    evidence_file = str(EVIDENCE_DIR / f"{document_id}-boxed.jpg")

    # Step 1: Vision / OCR Extraction
    try:
        vision_result = await llm.extract_prescription_vision(image_bytes)
    except Exception as e:
        logger.warning(f"Vision extraction raised exception: {e}. Falling back to OCR.")
        vision_result = None
    if vision_result and vision_result.medications:
        logger.info(f"Gemini Flash Vision extracted {len(vision_result.medications)} medications")
        extracted_meds = [
            ExtractedMedication(
                name=m.name,
                dose=m.dose,
                frequency=m.frequency,
                source_lines=m.source_lines or [],
                box_2d=m.box_2d,
                confidence=m.confidence
            )
            for m in vision_result.medications
        ]
        ocr_status = "SUCCESS"
        raw_ocr_text = "\n".join(f"{m.name} {m.dose or ''} {m.frequency or ''}".strip() for m in extracted_meds)
        ocr_lines_data = [
            {
                "line_index": idx + 1,
                "text": f"{m.name} {m.dose or ''} {m.frequency or ''}".strip(),
                "confidence": m.confidence or 0.95,
                "box_2d": m.box_2d
            }
            for idx, m in enumerate(extracted_meds)
        ]

        boxes = [m.box_2d for m in extracted_meds if m.box_2d]
        if boxes:
            try:
                highlighted_path = ocr_service.generate_evidence_image_from_boxes(
                    image_bytes, boxes, evidence_file
                )
            except Exception as e:
                logger.warning(f"Vision evidence boxing failed: {e}")
    else:
        # Offline Floor Route: RapidOCR + Local LLM
        try:
            ocr_result = ocr_service.process_image(image_bytes)
            overall_conf = ocr_result.overall_confidence
            raw_ocr_text = ocr_result.raw_text
            ocr_lines_data = ocr_result.to_dict()["lines"]
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            await db.execute(
                """
                INSERT INTO documents (id, encounter_id, patient_id, document_type, document_date, file_path, ocr_status)
                VALUES (?, ?, ?, ?, ?, ?, 'FAILED')
                """,
                (document_id, encounter_id, linked_patient_id, document_type, document_date, str(file_path))
            )
            await db.commit()
            return DocumentUploadResponse(
                document_id=document_id,
                ocr_status="FAILED",
                document_type=document_type,
                raw_ocr_text="",
                overall_ocr_confidence=0.0
            )

        if ocr_result.overall_confidence < 0.35:
            logger.warning(f"OCR confidence low: {ocr_result.overall_confidence:.2f}")
            ocr_status = "LOW_CONFIDENCE"

        # Medication Extraction for prescriptions
        if document_type != "lab_report":
            try:
                system_prompt = (
                    "You are a clinical prescription parser. Extract all medications from the OCR text below. "
                    "For each medication, provide: name, dose, frequency, and source line numbers. "
                    "Only extract what is explicitly written."
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
            except Exception as e:
                logger.warning(f"LLM extraction skipped/fallback: {e}")

            # Deterministic offline rule-based fallback if LLM extraction was empty or timed out
            if not extracted_meds and ocr_result and ocr_result.lines:
                extracted_meds = _extract_medications_rule_based(ocr_result.lines)
                if extracted_meds:
                    logger.info(f"Rule-based fallback extracted {len(extracted_meds)} medications from OCR lines")

        # Highlight lines if medications found
        if extracted_meds:
            all_source_lines = []
            for m in extracted_meds:
                all_source_lines.extend(m.source_lines)
            try:
                highlighted_path = ocr_service.generate_evidence_image(
                    image_bytes, all_source_lines, evidence_file
                )
            except Exception as e:
                logger.warning(f"Evidence boxing failed: {e}")

    # Step 2: Lab Value Extraction & Physiological Outlier Check
    extracted_labs = []
    flagged_labs = []
    parsed_labs = LabRangeChecker.extract_lab_values_from_text(raw_ocr_text)
    for lab_item in parsed_labs:
        eval_res = LabRangeChecker.evaluate_result(
            test_name=lab_item["test_name"],
            value=lab_item["value"],
            gender=encounter.get("patient_gender")
        )
        extracted_labs.append(eval_res)
        if eval_res["status"] != "NORMAL":
            flagged_labs.append(eval_res)

        # Save to clinical_facts as lab_result
        fact_id = f"fact-{uuid.uuid4().hex[:8]}"
        await db.execute(
            """
            INSERT INTO clinical_facts
            (id, encounter_id, category, field, value, dose, normalized_concept,
             provenance_tier, source_type, confidence, status)
            VALUES (?, ?, 'lab_result', ?, ?, ?, ?, 'OCR', 'document_ocr', ?, 'pending')
            """,
            (
                fact_id, encounter_id, lab_item["test_name"], str(lab_item["value"]),
                lab_item.get("unit", ""), eval_res.get("display_name", lab_item["test_name"]),
                overall_conf
            )
        )

    # Step 3: Drug Interaction Check
    med_names = [m.name for m in extracted_meds]
    existing_meds_row = await db.execute(
        "SELECT value FROM clinical_facts WHERE encounter_id = ? AND category = 'medication' AND is_negated = 0",
        (encounter_id,)
    )
    existing_meds = [row[0] for row in await existing_meds_row.fetchall()]
    all_meds = med_names + existing_meds

    drug_alerts_raw = DrugInteractionEngine.check_prescriptions(all_meds)
    drug_alerts = [DrugInteractionAlert(**alert) for alert in drug_alerts_raw]

    # Step 4: Save Document Record
    web_file_path = file_path.as_posix()
    web_highlighted_path = Path(highlighted_path).as_posix() if highlighted_path else ""

    await db.execute(
        """
        INSERT INTO documents
        (id, encounter_id, patient_id, document_type, document_date, file_path, ocr_status, ocr_raw_text, ocr_lines, highlighted_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            document_id, encounter_id, linked_patient_id, document_type, document_date,
            web_file_path, ocr_status, raw_ocr_text, json.dumps(ocr_lines_data), web_highlighted_path
        )
    )

    # Save extracted medications as clinical_facts
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

    highlighted_url = ""
    if highlighted_path:
        highlighted_url = f"/static/evidence/{document_id}-boxed.jpg"
    else:
        # Fall back to the actual saved uploaded document (zero mockups!)
        highlighted_url = f"/static/uploads/{document_id}_{document.filename}"

    return DocumentUploadResponse(
        document_id=document_id,
        ocr_status=ocr_status,
        document_type=document_type,
        extracted_medications=extracted_meds,
        extracted_labs=extracted_labs,
        flagged_interactions=drug_alerts,
        flagged_labs=flagged_labs,
        highlighted_image_url=highlighted_url,
        raw_ocr_text=raw_ocr_text,
        overall_ocr_confidence=overall_conf
    )


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    encounter_id: str = Form(...),
    document: UploadFile = File(...),
    document_type: str = Form("prescription"),
    document_date: Optional[str] = Form(None),
    patient_id: Optional[str] = Form(None),
    db=Depends(get_db)
):
    """Upload a single document (prescription, lab report, or discharge summary)."""
    return await _process_single_document(
        encounter_id=encounter_id,
        document=document,
        document_type=document_type,
        document_date=document_date,
        patient_id=patient_id,
        db=db
    )


@router.post("/batch-upload", response_model=BatchDocumentUploadResponse)
async def batch_upload_documents(
    encounter_id: str = Form(...),
    document_type: str = Form("prescription"),
    document_date: Optional[str] = Form(None),
    patient_id: Optional[str] = Form(None),
    files: list[UploadFile] = File(...),
    db=Depends(get_db)
):
    """Batch upload multiple documents for a patient encounter."""
    processed_docs = []
    total_meds = 0
    total_labs = 0
    total_interactions = 0
    total_panic_labs = 0

    for f in files:
        doc_resp = await _process_single_document(
            encounter_id=encounter_id,
            document=f,
            document_type=document_type,
            document_date=document_date,
            patient_id=patient_id,
            db=db
        )
        processed_docs.append(doc_resp)
        total_meds += len(doc_resp.extracted_medications)
        total_labs += len(doc_resp.extracted_labs)
        total_interactions += len(doc_resp.flagged_interactions)
        total_panic_labs += sum(1 for lab in doc_resp.flagged_labs if lab.get("requires_urgent_escalation"))

    return BatchDocumentUploadResponse(
        success=True,
        total_uploaded=len(files),
        documents=processed_docs,
        extracted_medications_count=total_meds,
        extracted_labs_count=total_labs,
        flagged_interactions_count=total_interactions,
        panic_lab_alerts_count=total_panic_labs
    )


@router.get("/encounter/{encounter_id}/timeline")
async def get_document_timeline(encounter_id: str, db=Depends(get_db)):
    """Retrieve chronologically organized multi-document timeline for an encounter."""
    rows = await db.execute(
        "SELECT * FROM documents WHERE encounter_id = ? ORDER BY created_at DESC",
        (encounter_id,)
    )
    docs = [dict(r) for r in await rows.fetchall()]
    return {
        "encounter_id": encounter_id,
        "total_documents": len(docs),
        "timeline": [
            {
                "id": d["id"],
                "document_type": d.get("document_type") or "prescription",
                "document_date": d.get("document_date") or d["created_at"],
                "file_path": d["file_path"],
                "ocr_status": d["ocr_status"],
                "ocr_raw_text": d.get("ocr_raw_text") or "",
                "highlighted_path": d.get("highlighted_path") or "",
                "created_at": d["created_at"]
            }
            for d in docs
        ]
    }
