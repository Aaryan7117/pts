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
    patient_id: Optional[str] = Field(default=None, description="Patient identifier (e.g. pat-001 or mobile number)")
    channel: Optional[str] = Field(default=None, description="Access channel (kiosk, android_byod, mobile_byod, ivr_phone, web_kiosk)")
    device_channel: Optional[str] = Field(default=None, description="Alias for channel")
    language: str = Field(default="hi", description="Preferred language code (en, hi, ta, te, mr)")

    def get_channel(self) -> str:
        return self.channel or self.device_channel or "kiosk"


class EncounterBootstrapResponse(BaseModel):
    """Response after bootstrapping a new encounter."""
    encounter_id: str
    patient_id: str
    token_number: str
    bearer_token: str = Field(description="Encounter-scoped bearer token (30-minute TTL for DPDP compliance)")
    status: str = "BOOTSTRAPPED"
    supported_languages: list[LanguageOption] = Field(default_factory=lambda: SUPPORTED_LANGUAGES)


class ConsentRequest(BaseModel):
    """Patient informed consent payload for DPDP compliance."""
    granted_at: Optional[str] = Field(default=None, description="ISO timestamp of consent")
    language: str = Field(default="hi", description="Language in which consent was presented")
    consent_version: str = Field(default="1.0", description="Version of consent policy")
    channel: Optional[str] = Field(default="mobile_byod", description="Channel through which consent was given")


class ConsentResponse(BaseModel):
    """Confirmation of recorded consent."""
    encounter_id: str
    status: str = "CONSENT_RECORDED"
    consent_version: str
    recorded_at: str


class EncounterSummary(BaseModel):
    """Compact encounter summary for queue displays and doctor dashboard."""
    encounter_id: str
    id: Optional[str] = None
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
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    abha_id: Optional[str] = None

    def model_post_init(self, __context):
        if not self.id and self.encounter_id:
            self.id = self.encounter_id
        elif not self.encounter_id and self.id:
            self.encounter_id = self.id


class EncounterFullStateResponse(BaseModel):
    """Full encounter rehydration state for mobile session resumption (B6)."""
    encounter_id: str
    id: Optional[str] = None
    patient_id: Optional[str] = None
    token_number: str
    channel: str
    language: str
    status: str
    severity_badge: str
    department: str
    created_at: Optional[str] = None
    fact_count: int = 0
    has_red_flags: bool = False
    clinical_facts: list[dict] = Field(default_factory=list)
    documents: list[dict] = Field(default_factory=list)
    active_call_session: Optional[dict] = None
    ayush_intake: Optional[dict] = None

    def model_post_init(self, __context):
        if not self.id and self.encounter_id:
            self.id = self.encounter_id
        elif not self.encounter_id and self.id:
            self.encounter_id = self.id
    queue_position: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None


class EncounterStatusUpdate(BaseModel):
    """Request to update encounter status."""
    status: Literal["BOOTSTRAPPED", "IN_PROGRESS", "COMPLETED", "DOCTOR_REVIEWED"]


class EncounterLanguageUpdate(BaseModel):
    """Request to update encounter preferred language."""
    language: Literal["en", "hi", "ta", "te", "mr"]

