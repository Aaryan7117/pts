# MediKiosk — Single-Developer Full Implementation Master Workflow

## Purpose

This document is the **single source of truth for one developer working in Antigravity** on the MediKiosk client-facing product, integration, doctor dashboard, accessibility flows, testing, and final delivery.

**This is intentionally NOT a Flutter implementation document.** Flutter-specific implementation belongs to a different workstream. This document describes the product, architecture, UI/UX behavior, backend integration, IVR boundary, doctor workflow, testing, and the exact Antigravity execution prompt.

---

# 1. Developer Role

You are the **single senior product/full-stack implementation developer**.

Own:

- Patient kiosk/web UI
- Patient BYOD web/mobile experience where required
- Doctor dashboard
- Navigation and client-side state
- Voice interaction UI
- Document/prescription capture
- OCR result and evidence visualization
- Queue/token UI
- Hospital services/map UI
- Emergency UI
- Multilingual UX
- Accessibility
- Loading/error/offline states
- API integration with the existing backend
- End-to-end testing
- Production polish
- Deployment/build documentation

Do NOT:

- rebuild the existing backend unnecessarily
- invent undocumented APIs
- put API secrets in frontend code
- duplicate clinical safety rules in UI code
- fake live ambulance/IVR/FHIR integrations
- remove required MediKiosk features
- expose patient data in logs

---

# 2. Repository and Source-of-Truth Order

Repository:

`Aaryan7117/pts`

Read these files completely before implementation:

1. `MEDIKIOSK_ANDROID_DESIGN_SPEC.md`
2. `MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md`
3. `MediKiosk_Architecture_Review_v2.md`
4. `MediKiosk_Architecture_Update_Summary.md`
5. `MediKiosk_Full_Context_Handoff.md`
6. `MediKiosk_Tech_Stack_Finalized.md`

Then inspect:

```text
app/
app/api/
app/core/
app/schemas/
mobile/
static/
requirements.txt
run.py
.env.example
```

When documents and code disagree, **actual working backend behavior wins**. Never assume that a feature described in a specification is already implemented.

---

# 3. Current Backend Baseline

The repository currently contains a FastAPI backend with these API areas:

```text
/api/encounters/*
/api/call/*
/api/documents/*
/api/queue/*
/api/doctor/*
/api/health
/docs
```

The backend entry point registers:

- encounter APIs
- conversational call-session APIs
- document APIs
- queue APIs
- doctor APIs
- health check
- Swagger/OpenAPI

The encounter bootstrap creates an encounter/patient reference and queue token.

Known voice endpoints:

```text
POST /api/call/session/start
POST /api/call/audio-turn
POST /api/call/session/end
```

The developer must inspect the exact Pydantic request/response schemas before integration.

---

# 4. CRITICAL IVR CLARIFICATION

MediKiosk has a **telephone/IVR backup channel** for elderly/basic-phone users.

Its intended purpose:

- elderly users who do not use smartphones
- basic-phone users
- users with low digital literacy
- rural users
- users unable to comfortably operate the kiosk

Conceptual flow:

```text
Basic phone
   ↓
Hospital/toll-free number
   ↓
IVR greeting
   ↓
DTMF language selection
   ↓
Consent / notice
   ↓
Identity
   ↓
Voice/keypad responses
   ↓
ASR / intent extraction
   ↓
Same clinical intake model
   ↓
Same triage
   ↓
Same doctor dashboard
```

### Important engineering fact

The existing `/api/call/*` endpoints are a **conversational voice-session API**. They are not, by themselves, proof that a PSTN/SIP/Twilio/Plivo telephone system is implemented.

Therefore:

- Do not fake a phone call.
- Search the repository for actual telephony integration.
- If a provider is present, connect it.
- If no provider exists, create/document the integration boundary only.
- Do not claim “live IVR” without an actual tested telephony provider.
- Reuse the same encounter/clinical data model.
- IVR is a separate channel, **not another Flutter/visual screen**.

---

# 5. Overall Architecture

