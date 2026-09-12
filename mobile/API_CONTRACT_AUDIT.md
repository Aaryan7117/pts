# MediKiosk — API Contract Audit & Frozen Interfaces
**Document Status:** FROZEN CONTRACT SPECIFICATION (Prompt 0 Deliverable)  
**Target Backend:** FastAPI 3.0.0 (`http://localhost:8000` or LAN IP:8000)  
**Target Client:** Flutter Android (Moto G54 5G + Kiosk Tablet)  
**Last Updated:** September 2026  

---

## 1. Overview

This document freezes the technical contracts between the MediKiosk Flutter mobile/kiosk application and the Python FastAPI backend. **No APIs have been invented.** All schemas documented here map directly to `app/schemas/` and `app/api/`.

---

## 2. API Endpoints Specification

### 2.1 System Health
- **Endpoint:** `GET /api/health`
- **Auth:** Public
- **Description:** Verifies backend liveness and AI model availability.
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "MediKiosk Backend",
  "version": "3.0.0",
  "sih_problem_id": "SIH26047",
  "network": "ONLINE",
  "llm_providers": {
    "cloud": ["gemini-1.5-flash", "groq-llama-3.1-70b"],
    "edge": ["ollama-qwen2.5:7b"],
    "total": 3
  },
  "endpoints": {
    "swagger": "http://0.0.0.0:8000/docs",
    "encounters": "/api/encounters/bootstrap",
    "call_start": "/api/call/session/start",
    "audio_turn": "/api/call/audio-turn",
    "call_end": "/api/call/session/end",
    "document_upload": "/api/documents/upload",
    "queue_status": "/api/queue/status/{token}",
    "doctor_auth": "/api/doctor/auth",
    "doctor_queue": "/api/doctor/queue",
    "doctor_patient": "/api/doctor/patient/{encounter_id}"
  }
}
```

---

### 2.2 Encounter Bootstrap & Lifecycle
- **Endpoint:** `POST /api/encounters/bootstrap`
- **Auth:** Public
- **Description:** Initiates a new patient session, assigns an OPD queue token, and registers patient language.
- **Request Body (`application/json`):**
```json
{
  "qr_token": "TK-4819", // Optional (e.g. scanned from paper slip). null if new
  "device_channel": "android_byod", // "kiosk" | "android_byod" | "ivr_phone"
  "language": "hi" // "en" | "hi" | "ta" | "te" | "mr"
}
```
- **Response `200 OK` (`EncounterBootstrapResponse`):**
```json
{
  "encounter_id": "enc-9c8f2a1b",
  "patient_id": "pat-3d4e5f6a",
  "token_number": "A-104",
  "status": "BOOTSTRAPPED",
  "supported_languages": [
    { "code": "en", "label": "English" },
    { "code": "hi", "label": "हिन्दी" },
    { "code": "ta", "label": "தமிழ்" },
    { "code": "te", "label": "తెలుగు" },
    { "code": "mr", "label": "मराठी" }
  ]
}
```

- **Endpoint:** `GET /api/encounters/{encounter_id}`
- **Auth:** Public
- **Response `200 OK` (`EncounterSummary`):**
```json
{
  "encounter_id": "enc-9c8f2a1b",
  "token_number": "A-104",
  "channel": "android_byod",
  "language": "hi",
  "status": "IN_PROGRESS",
  "severity_badge": "GREEN", // "GREEN" | "YELLOW" | "RED"
  "department": "General Medicine",
  "created_at": "2026-09-12T13:30:00",
  "fact_count": 4,
  "has_red_flags": false,
  "summary_text": "34-year-old presenting with mild fever for 2 days."
}
```

---

### 2.3 Conversational Voice Call Intake (`/api/call/*`)

- **Endpoint:** `POST /api/call/session/start`
- **Auth:** Public
- **Description:** Starts a conversational interview session, initializes the SOCRATES state machine, and returns opening prompt text + base64 audio.
- **Request Body (`application/json`):**
```json
{
  "encounter_id": "enc-9c8f2a1b",
  "language": "hi"
}
```
- **Response `200 OK` (`CallSessionStartResponse`):**
```json
{
  "session_id": "call-sess-8f7a2b1c",
  "status": "CALL_ACTIVE",
  "opening_text": "नमस्ते, मैं मेडीकिओस्क हूँ। आज आपको क्या परेशानी महसूस हो रही है?",
  "opening_audio_base64": "UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA..." // or null if TTS offline
}
```

- **Endpoint:** `POST /api/call/audio-turn`
- **Auth:** Public
- **Description:** Sends one audio turn from the patient's microphone. Transcribes via ASR, extracts clinical facts, validates against red-flag rules, and returns next question + audio.
- **Request Form-Data (`multipart/form-data`):**
  - `session_id`: `"call-sess-8f7a2b1c"`
  - `audio_file`: `patient_speech.wav` (WAV/OGG/AAC audio payload)
- **Response `200 OK` (`AudioTurnResponse`):**
```json
{
  "session_id": "call-sess-8f7a2b1c",
  "turn_index": 1,
  "patient_transcript": "मुझे दो दिन से तेज सिरदर्द और हल्का बुखार है",
  "extracted_facts": [
    {
      "category": "chief_complaint",
      "field": "headache",
      "concept": "Severe Headache",
      "concept_code": "SNOMED:25064002",
      "duration": "2 days",
      "confidence": 0.94,
      "provenance": "EMBEDDING"
    },
    {
      "category": "symptom",
      "field": "fever",
      "concept": "Mild Pyrexia",
      "concept_code": "SNOMED:386661006",
      "duration": "2 days",
      "confidence": 0.91,
      "provenance": "EMBEDDING"
    }
  ],
  "next_question_text": "क्या आपको सिरदर्द के साथ चक्कर या उल्टी जैसा भी लग रहा है?",
  "next_question_audio_base64": "UklGRi4AAABXQVZFZm10...",
  "is_completed": false
}
```

- **Endpoint:** `POST /api/call/session/end`
- **Auth:** Public
- **Description:** Completes interview intake and locks clinical facts.
- **Request Body (`application/json`):**
```json
{
  "session_id": "call-sess-8f7a2b1c"
}
```
- **Response `200 OK` (`CallSessionEndResponse`):**
```json
{
  "encounter_id": "enc-9c8f2a1b",
  "status": "COMPLETED",
  "assigned_token": "A-104",
  "department": "General Medicine",
  "total_facts_captured": 6,
  "red_flags_detected": false,
  "severity_badge": "GREEN"
}
```

---

### 2.4 Document Capture & OCR Pipeline (`/api/documents/*`)

- **Endpoint:** `POST /api/documents/upload`
- **Auth:** Public
- **Description:** Uploads a scanned prescription photo or lab report. Runs RapidOCR line-detection, performs medication extraction via LLM, and highlights bounding polygons.
- **Request Form-Data (`multipart/form-data`):**
  - `encounter_id`: `"enc-9c8f2a1b"`
  - `document`: `prescription.jpg` (Image binary)
- **Response `200 OK` (`DocumentUploadResponse`):**
```json
{
  "document_id": "doc-5a6b7c8d",
  "ocr_status": "SUCCESS", // "SUCCESS" | "LOW_CONFIDENCE" | "FAILED"
  "extracted_medications": [
    {
      "name": "Paracetamol",
      "dose": "650mg",
      "frequency": "1-0-1",
      "source_lines": [2, 3],
      "box_2d": [150, 45, 185, 320],
      "confidence": 0.95
    },
    {
      "name": "Cetirizine",
      "dose": "10mg",
      "frequency": "0-0-1",
      "source_lines": [5],
      "box_2d": [220, 50, 255, 290],
      "confidence": 0.92
    }
  ],
  "flagged_interactions": [],
  "highlighted_image_url": "/static/evidence/doc-5a6b7c8d-boxed.jpg",
  "raw_ocr_text": "Rx\nParacetamol 650mg BD\nCetirizine 10mg HS\nDr. S. Sharma",
  "overall_ocr_confidence": 0.93
}
```

---

### 2.5 Live OPD Queue Tracking (`/api/queue/*`)

- **Endpoint:** `GET /api/queue/status/{token}`
- **Auth:** Public
- **Description:** Real-time queue tracker for the patient ticket.
- **Response `200 OK` (`QueueStatusResponse`):**
```json
{
  "token": "A-104",
  "department": "General Medicine",
  "status": "WAITING", // "WAITING" | "CALLED" | "IN_CONSULTATION" | "COMPLETED"
  "patients_ahead": 3,
  "estimated_wait_minutes": 9,
  "doctor_room": "Room 102 (Dr. Verma)"
}
```

- **Endpoint:** `GET /api/queue/all`
- **Auth:** Public
- **Description:** Full OPD queue tracker overview.

---

### 2.6 Doctor Dashboard & Clinical Review (`/api/doctor/*`)

- **Endpoint:** `POST /api/doctor/auth`
- **Auth:** PIN Gated (Default PIN: `1234`)
- **Request Body:** `{ "pin": "1234" }`
- **Response `200 OK`:** `{ "authenticated": true, "message": "Authentication successful" }`

- **Endpoint:** `GET /api/doctor/queue`
- **Auth:** Doctor Authenticated
- **Response `200 OK` (`DoctorQueueResponse`):**
```json
{
  "queue": [
    {
      "encounter_id": "enc-9c8f2a1b",
      "token_number": "A-104",
      "severity_badge": "GREEN",
      "summary_30_words": "34-year-old presenting with mild fever for 2 days. Currently taking Paracetamol 650mg. No red flags.",
      "channel": "android_byod",
      "fact_count": 6,
      "has_medication_conflict": false,
      "has_red_flags": false,
      "created_at": "2026-09-12T13:30:00"
    }
  ],
  "total_waiting": 1
}
```

- **Endpoint:** `GET /api/doctor/patient/{encounter_id}`
- **Auth:** Doctor Authenticated
- **Response `200 OK` (`PatientDetailView`):**
  - Complete structured clinical breakdown including:
    - `encounter`: Full metadata
    - `clinical_facts`: All immutable facts with source reference links
    - `drug_interaction_alerts`: Contraindications detected
    - `lab_result_alerts`: High/low flag alerts
    - `clinical_gap_alerts`: Missing history prompts
    - `ayush_intake`: Complete Dashavidha Pariksha records
    - `documents`: Uploaded images with highlighted polygon overlays

---

## 3. Provenance & Confidence Arithmetic

To prevent hallucination, the client renders provenance tags based on the backend model:

```text
Confidence Tier Formula:
Tier Score × Input Quality × Completeness

Tiers:
≥ 0.85  → High (Locked, no further patient verification required)
0.55–0.85 → Medium (Requires explain-back patient confirmation card)
< 0.55  → Low Refuse (Flagged with warning badge for physician attention)
```
