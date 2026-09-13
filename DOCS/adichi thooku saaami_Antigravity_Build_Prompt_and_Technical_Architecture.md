# MediKiosk — Master Antigravity Build Prompt + Technical Architecture + Prototype Execution Plan

**Purpose:** Give this entire file to a coding agent (Antigravity or equivalent) as the master implementation instruction for the MediKiosk project.

**Important:** This prompt is designed to produce a strong SIH prototype, not a production-ready clinical system. The agent must never pretend that a mock ABHA/HIS connector is a real government integration.

---

# PART A — MASTER BUILD PROMPT

## ROLE

You are the lead full-stack engineer, AI integration engineer, product architect, security engineer, and test engineer responsible for implementing the **MediKiosk — AI Clinical Intake Platform**.

You must first inspect the existing repository and preserve working code. Do not blindly rewrite the application.

The target project may contain:

- `backend/` or `back-arya/`
- `app/`
- `mobile/`
- Flutter frontend
- FastAPI backend
- existing authentication
- existing UI
- existing database models

### First task

1. Inspect the repository tree.
2. Identify the frontend, backend, database, environment configuration, existing API routes, models, screens, and current integration points.
3. Produce a short `IMPLEMENTATION_AUDIT.md` before making major changes.
4. Reuse existing architecture where it is sound.
5. Add new modules incrementally.
6. Do not destroy existing working functionality.

---

# PART B — PRODUCT GOAL

Implement MediKiosk as a **first-mile clinical intake system**.

The primary workflow is:

```text
Patient
 ↓
Identify / Login
 ↓
Language
 ↓
Consent
 ↓
Voice + Touch Clinical Intake
 ↓
Adaptive Follow-up Questions
 ↓
Red-Flag Safety Rules
 ↓
Document Scan / Upload
 ↓
OCR + Medical Entity Extraction
 ↓
Chronological Patient Timeline
 ↓
Structured Clinical Summary
 ↓
Doctor Dashboard
 ↓
Doctor Edit / Confirm / Reject
 ↓
FHIR-ready / HIS-ready Integration Adapter
 ↓
ABDM-ready Linkage Adapter
```

Secondary workflow:

```text
Patient Basic Phone
 ↓
IVR Call
 ↓
Language
 ↓
Identity / Consent
 ↓
Voice History
 ↓
STT
 ↓
Same Clinical Data Model
 ↓
Same Red-Flag Engine
 ↓
Same Summary
 ↓
Same Doctor Portal
```

The two channels MUST share the same backend schema.

---

# PART C — NON-NEGOTIABLE SAFETY RULES

1. Do not implement autonomous diagnosis.
2. Do not implement autonomous prescribing.
3. Do not claim an AI result is medically authoritative.
4. Red-flag escalation must use deterministic rules for prototype decisions.
5. LLM output must be schema-validated.
6. Every generated clinical field should carry a source and confidence where possible.
7. Doctor review is mandatory before clinical record finalization.
8. Use synthetic data by default.
9. Never print health data or secrets in logs.
10. Never hard-code API keys.
11. Do not treat Aadhaar as the medical record primary key.
12. Do not fake real ABHA issuance. Build a mock/adapter for the SIH demo.
13. Do not claim full ABDM certification without validation against the actual sandbox/profile requirements.
14. Make production integrations configurable and isolated behind adapters.

---

# PART D — USER ROLES

## Role 1 — Patient

Can:

- register or identify themselves,
- select language,
- give consent,
- answer questions by voice,
- answer by touch,
- upload/scan documents,
- review the captured summary,
- see session completion,
- receive a local-language confirmation.

## Role 2 — Doctor

Can:

- log in,
- view the patient queue,
- see red-flag status,
- read structured history,
- view document timeline,
- inspect source evidence,
- edit AI-generated summary,
- confirm/reject sections,
- add clinical notes,
- complete the encounter.

## Role 3 — Triage/Staff

Can:

- see high-priority alerts,
- open the relevant patient encounter,
- mark alert acknowledged,
- route patient to appropriate queue.

## Role 4 — Admin

Can:

- create departments,
- manage doctors,
- manage clinical profiles,
- configure languages,
- configure question trees,
- inspect audit events.

---

# PART E — FRONTEND REQUIREMENTS

