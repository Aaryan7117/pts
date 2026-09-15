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
    department: Optional[str] = Field(default=None, description="Care stream / Department (e.g. AYUSH (Ayurveda))")


class CallSessionStartResponse(BaseModel):
    """Response after starting a call session — includes opening question audio."""
    session_id: str
    status: str = "CALL_ACTIVE"
    opening_text: str = Field(description="Opening question text in the patient's language")
    welcome_text: Optional[str] = Field(default=None, description="Alias for opening_text")
    opening_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded WAV/OGG audio of the opening question"
    )
    opening_audio_url: Optional[str] = Field(
        default=None,
        description="Direct streaming URL to the opening question audio (B3)"
    )
    audio_url: Optional[str] = Field(
        default=None,
        description="Alias for opening_audio_url"
    )

    def model_post_init(self, __context):
        if not self.welcome_text:
            self.welcome_text = self.opening_text
        if not self.audio_url and self.opening_audio_url:
            self.audio_url = self.opening_audio_url


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
    transcript: Optional[str] = Field(default=None, description="Alias for patient_transcript")
    extracted_facts: list[ExtractedFactSummary] = Field(default_factory=list)
    facts_extracted: list[ExtractedFactSummary] = Field(default_factory=list)
    next_question_text: Optional[str] = Field(
        default=None,
        description="Next adaptive follow-up question text"
    )
    assistant_reply: Optional[str] = Field(
        default=None,
        description="Alias for next_question_text"
    )
    next_question: Optional[str] = Field(
        default=None,
        description="Alias for next_question_text"
    )
    next_question_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded audio of the next question"
    )
    next_question_audio_url: Optional[str] = Field(
        default=None,
        description="Streaming audio URL of the next question (B3)"
    )
    suggested_options: list[dict] = Field(
        default_factory=list,
        description="Context-based suggested choice options for the follow-up question"
    )
    is_completed: bool = Field(
        default=False,
        description="True if the interview state machine has completed all sections"
    )
    is_complete: bool = Field(
        default=False,
        description="Alias for is_completed"
    )

    def model_post_init(self, __context):
        if not self.transcript:
            self.transcript = self.patient_transcript
        if not self.assistant_reply and self.next_question_text:
            self.assistant_reply = self.next_question_text
        if not self.next_question and self.next_question_text:
            self.next_question = self.next_question_text
        if not self.facts_extracted and self.extracted_facts:
            self.facts_extracted = self.extracted_facts
        self.is_complete = self.is_completed


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