```text
                 PATIENT CHANNELS
       ┌────────────┬─────────────┐
       │            │             │
     KIOSK        BYOD          IVR
       │            │             │
       └────────────┼─────────────┘
                    ↓
              BACKEND API
                    ↓
       ┌────────────┼────────────┐
       ↓            ↓            ↓
     Speech       OCR/Docs    Clinical Core
       │            │            │
       └────────────┼────────────┘
                    ↓
             Clinical Session
                    ↓
       ┌────────────┼─────────────┐
       ↓            ↓             ↓
    Triage        Queue        Evidence
       └────────────┼─────────────┘
                    ↓
             Doctor Dashboard
                    ↓
          Clinical Verification
                    ↓
             EMR / FHIR / ABDM
```

Core principle:

**Patient channel → structured backend → clinician verification.**

The patient is not the clinical editor.

---

# 6. Complete Patient Flow

```text
WELCOME
 ↓
LANGUAGE
 ↓
CONSENT
 ↓
IDENTITY
 ↓
CARE STREAM
 ↓
CHIEF COMPLAINT
 ↓
VOICE / TEXT INTAKE
 ↓
ADAPTIVE FOLLOW-UP
 ↓
PROCESSING
 ↓
EXPLAIN-BACK
 ↓
CONFIRM / REPEAT
 ↓
TRIAGE
 ↓
DOCUMENTS
 ↓
CAMERA
 ↓
OCR
 ↓
EVIDENCE
 ↓
VITALS
 ↓
AYUSH
 ↓
DEPARTMENT ROUTING
 ↓
QUEUE / TOKEN
 ↓
HOSPITAL SERVICES
 ↓
EMERGENCY IF REQUIRED
 ↓
COMPLETION
 ↓
AUTO RESET
```

At any stage:

```text
possible red flag
      ↓
emergency path
      ↓
clinical escalation
```

Do not force a possible emergency through a long normal intake.

---

# 7. Patient Screen Blueprint

## 01 — Welcome

Elements:

- MediKiosk logo
- professional healthcare visual
- large Start button
- Help button
- privacy reassurance
- optional language shortcut

Start → Language.

---

## 02 — Language

Priority languages:

```text
English
Hindi
Tamil
Telugu
Marathi
```

Use large language cards.

Each card:

- native script
- readable label
- optional speaker icon for pronunciation

Persist language for:

- UI
- questions
- ASR
- TTS
- explain-back

---

## 03 — Consent

Explain simply:

- why information is collected
- that healthcare staff will see it
- that documents may be digitized
- how the session ends/reset

Actions:

```text
I Agree
I Need Help
Back
```

Provide audio playback.

Do not show a giant legal paragraph as the primary experience.

---

## 04 — Identity

Support whatever the backend actually supports:

- returning patient
- new patient
- guest
- ABHA/identifier
- QR/token continuation

Prefer simple choices over passwords.

Do not invent authentication.

---

## 05 — Care Stream

Large choices:

```text
New health problem
Follow-up
Medicine review
Lab/report review
AYUSH consultation
Other
Emergency help
```

The selected path determines the intake route.

---

## 06 — Voice Introduction

Explain:

> “You can speak naturally. You do not need to type.”

Controls:

- microphone
- text fallback
- replay
- help

Use a large microphone with a subtle breathing halo.

---

## 07 — Voice Capture

States:

```text
READY
LISTENING
PROCESSING
RETRY
MICROPHONE DENIED
OFFLINE
```

Show:

- waveform
- listening indicator
- transcript preview where appropriate
- stop
- say again

Never show raw technical errors.

---

## 08 — Conversational Questions

One short question at a time.

Example:

```text
Where does it hurt?
How long have you had this problem?
What makes it better or worse?
```

The actual clinical question sequence comes from the backend/interview engine.

The UI must not hardcode clinical decision rules.

---

## 09 — Processing

Use calm states:

```text
Understanding your information...
Organizing your health history...
Checking important safety information...
Preparing your summary...
```

Never say that the AI has diagnosed the patient.

---

## 10 — Explain-Back

Critical accessibility feature.

Example:

```text
You said:
• knee pain
• for 3 weeks
• worse in the morning
```

Audio reads it back.

Large actions:

```text
YES, THAT IS CORRECT
NO, LET ME SAY IT AGAIN
```

Do not force elderly/low-literacy users to edit complex medical terminology.

---

## 11 — Triage

Possible statuses:

```text
ROUTINE
URGENT
EMERGENCY
```

