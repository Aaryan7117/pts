"""
MediKiosk — Encounter Schemas
Bootstrap, status tracking, and encounter lifecycle models.
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class LanguageOption(BaseModel):
    """Supported language entry."""
    code: str
    label: str


# --- Supported languages (constant) ---
SUPPORTED_LANGUAGES = [
    LanguageOption(code="en", label="English"),
    LanguageOption(code="hi", label="हिन्दी"),
    LanguageOption(code="ta", label="தமிழ்"),
    LanguageOption(code="te", label="తెలుగు"),
    LanguageOption(code="mr", label="मराठी"),
]


class EncounterBootstrapRequest(BaseModel):
    """Request to initialize a new patient encounter."""
    qr_token: Optional[str] = Field(default=None, description="QR token scanned from OPD waiting queue (e.g. TK-4819)")
    device_channel: Literal["kiosk", "android_byod", "ivr_phone"] = Field(
        default="kiosk",
        description="Which intake channel is initiating this encounter"
    )
    language: str = Field(default="hi", description="Preferred language code (en, hi, ta, te, mr)")


class EncounterBootstrapResponse(BaseModel):
    """Response after bootstrapping a new encounter."""
    encounter_id: str
    patient_id: str
    token_number: str
    status: str = "BOOTSTRAPPED"
    supported_languages: list[LanguageOption] = Field(default_factory=lambda: SUPPORTED_LANGUAGES)


class EncounterSummary(BaseModel):
    """Compact encounter summary for queue displays and doctor dashboard."""
    encounter_id: str
    token_number: str
    channel: str
    language: str
    status: str
    severity_badge: str
    department: str
    created_at: Optional[str] = None
    fact_count: int = 0
    has_red_flags: bool = False
    summary_text: Optional[str] = None


class EncounterStatusUpdate(BaseModel):
    """Request to update encounter status."""
    status: Literal["IN_PROGRESS", "COMPLETED", "DOCTOR_REVIEWED"]
