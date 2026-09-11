"""
MediKiosk — Doctor Dashboard Schemas
PIN-gated doctor interface models for queue intelligence and evidence drilldown.
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.clinical_fact import ClinicalFact, DrugInteractionAlert, LabResultAlert, ClinicalGapAlert
from app.schemas.encounter import EncounterSummary


class DoctorAuthRequest(BaseModel):
    """Doctor PIN authentication request."""
    pin: str = Field(description="4-digit doctor PIN")


class DoctorAuthResponse(BaseModel):
    """Doctor authentication response."""
    authenticated: bool
    message: str


class PatientQueueEntry(BaseModel):
    """Single patient entry in the doctor's waiting queue with triage info."""
    encounter_id: str
    token_number: str
    severity_badge: str = Field(description="GREEN | YELLOW | RED")
    summary_30_words: str = Field(description="Changes-first 30-word triage summary")
    channel: str
    fact_count: int = 0
    has_medication_conflict: bool = False
    has_red_flags: bool = False
    created_at: Optional[str] = None


class DoctorQueueResponse(BaseModel):
    """Full waiting queue for the doctor dashboard."""
    queue: list[PatientQueueEntry] = Field(default_factory=list)
    total_waiting: int = 0


class PatientDetailView(BaseModel):
    """Complete patient detail view for the doctor — facts, alerts, evidence."""
    encounter: EncounterSummary
    clinical_facts: list[ClinicalFact] = Field(default_factory=list)
    drug_interaction_alerts: list[DrugInteractionAlert] = Field(default_factory=list)
    lab_result_alerts: list[LabResultAlert] = Field(default_factory=list)
    clinical_gap_alerts: list[ClinicalGapAlert] = Field(default_factory=list)
    ayush_intake: Optional[dict] = None
    medication_timeline: Optional[list[dict]] = None
    documents: list[dict] = Field(default_factory=list)