## Patient UI

Create these screens:

1. Splash
2. Welcome
3. Language Selection
4. Consent
5. Identity / Patient Lookup
6. Patient Details
7. Clinical Intake Home
8. Voice Interaction
9. Touch Question
10. Red-Flag Alert
11. Document Upload / Camera
12. OCR Processing
13. Extracted Data Review
14. Medical Timeline
15. Structured Summary Review
16. Confirmation
17. Session Completed

### UI principles

- Large text.
- Large touch targets.
- High contrast.
- Minimal text per screen.
- Audio prompt button.
- Voice recording state.
- Clear progress indicator.
- Do not overwhelm the patient with medical jargon.
- Provide Tamil/Hindi/English demo translations.
- Avoid long forms.
- Keep the patient on one task at a time.

---

# PART F — DOCTOR UI

Create:

1. Login
2. Dashboard
3. Patient Queue
4. Encounter Detail
5. Clinical Summary
6. Document Timeline
7. Document Detail
8. Evidence/Source Traceability panel
9. Red-Flag alert panel
10. Doctor Edit/Confirm page
11. Finalized encounter page

### Doctor dashboard example

```text
PATIENT QUEUE
--------------------------------------------------
# | Patient | Age | Chief Complaint | Priority
--------------------------------------------------
1 | Lakshmi | 58  | Chest pain      | HIGH
2 | Arun    | 42  | Fever           | NORMAL
3 | Meena   | 33  | Back pain       | NORMAL
```

---

# PART G — IVR UI / BACKEND FLOW

Do not create a separate clinical backend for IVR.

Implement an interface:

```python
class TelephonyProvider:
    async def start_call(...): ...
    async def get_input(...): ...
    async def end_call(...): ...
```

Create a `MockTelephonyProvider` first.

Production providers can later be plugged in through environment variables.

IVR steps:

```text
Call
 ↓
Language selection
 ↓
Identity verification
 ↓
Consent
 ↓
Chief complaint
 ↓
Adaptive questions
 ↓
Confirm captured information
 ↓
Submit encounter
 ↓
Doctor queue
```

For the SIH demo, simulate phone interaction through a browser/call simulator if real telephony access is not yet available.

---

# PART H — BACKEND MODULES

FastAPI modules:

```text
app/
├── main.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── db.py
├── auth/
├── patients/
├── doctors/
├── encounters/
├── conversations/
├── questions/
├── documents/
├── ocr/
├── extraction/
├── summarization/
├── triage/
├── consent/
├── fhir/
├── abdm/
├── ivr/
├── audit/
└── health/
```

Every service must have:

- schema
- route
- service layer
- repository/data layer where appropriate
- validation
- tests

---

# PART I — DATABASE SCHEMA

Use PostgreSQL.

Required tables:

```text
patients
patient_identifiers
consents
encounters
clinical_questions
conversation_sessions
conversation_turns
history_answers
documents
document_pages
document_extractions
clinical_entities
clinical_timelines
clinical_summaries
triage_alerts
doctors
departments
hospital_users
audit_events
```

### `patients`

```text
id UUID PK
full_name
first_name
last_name
dob
age
sex
mobile
preferred_language
internal_patient_id
abha_id nullable
hospital_mrn nullable
created_at
updated_at
```

### `encounters`

```text
id UUID PK
patient_id FK
hospital_id
department_id
specialty
status
priority
started_at
completed_at
```

### `conversation_turns`

```text
id UUID PK
session_id FK
turn_index
speaker
language
audio_uri nullable
transcript
normalized_text
question_id nullable
created_at
```

### `history_answers`

```text
id UUID PK
encounter_id
section
question_id
question_text
answer_raw
answer_normalized
answer_type
source
source_reference
confidence
clinician_verified
```

### `documents`

```text
id UUID PK
patient_id
encounter_id
file_uri
file_name
document_type
capture_source
document_date nullable
ocr_status
extraction_status
created_at
```

### `document_extractions`

```text
id UUID PK
document_id
entity_type
entity_value
normalized_value
confidence
page_number
bounding_box_json
source_text
```

### `clinical_summaries`

```text
id UUID PK
encounter_id
summary_json
summary_text
model_name
model_version
status
clinician_verified
created_at
verified_at
```

