"""
MediKiosk — Call Session Schemas
Conversational voice call intake DTOs for the mobile app.
Ref: MediKiosk_Android_Two_Developer_Execution_Plan.md Section 3
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.schemas.clinical_fact import ClinicalFact


class CallSessionStartRequest(BaseModel):
    """Start a new conversational voice call session."""
    encounter_id: str
    language: str = Field(default="hi", description="Language code for the call (en, hi, ta, te, mr)")


class CallSessionStartResponse(BaseModel):
    """Response after starting a call session — includes opening question audio."""
    session_id: str
    status: str = "CALL_ACTIVE"
    opening_text: str = Field(description="Opening question text in the patient's language")
    opening_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded WAV/OGG audio of the opening question (via Sarvam Bulbul V3 / IndicF5)"
    )


class ExtractedFactSummary(BaseModel):
    """Compact fact summary returned during each call audio turn."""
    category: str
    field: str
    concept: str
    concept_code: Optional[str] = None
    duration: Optional[str] = None
    confidence: float
    provenance: str


class AudioTurnResponse(BaseModel):
    """Response for each audio turn in the conversational call loop."""
    session_id: str
    turn_index: int
    patient_transcript: str = Field(description="ASR transcription of the patient's speech")
    extracted_facts: list[ExtractedFactSummary] = Field(default_factory=list)
    next_question_text: Optional[str] = Field(
        default=None,
        description="Next adaptive follow-up question text"
    )
    next_question_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded audio of the next question"
    )
    is_completed: bool = Field(
        default=False,
        description="True if the interview state machine has completed all sections"
    )


class CallSessionEndRequest(BaseModel):
    """End a voice call session and lock the intake."""
    session_id: str


class CallSessionEndResponse(BaseModel):
    """Response after ending a call session — patient enters the queue."""
    encounter_id: str
    status: str = "COMPLETED"
    assigned_token: str
    department: str = "General Medicine"
    total_facts_captured: int
    red_flags_detected: bool = False
    severity_badge: str = "GREEN"
