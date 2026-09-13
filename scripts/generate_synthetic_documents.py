"""
MediKiosk — Synthetic Document & Evidence Image Generator
Generates realistic prescription and lab report images with PIL:
  - Uploaded document saved in static/uploads/{doc_id}_{filename}
  - Evidence-highlighted image with bounding boxes in static/evidence/{doc_id}-boxed.jpg
  - Structured OCR line metadata with pixel coordinates
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int = 16, bold: bool = False):
    """Load default font or TrueType font if available."""
    try:
        # Try system fonts commonly found on Linux
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def generate_document_image(
    doc_def: dict,
    encounter_id: str,
    output_upload_dir: Path,
    output_evidence_dir: Path,
) -> dict:
    """
    Generate a realistic document image and an annotated evidence-highlighted version.

    Returns a dictionary matching the MediKiosk `documents` table row.
    """
    output_upload_dir.mkdir(parents=True, exist_ok=True)
    output_evidence_dir.mkdir(parents=True, exist_ok=True)

    doc_id = doc_def["id"]
    filename = doc_def["filename"]
    upload_file_path = output_upload_dir / f"{doc_id}_{filename}"
    evidence_file_path = output_evidence_dir / f"{doc_id}-boxed.jpg"

    # Canvas dimensions
    width, height = 760, 980
    bg_color = (252, 252, 250)  # Prescription paper off-white
    border_color = (200, 205, 215)
    text_dark = (30, 41, 59)
    text_muted = (100, 116, 139)
    header_bg = (241, 245, 249)

    # 1. Base Document Image
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Outer document border
    draw.rectangle([15, 15, width - 15, height - 15], outline=border_color, width=2)
    draw.rectangle([25, 25, width - 25, height - 25], outline=(226, 232, 240), width=1)

    # Header section
    draw.rectangle([25, 25, width - 25, 120], fill=header_bg)
    header_font = _get_font(20, bold=True)
    title_font = _get_font(13, bold=False)
    body_font = _get_font(14, bold=False)
    bold_body_font = _get_font(14, bold=True)
    meta_font = _get_font(12, bold=False)

    # Hospital emblem mark & title
    draw.rectangle([45, 45, 85, 85], fill=(37, 99, 235))
    draw.text((58, 48), "+", fill=(255, 255, 255), font=_get_font(30, bold=True))
    draw.text((105, 45), doc_def.get("header", "ALL INDIA INSTITUTE OF MEDICAL SCIENCES"), fill=(15, 23, 42), font=header_font)
    draw.text((105, 75), doc_def.get("title", "CLINICAL OUTPATIENT RECORD"), fill=text_muted, font=title_font)

    # Patient info bar
    draw.line([25, 120, width - 25, 120], fill=(203, 213, 225), width=2)
    draw.text((45, 135), f"Patient: {doc_def.get('patient_name', 'Patient')}", fill=text_dark, font=bold_body_font)
    draw.text((45, 158), doc_def.get("patient_info", "OPD General"), fill=text_muted, font=meta_font)
    draw.line([25, 185, width - 25, 185], fill=(226, 232, 240), width=1)

    # Document body text
    body_y = 205
    line_bboxes = []
    body_lines = doc_def.get("body_lines", [])

    for idx, line in enumerate(body_lines):
        # Draw line text
        is_subhead = line.startswith("Diagnosis:") or line.startswith("TEST") or line.startswith("Rx:") or line.startswith("Chikitsa")
        fnt = bold_body_font if is_subhead else body_font
        fill_col = (15, 23, 42) if is_subhead else (51, 65, 85)

        draw.text((45, body_y), line, fill=fill_col, font=fnt)

        # Record approximate bounding box for OCR traceability
        bbox = [40, body_y - 2, width - 60, body_y + 24]
        line_bboxes.append({
            "line_index": idx,
            "text": line,
            "bbox": bbox,
            "confidence": 0.96
        })
        body_y += 38

    # Doctor signature / footer area
    draw.line([25, height - 120, width - 25, height - 120], fill=(226, 232, 240), width=1)
    draw.text((45, height - 100), "Electronically Authenticated Clinical Document", fill=text_muted, font=meta_font)
    draw.text((45, height - 80), "ABHA Health Locker / NDHM Linked Record", fill=(59, 130, 246), font=meta_font)

    draw.text((width - 240, height - 105), "Dr. Verified & Signed", fill=text_dark, font=bold_body_font)
    draw.text((width - 240, height - 85), "Reg No: MCI-2024-91823", fill=text_muted, font=meta_font)

    # Save original uploaded image
    img.save(upload_file_path, "JPEG", quality=90)

    # 2. Evidence Boxed Image (highlight regions where clinical entities were extracted)
    evidence_img = img.copy()
    evidence_draw = ImageDraw.Draw(evidence_img)

    highlights = doc_def.get("highlights", [])
    for h in highlights:
        box = h["box"]  # [x1, y1, x2, y2]
        color_hex = h.get("color", "#3B82F6")

        # Parse hex color
        hex_clean = color_hex.lstrip("#")
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        highlight_color = (r, g, b)

        # Draw highlight border box
        evidence_draw.rectangle(box, outline=highlight_color, width=3)

        # Draw subtle label badge above box
        label_text = f"✔ OCR DETECTED: {h.get('text', '')[:35]}"
        label_y = max(10, box[1] - 18)
        evidence_draw.rectangle([box[0], label_y, box[0] + 320, label_y + 16], fill=highlight_color)
        evidence_draw.text((box[0] + 4, label_y + 1), label_text, fill=(255, 255, 255), font=_get_font(11, bold=True))

    evidence_img.save(evidence_file_path, "JPEG", quality=90)

    raw_text = "\n".join(body_lines)

    return {
        "id": doc_id,
        "encounter_id": encounter_id,
        "file_path": str(upload_file_path),
        "ocr_status": "SUCCESS",
        "ocr_raw_text": raw_text,
        "ocr_lines": json.dumps(line_bboxes),
        "highlighted_path": str(evidence_file_path)
    }


def generate_all_synthetic_documents(patients: list[dict], base_dir: Path) -> list[dict]:
    """Generate all document images for synthetic patients and return DB records."""
    upload_dir = base_dir / "static" / "uploads"
    evidence_dir = base_dir / "static" / "evidence"

    records = []
    for patient_case in patients:
        encounter_id = patient_case["encounter"]["id"]
        for doc_def in patient_case.get("documents", []):
            rec = generate_document_image(
                doc_def=doc_def,
                encounter_id=encounter_id,
                output_upload_dir=upload_dir,
                output_evidence_dir=evidence_dir
            )
            records.append(rec)

    return records