### `triage_alerts`

```text
id UUID PK
encounter_id
rule_code
severity
reason
status
created_at
acknowledged_by
acknowledged_at
```

### `consents`

```text
id UUID PK
patient_id
encounter_id
purpose
scope
status
consent_method
given_at
withdrawn_at
```

### `audit_events`

```text
id UUID PK
actor_id
actor_role
action
resource_type
resource_id
metadata_json
created_at
```

---

# PART J — CLINICAL QUESTION ENGINE

Do not let the LLM invent an unrestricted diagnostic interview.

Create a structured question tree.

Example configuration:

```json
{
  "profile": "general_medicine",
  "chief_complaints": {
    "chest_pain": [
      "onset",
      "duration",
      "character",
      "location",
      "radiation",
      "aggravating_factors",
      "relieving_factors",
      "associated_breathlessness",
      "syncope",
      "sweating"
    ]
  }
}
```

The LLM may:

- normalize patient language,
- choose among predefined question nodes,
- ask a clarification question,
- translate the question.

The LLM may NOT:

- invent arbitrary clinical branches,
- declare a diagnosis,
- suppress safety questions,
- alter safety-rule thresholds.

---

# PART K — SPEECH PIPELINE

Recommended prototype provider: Sarvam Speech-to-Text.

Current docs expose speech-to-text APIs for Indian languages, including Tamil, Hindi, Telugu and other Indian languages, with code-mixing support.

Reference:
https://docs.sarvam.ai/api-reference/speech-to-text/transcribe

### Architecture

```text
Microphone
   ↓
Audio chunk
   ↓
Noise handling / level check
   ↓
STT Provider
   ↓
Transcript
   ↓
Language normalization
   ↓
Clinical structuring
```

### Interface

```python
class STTProvider(Protocol):
    async def transcribe(
        self,
        audio_bytes: bytes,
        language_code: str | None = None,
        mode: str = "transcribe",
    ) -> STTResult:
        ...
```

### `STTResult`

```json
{
  "text": "எனக்கு மூன்று நாட்களாக மார்பு வலி உள்ளது",
  "language": "ta-IN",
  "confidence": 0.91,
  "provider": "sarvam"
}
```

### TTS

Use a TTS provider such as Sarvam Bulbul for local-language prompts.

---

# PART L — DOCUMENT PIPELINE

```text
Camera / File
      ↓
Image preprocessing
      ↓
Deskew / rotate / crop
      ↓
OCR / Document AI
      ↓
Layout analysis
      ↓
Text extraction
      ↓
Medical entity extraction
      ↓
Normalization
      ↓
Date extraction
      ↓
Timeline insertion
      ↓
Doctor review
```

Recommended prototype choices:

- Sarvam Vision for Indian-language document understanding, or
- PaddleOCR / PP-Structure for local/open deployment.

Reference:
https://www.paddleocr.ai/main/en/version2.x/ppstructure/overview.html

Do not use plain Tesseract as the only handwritten-prescription solution.

---

# PART M — MEDICAL ENTITY SCHEMA

The extractor should return something like:

```json
{
  "document_type": "prescription",
  "document_date": "2026-08-21",
  "diagnoses": [
    {
      "text": "Type 2 diabetes mellitus",
      "normalized": "diabetes mellitus type 2",
      "confidence": 0.95
    }
  ],
  "medications": [
    {
      "name": "Metformin",
      "dose": "500 mg",
      "frequency": "BID",
      "duration": "30 days",
      "confidence": 0.92
    }
  ],
  "investigations": [],
  "procedures": []
}
```

The extraction service MUST return machine-readable JSON.

No downstream module should parse free-form LLM prose.

---

# PART N — LAB VALUE EXTRACTION

For lab reports, extract:

```text
Test name
Value
Unit
Reference range
Abnormal flag
Date
Source document
Confidence
```

Example:

```json
{
  "test": "HbA1c",
  "value": 7.8,
  "unit": "%",
  "reference_range": "< 5.7",
  "abnormal": true,
  "source": "DOC-004",
  "confidence": 0.97
}
```

The system can highlight the value for physician attention.

Do not convert an abnormal result into a diagnosis automatically.

---

# PART O — LLM SUMMARY GENERATION