Patient wording must be simple.

The decision must come from deterministic backend rules.

Emergency path exits normal intake.

---

## 12 — Document Hub

Options:

```text
Prescription
Lab report
Discharge summary
Other medical document
Skip
```

Explain why documents help the doctor.

---

## 13 — Document Camera

Provide:

- camera preview
- document frame
- capture
- retake
- use photo
- flash if useful

Use a subtle scan-line animation.

---

## 14 — OCR Processing

Show:

```text
Reading document...
Finding medicines...
Finding lab values...
Linking information to the original document...
```

Use the actual backend OCR path.

---

## 15 — OCR Result

Show:

```text
Medicine
Dose
Frequency

Lab
Value
Unit
Reference range
```

Important facts must retain:

- document ID
- source line/region where available
- confidence
- provenance

Do not invent bounding boxes.

---

## 16 — Evidence Viewer

Doctor view must support:

- original prescription image
- zoom
- source line
- bounding box where actually supplied
- confidence
- extraction provenance
- normalized value
- original text

Signature interaction:

```text
Click medicine
      ↓
open source prescription
      ↓
highlight exact source region
```

If backend only supplies line indices, implement line evidence rather than fake coordinates.

---

## 17 — Vitals

Possible values:

```text
Blood pressure
Pulse
Temperature
SpO2
Blood glucose
Weight
```

Only show actual device/manual values.

Never fabricate readings.

---

## 18 — AYUSH History

Capture where relevant:

```text
Prakriti
Agni
Ahara
Vihara
Lifestyle
Traditional medicine use
Relevant AYUSH history
```

Use short questions and audio.

Map into the backend's structured AYUSH schema.

---

## 19 — Queue / Department

Show:

```text
Intake complete
Department
Token
Queue position / estimate
```

Example:

```text
General Medicine
A-402
```

Never hardcode live wait estimates.

---

## 20 — Hospital Services

Cards:

```text
OPD
Pharmacy
Laboratory
Billing
Emergency
Help Desk
Washrooms
Departments
```

---

## 21 — Hospital Map

Show:

- destination
- route
- current location when permitted
- manual destination fallback

Actions:

```text
START DIRECTIONS
CALL HELP DESK
BACK
```

If location permission fails, provide manual selection.

---

## 22 — Emergency

Large high-priority layout:

```text
EMERGENCY HELP
```

Actions:

```text
CALL EMERGENCY SERVICE
CALL HOSPITAL
REQUEST AMBULANCE
```

Require confirmation where appropriate.

---

## 23 — Ambulance Status

Only show:

- requested
- dispatched
- pickup
- destination
- ETA

when actual integration supplies them.

Otherwise clearly show:

```text
Service unavailable / prototype
```

Never fake a live ETA.

---

## 24 — Completion / Reset

Show:

```text
Your intake is complete.

Your information has been prepared for the healthcare team.
```

Show token.

Then:

```text
This screen will reset automatically.
```

Clear temporary:

- patient details
- audio
- transcripts
- temporary images
- sensitive session state

unless needed for a pending backend transaction.

---

# 8. Doctor Dashboard

The doctor dashboard is the clinical verification layer.

## Dashboard

Show:

```text
Queue
Emergency
Urgent
Routine
Completed
```

Patient card:

- token
- demographics where appropriate
- chief complaint
- severity
- key changes
- waiting state
- verification state

---

# 9. Doctor Patient Case

Structure:

```text
Patient header
 ↓
Priority
 ↓
Changes-first summary
 ↓
Patient-reported facts
 ↓
AI-structured facts
 ↓
AYUSH profile
 ↓
Vitals
 ↓
Medication timeline
 ↓
Documents
 ↓
OCR evidence
 ↓
Clinical gaps
 ↓
Drug interaction alerts
 ↓
Abnormal lab alerts
 ↓
Doctor verification
 ↓
FHIR/EMR boundary
```

---

# 10. Provenance

Every important fact must visibly identify its source:

```text
PATIENT SAID
VOICE
TOUCH
OCR
EMBEDDING
AI EXTRACTED
SYSTEM FLAGGED
DOCTOR VERIFIED
```

Never make AI-extracted data look identical to doctor-verified information.

---

# 11. Medication Timeline

