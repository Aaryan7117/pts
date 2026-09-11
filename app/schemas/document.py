"""
MediKiosk — Document Upload Schemas
Prescription scan, OCR extraction, and evidence-boxed image response.
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.clinical_fact import DrugInteractionAlert


class ExtractedMedication(BaseModel):
    """Single medication extracted from a scanned prescription."""
    name: str = Field(description="Medication name")
    dose: Optional[str] = Field(default=None, description="Dosage (e.g. 500mg)")
    frequency: Optional[str] = Field(default=None, description="e.g. 1-0-1 or twice daily")
    source_lines: list[int] = Field(min_length=1, description="Mandatory line citations from OCR output")
    confidence: float = Field(ge=0.0, le=1.0)


class DocumentUploadResponse(BaseModel):
    """Response after uploading and processing a prescription/lab document."""
    document_id: str
    ocr_status: str = Field(description="SUCCESS | LOW_CONFIDENCE | FAILED")
    extracted_medications: list[ExtractedMedication] = Field(default_factory=list)
    flagged_interactions: list[DrugInteractionAlert] = Field(default_factory=list)
    highlighted_image_url: Optional[str] = Field(
        default=None,
        description="URL to the evidence-boxed prescription image with line highlights"
    )
    raw_ocr_text: Optional[str] = None
    overall_ocr_confidence: float = 0.0


class OCRLine(BaseModel):
    """Individual OCR-detected text line with bounding polygon."""
    line_index: int
    text: str
    bbox: list[int] = Field(description="[x1, y1, x2, y2] bounding box coordinates")
    confidence: float