Use a structured-output-capable model.

A prototype option is Gemini 2.5 Flash because Google's current documentation lists multimodal input and structured outputs.

Reference:
https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash

Alternative: Sarvam-105B for Indic-language reasoning where available.

### LLM task

Input:

```text
patient history JSON
+
document entities JSON
+
timeline JSON
+
questionnaire answers JSON
```

Output JSON:

```json
{
  "chief_complaint": "",
  "hpi": "",
  "past_medical_history": [],
  "past_surgical_history": [],
  "medications": [],
  "allergies": [],
  "family_history": [],
  "personal_history": [],
  "review_of_systems": [],
  "prior_investigations": [],
  "red_flags": [],
  "unknown_or_unverified": [],
  "source_references": []
}
```

### Summary generation prompt

Use a system instruction equivalent to:

```text
You are a clinical information structuring assistant.
You do not diagnose, prescribe, or make autonomous medical decisions.
Transform only the supplied patient statements, structured answers, and document-extraction evidence into a concise clinician-reviewable history.
Never invent missing facts.
If information is missing, return null or "not provided".
Preserve uncertainty.
Keep source references for every material claim.
Clearly separate patient-reported information from document-derived information.
Return strict JSON matching the schema.
```

---

# PART P — RED-FLAG ENGINE

Build this as a deterministic rules service.

Example:

```python
RED_FLAG_RULES = [
    {
        "code": "CHEST_PAIN_DYSPNEA",
        "when": lambda h: h.chest_pain and h.breathlessness_severe,
        "severity": "HIGH",
    },
    {
        "code": "STROKE_LIKE",
        "when": lambda h: h.face_droop or h.arm_weakness or h.speech_difficulty,
        "severity": "HIGH",
    },
]
```

The response should be:

```json
{
  "priority": "HIGH",
  "rule_code": "CHEST_PAIN_DYSPNEA",
  "message": "Potential emergency symptoms detected. Please alert triage staff immediately.",
  "requires_staff_action": true
}
```

The system should NEVER say:

> "You are having a heart attack."

Instead:

> "Potential emergency symptoms detected. Please alert triage staff immediately."

---

# PART Q — CONSENT FLOW

Patient should see:

```text
We will record the health information you provide.
It may be shared with your treating hospital team for your care.
You can review and withdraw consent according to the hospital's process.
```

For low-literacy mode, play an audio explanation.

Record:

- what was consented,
- purpose,
- time,
- method,
- status.

Never use a generic checkbox only.

---

# PART R — ABDM / FHIR ADAPTER

Implement interfaces:

```python
class ABDMAdapter:
    async def lookup_patient(...): ...
    async def link_health_record(...): ...
    async def submit_consent(...): ...
    async def export_record(...): ...
```

For SIH:

```text
REAL_MODE = false
MOCK_MODE = true
```

### Mock integration

Create endpoints:

```text
POST /integration/mock/abha/link
POST /integration/mock/his/push
GET  /integration/mock/abha/patient/{id}
```

Return realistic JSON.

Do not display "ABDM verified" unless the response actually comes from the integration adapter.

---

# PART S — FHIR OUTPUT

Create a conversion service that can produce a bundle-like export.