Support temporal medication history:

```text
March
Medication prescribed
 ↓
June
Patient stopped
 ↓
August
Dose changed
```

Highlight:

- stopped medications
- dose changes
- gaps
- contradictions
- new prescriptions

This is a clinical history aid, not a diagnosis.

---

# 12. Clinical Gap List

Show missing questions/facts identified by the backend.

Example:

```text
Clinical gaps detected

• Peripheral neuropathy not asked
• Morning stiffness duration not captured
```

These are prompts for clinician review, not diagnoses.

---

# 13. Safety Presentation

## Drug interactions

Show:

```text
CRITICAL / HIGH / MODERATE
Drug A + Drug B
Reason
Reference/source
```

## Abnormal labs

Show:

```text
HIGH
HbA1c: 9.2%
Reference range: ...
```

Do not use an LLM as the sole authority for interaction or lab thresholds.

---

# 14. API Integration Rules

Use actual backend routes and schemas.

Known route groups:

```text
POST /api/encounters/bootstrap
GET  /api/encounters/{encounter_id}
PATCH /api/encounters/{encounter_id}/status

POST /api/call/session/start
POST /api/call/audio-turn
POST /api/call/session/end

POST /api/documents/upload

GET  /api/queue/status/{token}

POST /api/doctor/auth
GET  /api/doctor/queue
GET  /api/doctor/patient/{encounter_id}

GET  /api/health
GET  /docs
```

The exact document, queue and doctor endpoints must be read from:

```text
app/api/documents.py
app/api/queue.py
app/api/doctor.py
app/schemas/
```

Never invent request/response fields.

---

# 15. Core Data Concepts

Design client models around:

```text
Encounter
PatientReference
Consent
IntakeTurn
Transcript
ClinicalFact
ClinicalSummary
TriageResult
Document
OCRField
EvidenceReference
Vital
AyushProfile
DepartmentRoute
QueueTicket
HospitalService
EmergencyRequest
CallSession
DoctorPatientView
```

Clinical facts should preserve, where provided:

```text
id
encounter_id
category
field
value
dose
frequency
patient_words
normalized_concept
concept_code
provenance
source_type
source_reference
confidence
temporal_state
status
created_at
```

Do not throw away provenance to simplify rendering.

---

# 16. AI Boundary

AI may:

- transcribe
- translate
- normalize
- extract
- summarize
- perform semantic retrieval
- process documents
- assist routing
- flag possible red flags

AI must NOT be presented as:

- autonomous doctor
- definitive diagnosis engine
- replacement for clinician verification

Pipeline:

```text
Voice/document
 ↓
ASR/OCR
 ↓
Language normalization
 ↓
Semantic matching
 ↓
Structured extraction
 ↓
Deterministic validation
 ↓
Deterministic safety rules
 ↓
Clinical summary
 ↓
Doctor verification
```

---

# 17. Model/Provider Strategy

The architecture documents describe a hybrid edge/cloud design.

Potential configured services include:

### Cloud

- Sarvam speech
- Gemini multimodal/document processing
- Groq acceleration

### Edge/offline

- AI4Bharat IndicWhisper / IndicConformer
- RapidOCR
- multilingual MiniLM embeddings
- Qwen 2.5 7B via Ollama
- IndicF5 / Piper TTS

The frontend must not depend on provider-specific implementation.

It should consume backend results.

---

# 18. Multilingual UX

Priority:

```text
English
Hindi
Tamil
Telugu
Marathi
```

Requirements:

- every patient-visible string localized
- no English-only hardcoded screens
- TTS follows session language
- questions can be replayed
- simple patient wording
- doctor workspace may use English while preserving original-language patient content

---

# 19. Accessibility

Target users include elderly, rural and low-literacy patients.

Required:

- large touch targets
- high contrast
- short sentences
- one task per screen
- audio guidance
- replay
- voice-first interaction
- text fallback
- visible focus
- no color-only meaning
- no tiny icons
- no dense forms
- no forced typing of clinical terms

Use:

```text
icon + text + color
```

for important status states.

---

# 20. Offline / Error States

The client must distinguish:

```text
ONLINE
LOCAL NETWORK
OFFLINE
SYNCING
RETRYING
SERVICE UNAVAILABLE
```

