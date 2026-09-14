"""
MediKiosk — IVR & Exotel Telephony Pydantic Schemas
Defines request and response structures for incoming calls, speech turns, and location diagnostics.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ExotelIncomingCallRequest(BaseModel):
    """Payload sent by Exotel Webhook on incoming call."""
    CallSid: Optional[str] = Field(None, description="Unique Exotel Call ID")
    From: str = Field(..., description="Caller 10-digit mobile number")
    To: Optional[str] = Field(None, description="Dialed Virtual Number / DID")
    CallType: Optional[str] = Field("inbound", description="Call type")
    Direction: Optional[str] = Field("inbound", description="Call direction")
    language: Optional[str] = Field("hi", description="Preferred language (hi, en, ta, te, mr)")


class IVRSpeechTurnRequest(BaseModel):
    """Patient speech turn captured by Exotel / Voice recognition."""
    session_id: Optional[str] = Field(None, description="Active IVR call session ID")
    CallSid: Optional[str] = Field(None, description="Exotel Call ID alias")
    caller_phone: Optional[str] = Field(None, description="Caller mobile number")
    speech_text: Optional[str] = Field(None, description="Transcribed patient speech")
    SpeechResult: Optional[str] = Field(None, description="Exotel speech transcript alias")
    turn_index: Optional[int] = Field(0, description="Zero-indexed turn count")


class IVRSpeechTurnResponse(BaseModel):
    session_id: str
    patient_transcript: str
    next_question_text: Optional[str] = None
    is_completed: bool = False
    turn_index: int
    extracted_facts_count: int


class IVRCallResponse(BaseModel):
    """Response returned to Exotel / Caller client upon incoming call setup."""
    status: str
    session_id: str
    encounter_id: str
    token_number: str
    assigned_clinic: Dict[str, Any]
    waterfall_step: int
    resolution_type: str
    opening_prompt: str
    exotel_say: str


class IVREndCallResponse(BaseModel):
    """Response upon concluding the IVR call session."""
    encounter_id: str
    session_id: str
    token_number: str
    assigned_clinic: Dict[str, Any]
    total_facts_captured: int
    severity_badge: str
    sms_dispatched: bool
    sms_text: str


class LocationDiagnosticResponse(BaseModel):
    """Response for public testing endpoint /api/ivr/resolve-location."""
    caller_phone: str
    dialed_number: Optional[str] = None
    waterfall_step: int
    resolution_type: str
    confidence: float
    clinic: Dict[str, Any]
    patient_name: Optional[str] = None
    abha_id: Optional[str] = None
    rationale: str