Example conceptual bundle:

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    { "resource": { "resourceType": "Patient" } },
    { "resource": { "resourceType": "Encounter" } },
    { "resource": { "resourceType": "QuestionnaireResponse" } },
    { "resource": { "resourceType": "Observation" } },
    { "resource": { "resourceType": "DocumentReference" } }
  ]
}
```

Validate JSON schema where practical.

Do not claim ABDM certification from this export alone.

---

# PART T — PATIENT FLOW IMPLEMENTATION

Implement exactly:

### Step 1 — Identify

- New patient or returning patient.
- Demo patient selector allowed in prototype.
- ABHA mock linking.
- Hospital MRN mock.

### Step 2 — Language

Support at minimum:

- English
- Tamil
- Hindi

Optional:

- Telugu
- Malayalam
- Kannada

### Step 3 — Consent

Audio + text.

### Step 4 — Chief complaint

Patient can:

- tap a complaint,
- type,
- speak.

### Step 5 — Adaptive questions

Load question tree based on complaint.

### Step 6 — Safety check

Apply rules.

### Step 7 — Previous documents

Allow:

- camera
- image upload
- PDF

### Step 8 — OCR

Show processing indicator.

### Step 9 — Review extracted information

Allow the patient to correct obvious nonclinical metadata, but keep doctor verification for clinical finalization.

### Step 10 — Summary

Generate draft.

### Step 11 — Submit

Send to doctor queue.

---

# PART U — DOCTOR FLOW IMPLEMENTATION

1. Login.
2. Dashboard.
3. View queue.
4. Sort by priority.
5. Open patient.
6. See structured summary.
7. See source references.
8. See document timeline.
9. Inspect red flags.
10. Edit/confirm.
11. Mark verified.
12. Export/push mock FHIR record.

---

# PART V — SOURCE TRACEABILITY UI

Whenever a summary sentence is shown, provide a small `Source` button.

Example:

```text
Diabetes for 5 years.
[Source: Patient voice turn #7]
```

For medication:

```text
Metformin 500 mg BID
[Source: Prescription DOC-001, page 1]
```

This will improve judge confidence significantly.

---

# PART W — AUDIT LOGGING

Record:

- login
- consent
- document upload
- document read
- AI extraction
- summary generation
- summary edit
- summary verification
- export
- integration event
- logout

Do not log raw medical content by default.

---

# PART X — API LIST

Implement at least:

```text
POST   /api/auth/patient/login
POST   /api/auth/doctor/login
POST   /api/patients
GET    /api/patients/{id}
POST   /api/encounters
GET    /api/encounters/{id}
POST   /api/encounters/{id}/consent
POST   /api/conversation/session
POST   /api/conversation/turn
POST   /api/audio/transcribe
POST   /api/audio/synthesize
POST   /api/documents/upload
POST   /api/documents/{id}/extract
GET    /api/patients/{id}/timeline
POST   /api/summaries/generate
GET    /api/summaries/{encounter_id}
POST   /api/summaries/{id}/verify
GET    /api/triage/alerts
POST   /api/triage/alerts/{id}/ack
POST   /api/fhir/export/{encounter_id}
POST   /api/integration/mock/abha/link
POST   /api/integration/mock/his/push
GET    /api/doctors/me/queue
```

---

# PART Y — ENVIRONMENT VARIABLES

Create `.env.example`:

```env
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/medikiosk
JWT_SECRET=change_me

STT_PROVIDER=sarvam
SARVAM_API_KEY=

LLM_PROVIDER=gemini
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

OCR_PROVIDER=sarvam
OCR_API_KEY=

TTS_PROVIDER=sarvam

ABDM_MODE=mock
HIS_MODE=mock

OBJECT_STORAGE_MODE=local
OBJECT_STORAGE_PATH=./storage

ENABLE_IVR=true
TELEPHONY_MODE=mock
```

Never commit actual secrets.

---

# PART Z — MOCK DATA GENERATION

Create:

```text
scripts/seed_demo_data.py
scripts/generate_synthetic_documents.py
scripts/generate_synthetic_patients.py
```

Seed at least:

- 10 patients
- 3 doctors
- 3 departments
- 10 encounters
- 15 documents
- 5 red-flag cases
- 10 normal cases

Use deterministic IDs and reproducible data.

---

# PART AA — REALISTIC DEMO CASE

Primary demo:

```text
Patient: Lakshmi Devi
Age: 58
Language: Tamil
Chief complaint: chest pain
Duration: 3 days
Associated symptom: breathlessness on exertion
Past history: diabetes, hypertension
Medication: metformin, amlodipine
Old document: prescription + HbA1c report
```

Demo narration:

```text
1. Patient selects Tamil.
2. Patient gives consent.
3. Patient speaks: "எனக்கு மூன்று நாட்களாக மார்பு வலி உள்ளது."
4. System transcribes it.
5. System asks follow-up questions.
6. Patient answers by voice or touch.
7. Safety rules detect if configured red flags are present.
8. Patient scans old prescription.
9. OCR extracts medication.
10. Timeline shows history.
11. Summary is generated.
12. Doctor dashboard receives the patient.
13. Doctor opens source evidence.
14. Doctor edits/accepts the draft.
15. Mock FHIR export is shown.
```

---

# PART AB — SECONDARY DEMO: IVR

Use a browser call simulator if real telecom integration is unavailable.

Example:

```text
CALLER: +91XXXXXXXXXX

SYSTEM:
"Press 1 for Tamil, 2 for Hindi, 3 for English."

CALLER:
1

SYSTEM:
"Please confirm your registered mobile number."

...

SYSTEM:
"Please tell me the main problem you are facing."

CALLER:
"எனக்கு மூன்று நாட்களாக மார்பு வலி இருக்கிறது."

SYSTEM:
STT → structured history

...

RESULT:
Doctor queue updated.
```

---

# PART AC — TESTING

Create tests for:

## Unit tests

- question branching
- red-flag rules
- FHIR conversion
- summary JSON schema
- confidence thresholds
- consent state

## Integration tests

- patient → encounter
- document → OCR → entity extraction
- encounter → summary
- summary → doctor queue
- summary → mock HIS
- summary → mock ABHA adapter

## UI tests

- patient completes flow
- doctor reviews flow
- language changes
- error handling
- upload failure

## Negative tests

- unclear audio
- unsupported language
- blank answer
- duplicate upload
- corrupt PDF
- invalid identity
- expired session
- missing consent

---

# PART AD — OFFLINE / FAILURE MODES

The kiosk must not crash if an AI provider fails.

If STT fails:

```text
Show:
"We could not understand the audio. You can try again or use the touch options."
```

If OCR fails:

```text
Show:
"We could not read this document clearly. You can upload another image or continue without it."
```

If LLM summary fails:

```text
Fallback to structured raw history and show doctor data.
```

The patient should still be able to finish a safe non-AI workflow.

---

# PART AE — OBSERVABILITY

Track:

- STT latency
- OCR latency
- summary latency
- API latency
- error count
- failed uploads
- session completion rate
- document extraction confidence

For prototype, display a simple developer monitoring page.

---

# PART AF — PERFORMANCE TARGETS FOR SIH DEMO

These are engineering goals, not clinical guarantees:

- Main UI interaction < 500 ms excluding AI network call.
- STT result within a few seconds for short utterances.
- Document processing visible with progress indicator.
- Summary generation within an acceptable demo window.
- Doctor dashboard updates without page reload.

Do not invent accuracy percentages unless measured on a test set.

---

# PART AG — PRIVACY / DATA HANDLING

Default prototype policy:

- synthetic data only,
- local database,
- local document storage,
- secrets in environment variables,
- audit log enabled,
- temporary audio deleted after processing unless explicitly needed for demo replay.

For production, add:

- approved hosting boundary,
- key management,
- encryption at rest,
- network controls,
- retention policies,
- formal data-protection assessment,
- hospital security review,
- ABDM consent integration.

The Digital Personal Data Protection Act, 2023 and the notified 2025 Rules should be considered in production planning.

Official references:
- https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf
- https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf

---

# PART AH — ACCESSIBILITY

Implement:

- high contrast,
- large font mode,
- icon-driven controls,
- audio prompts,
- repeat question button,
- speak/tap alternatives,
- one-step-per-screen flow,
- low-text mode,
- timeout with recovery,
- visual microphone status.

Optional stretch:

- sign-language video avatar.

---

# PART AI — CLINICAL PROFILE CONFIGURATION

Do not hard-code every specialty into source code.

Create configuration files:

```text
clinical_profiles/
├── general_medicine.json
├── cardiology.json
├── orthopedics.json
└── ayush_ayurveda.json
```

Each profile contains:

- complaint categories,
- question nodes,
- required history fields,
- safety rules,
- summary template,
- language prompts.

This makes the system scalable.

---

# PART AJ — FOLDER STRUCTURE

If the repo is new or needs organization, target:

```text
MediKiosk/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── scripts/
│   ├── clinical_profiles/
│   └── requirements.txt
├── mobile/
│   ├── lib/
│   ├── test/
│   └── pubspec.yaml
├── web-doctor/
│   ├── src/
│   └── package.json
├── mock-data/
├── docs/
├── storage/
├── docker-compose.yml
├── .env.example
└── README.md
```

If the repository already has another structure, preserve it and adapt the implementation instead of doing a destructive reorganization.

---

# PART AK — ANTIGRAVITY EXECUTION ORDER

The coding agent must execute in this order:

### Step 1 — Audit

- inspect files
- identify stack
- identify running commands
- identify existing endpoints
- identify current screens

### Step 2 — Stabilize

- make current project run
- fix obvious build/runtime issues
- create baseline tests

### Step 3 — Backend foundation

- DB
- auth
- patient
- encounter
- consent

### Step 4 — Patient frontend

- language
- consent
- identity
- question flow

### Step 5 — AI adapters

- STT adapter
- TTS adapter
- LLM adapter
- OCR adapter

### Step 6 — Safety

- red-flag rules
- triage alerts

### Step 7 — Document pipeline

- upload
- OCR
- entity extraction
- timeline

### Step 8 — Summary

- schema-validated summary
- source traceability

### Step 9 — Doctor portal

- queue
- patient detail
- edit/confirm

### Step 10 — Integration adapters

- mock FHIR
- mock HIS
- mock ABHA

### Step 11 — IVR

- mock telephony service
- shared conversation engine

### Step 12 — Demo seed

- synthetic dataset
- demo case

### Step 13 — End-to-end test

Run the complete patient → doctor journey.

---

# PART AL — ANTIGRAVITY DEFINITION OF DONE

The build is not considered complete until:

- `README.md` explains setup.
- `.env.example` exists.
- backend starts.
- frontend starts.
- database migrations/initialization work.
- patient login works.
- doctor login works.
- patient can select language.
- patient can give consent.
- patient can answer by text/touch.
- patient can record voice.
- STT adapter works or mock mode works.
- adaptive questions work.
- red-flag rules work.
- patient can upload document.
- OCR/extraction pipeline works or deterministic mock mode works.
- timeline is generated.
- structured summary is generated.
- doctor sees summary.
- doctor can edit and verify.
- source traceability is visible.
- mock FHIR export works.
- mock HIS push works.
- IVR mock flow writes to same encounter schema.
- test suite passes.

---

# PART AM — DEMO-ACCELERATION / "CHEAT CODE" FOR SIH

Do not waste the SIH prototype phase trying to make every component production-grade.

Use a **two-layer architecture**:

## Layer 1 — Real showcase components

Make these genuinely functional:

- voice recording,
- STT,
- adaptive questioning,
- document upload,
- OCR/extraction,
- doctor dashboard,
- editable summary,
- source traceability,
- red-flag rules.

## Layer 2 — Realistic mock adapters

Mock:

- ABHA lookup/link,
- HIS push,
- hospital master data,
- telephony provider.

This is not cheating. It is standard prototyping architecture as long as the UI clearly labels mocks as mocks.

The judges should see:

```text
REAL patient interaction
        ↓
REAL AI processing
        ↓
REAL structured output
        ↓
REAL doctor review
        ↓
MOCK external-system adapter
```

This is far stronger than a fake video where everything is pre-recorded.

---

# PART AN — JUDGE DEMONSTRATION SCRIPT

### Scene 1

Patient approaches kiosk.

### Scene 2

Select Tamil.

### Scene 3

Consent is explained by audio.

### Scene 4

Patient speaks complaint.

### Scene 5

System asks adaptive follow-ups.

### Scene 6

Patient uploads old prescription.

### Scene 7

System extracts medication and report values.

### Scene 8

Timeline is generated.

### Scene 9

Red-flag badge appears if demo criteria trigger.

### Scene 10

Doctor dashboard receives patient.

### Scene 11

Doctor opens summary and taps source evidence.

### Scene 12

Doctor edits one field and confirms.

### Scene 13

Show mock FHIR export / HIS push result.

### Scene 14

Optional: show the same patient using IVR and the same doctor queue receiving that record.

---

# PART AO — WHAT THE TEAM SHOULD NOT CLAIM DURING PITCH

Do not say:

- "No one in the world has done this."
- "AI diagnoses the patient."
- "AI decides which treatment is required."
- "ABHA is created automatically by our software from name and phone number."
- "The system is 100% accurate."
- "This is already fully integrated with government systems" unless it really is.

Say instead:

- "We integrate existing digital-health infrastructure with a first-mile clinical intake layer."
- "AI assists data capture and structuring; the doctor remains the decision-maker."
- "The SIH gap is the combination of these capabilities in an accessible, patient-facing workflow for Indian public hospitals."
- "Our prototype uses mock external integrations and is architected for official integration."

---

# PART AP — SCALABILITY PLAN

## Horizontal scaling

- stateless FastAPI instances
- load balancer
- async workers
- Redis
- object storage
- PostgreSQL with read replicas later

## AI scaling

- provider adapter
- request queue
- retry policy
- timeout
- fallback model/provider
- cached TTS prompts

## Document scaling

- upload object storage
- asynchronous OCR workers
- batch extraction
- confidence queue for human review

## Hospital scaling

Multi-tenant model:

```text
Hospital
 ├── Departments
 │    ├── Doctors
 │    ├── Profiles
 │    └── Queues
 └── Patients / Encounters
```

Each hospital can configure:

- branding,
- language list,
- clinical profiles,
- triage rules,
- HIS connector,
- retention policy.

---

# PART AQ — FUTURE EXTENSIONS

After the core prototype is stable, consider:

- more Indian languages,
- offline/edge inference for kiosk resilience,
- continuous speech streaming,
- richer document handwriting models,
- medication interaction support for clinician review,
- appointment scheduling,
- queue prediction,
- referral routing,
- hospital analytics,
- patient longitudinal timeline,
- multilingual doctor-patient explanation,
- sign-language support,
- approved ABDM production integration.

Do not add these before the core first-mile workflow works end-to-end.

---

# PART AR — FINAL ARCHITECTURE SUMMARY

```text
                         ┌──────────────────────┐
                         │      PATIENT         │
                         └──────────┬───────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  KIOSK / WEB / IVR    │
                        └───────────┬───────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
             VOICE/TTS            TOUCH            DOCUMENTS
                 │                  │                  │
                 ▼                  └────────┬─────────┘
              STT / NLP                       ▼
                 │                         OCR / CV
                 └───────────────┬───────────┘
                                 ▼
                       CLINICAL STRUCTURING
                                 │
                       ┌─────────┴─────────┐
                       ▼                   ▼
                 SAFETY RULES          TIMELINE
                       │                   │
                       └─────────┬─────────┘
                                 ▼
                       SUMMARY GENERATOR
                                 │
                                 ▼
                         DOCTOR DASHBOARD
                                 │
                         EDIT / VERIFY
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
               FHIR / HIS                ABDM ADAPTER
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                          DIGITAL RECORD
```

---

# PART AS — FINAL MASTER INSTRUCTION TO THE CODING AGENT

> Build MediKiosk as a safe, modular, testable, first-mile clinical-intake platform. Inspect the existing repository before changing it. Preserve working code. Implement patient and doctor portals, voice + touch history collection, adaptive question trees, deterministic red-flag rules, document OCR/entity extraction, timeline construction, schema-validated clinician-reviewable summaries, source traceability, consent, audit logging, mock FHIR/HIS/ABHA adapters, and a shared IVR channel. Use synthetic data for the prototype. Keep AI providers behind interfaces. Never implement autonomous diagnosis or prescribing. Never treat Aadhaar as the medical record key. Clearly label mock integrations. Produce a working end-to-end demo and document all setup, architecture, APIs, data models, tests, and known limitations.

---

# REFERENCES FOR THE TECHNICAL CHOICES

- Sarvam API documentation: https://docs.sarvam.ai/
- Sarvam speech-to-text: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe
- Sarvam models: https://docs.sarvam.ai/api/getting-started/models
- Google Gemini 2.5 Flash: https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash
- PaddleOCR PP-Structure: https://www.paddleocr.ai/main/en/version2.x/ppstructure/overview.html
- HL7 FHIR QuestionnaireResponse: https://hl7.org/fhir/questionnaireresponse.html
- NIC NextGen eHospital: https://www.nic.gov.in/project/nextgen-ehospital/
- ABHA Scan & Share: https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2009483&lang=2&reg=48
- NHS online consultation tools: https://www.england.nhs.uk/long-read/online-consultation-tools/
- Digital Personal Data Protection Act 2023: https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf
- Digital Personal Data Protection Rules 2025: https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf
- WHO AI ethics and governance: https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-artificial-intelligence-ai-in-health-and-six-guiding-principles-for-its-design-and-use