Every important network operation needs:

- loading
- success
- retry
- timeout
- failure
- offline state

Never show stack traces to patients.

Never pretend a failed request succeeded.

---

# 21. Security / Privacy

Never:

- put API keys in frontend code
- commit `.env`
- log patient medical data
- store temporary documents forever
- expose doctor endpoints without authentication
- commit audio recordings or patient records

Use public client configuration only.

Secrets belong on the server.

---

# 22. Repository Reality Audit

Before declaring completion, explicitly verify:

### Present in repository

- FastAPI backend
- encounter bootstrap
- voice session endpoints
- document API
- queue API
- doctor API
- health endpoint
- Swagger
- mobile project

### Must be verified before claiming complete

- exact OCR response contract
- exact evidence/bounding-box implementation
- exact doctor response structure
- actual FHIR/ABDM integration
- actual ambulance integration
- actual PSTN/SIP/telephony IVR
- production authentication
- production database/deployment
- real hospital map/service data

**A specification saying something exists is not proof that the code implements it.**

---

# 23. Antigravity Development Order

```text
PHASE 0
Read all specifications

PHASE 1
Inspect repository

PHASE 2
Audit backend contracts

PHASE 3
Audit existing frontend/mobile code

PHASE 4
Create implementation map

PHASE 5
Create/reuse design system

PHASE 6
Implement patient flow

PHASE 7
Implement voice/document/evidence

PHASE 8
Implement queue/services/map/emergency

PHASE 9
Implement doctor dashboard

PHASE 10
Integrate actual APIs

PHASE 11
Add offline/error/permission states

PHASE 12
Multilingual/accessibility QA

PHASE 13
End-to-end testing

PHASE 14
Fix all issues

PHASE 15
Final polish

PHASE 16
Final acceptance audit
```

---

# 24. Git Rules

Before changing code:

```text
git status
git branch
inspect current diff
```

Use a feature branch.

Use logical commits:

```text
feat: patient kiosk foundation
feat: conversational intake
feat: document evidence viewer
feat: doctor queue
feat: clinical verification
feat: emergency flow
test: patient journey
fix: API contract mismatch
```

Never commit:

```text
.env
API keys
tokens
patient records
audio recordings
temporary OCR files
```

---

# 25. Testing Matrix

Patient:

```text
Welcome
Language
Consent
Identity
Intake
Voice
Text fallback
Follow-up
Explain-back
Triage
Documents
OCR
Evidence
Vitals
AYUSH
Queue
Services
Map
Emergency
Completion/reset
```

Doctor:

```text
Login
Queue
Priority
Patient case
Summary
Facts
Vitals
AYUSH
Documents
Evidence
Medication timeline
Clinical gaps
Interaction alerts
Lab alerts
Verification
```

Failure tests:

```text
No network
Backend unavailable
Microphone denied
Camera denied
Location denied
Malformed response
Expired session
Upload failure
OCR failure
ASR failure
TTS failure
Timeout
Duplicate submission
```

---

# 26. Definition of Done

```text
[ ] Repository inspected
[ ] Existing backend preserved
[ ] API contracts mapped
[ ] Patient journey complete
[ ] All required patient screens complete
[ ] Voice connected to real backend
[ ] Text fallback works
[ ] Explain-back works
[ ] Triage works
[ ] Document capture works
[ ] OCR works according to backend capability
[ ] Evidence viewer works
[ ] Vitals works
[ ] AYUSH works
[ ] Queue works
[ ] Hospital services works
[ ] Map fallback works
[ ] Emergency works
[ ] Completion/reset works
[ ] Doctor dashboard works
[ ] Provenance visible
[ ] Medication timeline works
[ ] Clinical gaps visible
[ ] Safety alerts visible
[ ] Multilingual UI works
[ ] Accessibility checked
[ ] Offline/error states checked
[ ] No frontend secrets
[ ] No fake live integrations
[ ] Tests pass
[ ] End-to-end demo passes
```

---

# 27. MASTER ANTIGRAVITY PROMPT

Copy this entire prompt into Antigravity Agent **after placing this file in the repository root**.

```text
You are the single senior product/full-stack implementation engineer responsible for completing the MediKiosk client-facing product in the existing repository.

FIRST READ:
MEDIKIOSK_SINGLE_DEVELOPER_MASTER_WORKFLOW.md

Then read completely:

MEDIKIOSK_ANDROID_DESIGN_SPEC.md
MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md
MediKiosk_Architecture_Review_v2.md
MediKiosk_Architecture_Update_Summary.md
MediKiosk_Full_Context_Handoff.md
MediKiosk_Tech_Stack_Finalized.md

Then inspect the actual source code.

Do not begin random UI generation.

==================================================
MISSION
==================================================

Complete the MediKiosk product using the existing backend.

Do NOT rebuild the backend from scratch.

Preserve the complete product workflow:

WELCOME
→ LANGUAGE
→ CONSENT
→ IDENTITY
→ CARE STREAM
→ VOICE/TEXT INTAKE
→ ADAPTIVE FOLLOW-UP
→ PROCESSING
→ EXPLAIN-BACK
→ CONFIRMATION
→ TRIAGE
→ DOCUMENTS
→ CAMERA
→ OCR
→ EVIDENCE
→ VITALS
→ AYUSH
→ QUEUE
→ HOSPITAL SERVICES
→ MAP
→ EMERGENCY
→ AMBULANCE STATUS WHEN REAL INTEGRATION EXISTS
→ COMPLETION/RESET

Also complete:

DOCTOR LOGIN
→ QUEUE
→ PRIORITY
→ PATIENT CASE
→ CHANGES-FIRST SUMMARY
→ PATIENT FACTS
→ AI-STRUCTURED FACTS
→ AYUSH
→ VITALS
→ MEDICATION TIMELINE
→ DOCUMENTS
→ OCR
→ EVIDENCE
→ CLINICAL GAPS
→ DRUG INTERACTION ALERTS
→ ABNORMAL LAB ALERTS
→ DOCTOR VERIFICATION
→ FHIR/EMR BOUNDARY

==================================================
NON-NEGOTIABLE RULES
==================================================

1. Inspect existing code before changing anything.
2. Do not delete working code blindly.
3. Do not rebuild the backend unnecessarily.
4. Do not invent API endpoints.
5. Read actual Pydantic schemas before integration.
6. Never put API/provider secrets in frontend code.
7. Do not duplicate clinical decision logic in the UI.
8. Never present AI output as a diagnosis.
9. Never fabricate live queue, ambulance, hospital or clinical data.
10. Every important button must perform a real action.
11. Every API operation must have loading/success/retry/error handling.
12. Support offline/local-network states.
13. Preserve evidence/provenance.
14. Keep patient interaction simple.
15. Complex reconciliation belongs to the doctor.
16. Support English, Hindi, Tamil, Telugu and Marathi.
17. Use accessible large controls.
18. Do not use color as the only status indicator.
19. Do not expose stack traces to patients.
20. Do not claim integrations are live unless actually connected and tested.
21. Do not stop after static screens.
22. Run tests and fix errors before declaring completion.

==================================================
STEP 1 — AUDIT
==================================================

Inspect:

app/
app/api/
app/core/
app/schemas/
mobile/
static/
requirements.txt
run.py
.env.example

Inspect:

- encounter APIs
- call session APIs
- document APIs
- queue APIs
- doctor APIs
- database models
- schemas
- authentication
- existing frontend
- existing mobile app
- existing tests
- model/provider adapters
- configuration

Create:

IMPLEMENTATION_AUDIT.md

Include:

- architecture
- existing features
- existing screens
- API routes
- schemas
- integration status
- missing features
- risks
- IVR status
- ambulance status
- FHIR/ABDM status

==================================================
STEP 2 — IMPLEMENTATION TRACKING
==================================================

Create:

IMPLEMENTATION_STATUS.md

Track:

Feature
Status
Files
API
Tests
Notes

Statuses:

NOT_STARTED
IN_PROGRESS
BLOCKED
COMPLETE
VERIFIED

Never mark a feature COMPLETE merely because a UI screen exists.

==================================================
STEP 3 — DESIGN SYSTEM
==================================================

Implement the design specification:

- professional healthcare
- calm
- trustworthy
- high contrast
- elderly friendly
- large controls
- rounded cards
- restrained shadows
- minimal clutter
- subtle motion
- multilingual typography

Create/reuse components:

- buttons
- cards
- status badges
- headers
- microphone control
- waveform
- document viewer
- evidence viewer
- queue card
- clinical fact card
- loading state
- error state
- offline state
- permission state

==================================================
STEP 4 — PATIENT EXPERIENCE
==================================================

Implement all patient screens in the exact workflow from the master document.

Every screen must be connected.

No dead buttons.

No placeholder-only implementation.

==================================================
STEP 5 — VOICE
==================================================

Inspect the actual schemas first.

Integrate:

POST /api/call/session/start
POST /api/call/audio-turn
POST /api/call/session/end

Implement:

- microphone permission
- recording
- waveform
- upload
- transcript
- extracted facts
- next question
- TTS playback
- retry
- timeout
- failure
- completion

==================================================
STEP 6 — DOCUMENT/OCR
==================================================

Inspect app/api/documents.py and schemas.

Implement:

- camera/capture
- upload
- processing
- OCR result
- confidence/provenance
- source evidence
- retry/failure

If actual bounding boxes exist:
implement interactive highlighting.

If only line evidence exists:
implement line evidence.

Never invent coordinates.

==================================================
STEP 7 — QUEUE
==================================================

Inspect app/api/queue.py.

Use actual backend data.

Implement:

- token
- department
- priority
- position
- waiting state
- refresh
- failure state

Never hardcode live values.

==================================================
STEP 8 — DOCTOR DASHBOARD
==================================================

Inspect app/api/doctor.py and schemas.

Implement:

- authentication
- queue
- severity
- patient case
- summary
- patient facts
- AI facts
- AYUSH
- vitals
- documents
- evidence
- medication timeline
- clinical gaps
- interaction alerts
- abnormal labs
- doctor verification
- export/integration boundary

Clearly distinguish:

PATIENT SAID
OCR
AI EXTRACTED
SYSTEM FLAGGED
DOCTOR VERIFIED

==================================================
STEP 9 — EMERGENCY
==================================================

Implement clear emergency states.

Never fake ambulance dispatch.

Only show live dispatch/ETA if the backend provides actual data.

==================================================
STEP 10 — IVR
==================================================

Search repository for:

Twilio
Plivo
SIP
telephony
DTMF
webhook
phone number
call routing

If real telephony exists:
integrate it.

If not:
document the missing integration and create only a clean adapter/interface where useful.

Do NOT create a fake telephone experience.

The IVR must use the same encounter/clinical data model.

==================================================
STEP 11 — SECURITY
==================================================

Audit:

- secrets
- API keys
- logs
- local storage
- patient data exposure
- doctor authentication

Do not print secrets.

Do not commit secrets.

==================================================
STEP 12 — ACCESSIBILITY
==================================================

Verify:

- large touch targets
- high contrast
- readable text
- audio guidance
- replay
- simple wording
- multilingual rendering
- long-text wrapping
- no color-only meaning
- elderly-friendly spacing

==================================================
STEP 13 — TEST
==================================================

Run all available tests.

Manually verify:

1. new patient happy path
2. voice path
3. text fallback
4. document path
5. OCR/evidence path
6. triage
7. emergency
8. queue
9. doctor verification
10. offline
11. microphone denied
12. camera denied
13. backend unavailable
14. OCR failure
15. ASR failure
16. TTS failure
17. session reset
18. multilingual flow

==================================================
STEP 14 — FINAL REPORT
==================================================

Create:

FINAL_IMPLEMENTATION_REPORT.md

Include:

- implemented features
- screens
- API integrations
- tests
- known limitations
- IVR status
- ambulance status
- FHIR/ABDM status
- deployment instructions
- remaining work

Be completely honest about what is real versus prototype.

START NOW.

FIRST:
READ THE SPECIFICATIONS.

SECOND:
INSPECT THE REPOSITORY.

THIRD:
CREATE IMPLEMENTATION_AUDIT.md.

ONLY THEN START IMPLEMENTATION.
```

---

# 28. Final Product Principle

The goal is NOT “a lot of screens”.

The goal is:

**one coherent MediKiosk system where Kiosk, BYOD and the elderly/basic-phone IVR path feed the same clinical data model, while the doctor dashboard provides evidence-linked clinical verification.**

