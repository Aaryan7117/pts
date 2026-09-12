# MEDIKIOSK — DEVELOPMENT FLOW MASTER
## The exact workflow the coding AI must follow

> **Purpose:** This is the execution/control document. Read this file first. It defines WHAT must be built, in WHAT order, how the two developers divide the work, how the Flutter app connects to backend/AI, and what must never be changed.
>
> **Implementation target:** One Flutter codebase for Android + iOS. Patient-facing application first; backend/cloud AI and doctor web integration in parallel. Telephone/IVR is a backup channel, not a replacement for the main app.
>
> **Source of truth:** This document and the companion `MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md`. Do not invent new product flows unless explicitly approved.

---

# 1. NON-NEGOTIABLE PRODUCT FLOW

```text
PATIENT
  ↓
Welcome
  ↓
Language
  ↓
Consent
  ↓
Identification (ABHA / mobile / skip)
  ↓
Reason for visit / care stream
  ↓
Voice or text symptom intake
  ↓
Conversational follow-up
  ↓
Cloud speech + language + semantic extraction
  ↓
Simple patient confirmation
  ↓
Deterministic safety/triage check
  ├── RED FLAG → nurse/duty terminal + emergency path
  └── NORMAL   → continue
  ↓
Document scan (optional)
  ↓
OCR + document understanding + evidence linking
  ↓
Vitals (when available)
  ↓
AYUSH profile (when applicable)
  ↓
Department routing
  ↓
Queue / appointment / token
  ↓
Hospital services / map / directions (optional)
  ↓
Emergency assistance (available separately)
  ↓
Completion
  ↓
Secure reset / wipe session
```

The patient never becomes the clinical editor. Complex correction/reconciliation belongs on the clinician dashboard.

---

# 2. DEVELOPMENT ORDER — DO NOT SKIP STEPS

## Phase 0 — Freeze the contract
1. Read this file completely.
2. Read `MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md` completely.
3. Inspect the repository before editing anything.
4. Preserve the existing project if it is already a valid Flutter project.
5. Do not replace working code blindly.
6. Create a short implementation checklist from the requirements.
7. Confirm Android and iOS targets exist.

## Phase 1 — Flutter foundation
Build:
- project structure
- theme/design tokens
- localization
- routing
- app state machine
- reusable components
- permission service interfaces
- repository interfaces
- mock data source
- error/offline states

At the end of Phase 1, the app must launch and navigate through all screens in mock mode.

## Phase 2 — Complete patient UI
Implement every screen from the companion UI prompt.
Requirements:
- no placeholder rectangles
- no dead buttons
- every button has a defined transition or action
- every screen has loading/error/offline behavior where applicable
- accessibility and large touch targets
- Android and iOS safe areas

## Phase 3 — Mock end-to-end flow
The complete patient journey must work without internet using deterministic mock repositories:
- start
- language
- consent
- identification
- intake
- follow-up
- summary
- triage
- document flow
- vitals
- AYUSH
- routing
- queue
- completion/reset

## Phase 4 — Backend integration
Replace mock repositories one service at a time:
1. session
2. patient/identity
3. speech
4. clinical extraction
5. semantic matching
6. triage
7. document upload/OCR
8. evidence
9. vitals
10. routing/queue
11. hospital services/map
12. emergency
13. audit/consent

Do not couple UI widgets directly to HTTP calls.

## Phase 5 — AI integration
Use cloud AI through backend APIs. Keep API keys and provider credentials out of Flutter.

Pipeline:
```text
Audio
 → speech-to-text
 → language normalization
 → clinical information extraction
 → embedding/semantic matching
 → structured clinical facts
 → deterministic validation
 → triage rules
 → clinician-facing payload
```

AI must not independently make a final medical diagnosis or emergency decision.

## Phase 6 — Hardware/platform integration
Add and test:
- microphone
- camera
- location
- notifications
- secure storage
- scanner/printer integration if available
- optional Bluetooth/medical peripherals

Keep platform-specific implementation behind service interfaces.

## Phase 7 — Doctor integration
The patient app submits a stable structured payload.
The doctor dashboard:
- sees queue
- sees structured summary
- sees source evidence
- corrects/reconciles extracted information
- approves/exports according to backend policy

## Phase 8 — Real-device testing
Test on:
- Android phone/tablet
- iPhone/iPad where available
- poor network
- no network
- microphone denied
- camera denied
- location denied
- interrupted app
- rotation/resizing where supported
- long text
- multilingual input
- low-end hardware

## Phase 9 — Release builds
Produce:
- Android debug APK
- Android release build
- iOS build/archive when signing environment is available

---

# 3. TWO-DEVELOPER OWNERSHIP

## DEVELOPER 1 — THOUFIKUR
**Primary ownership: Flutter patient application**

Build and own:
- Flutter architecture
- design system
- all patient screens
- navigation
- state machine
- localization
- microphone/camera/location UI integration
- document capture UI
- OCR review/evidence UI
- vitals UI
- AYUSH UI
- queue/token UI
- hospital services/map UI
- emergency UI
- IVR entry/information UI where represented in the app
- offline UI
- permissions
- mock repositories
- widget/integration tests for patient flow
- API client integration against Developer 2 contracts

Do NOT:
- put cloud AI keys in Flutter
- implement clinical diagnosis logic in widgets
- invent backend payloads
- duplicate backend business rules

## DEVELOPER 2 — MUBASHIR
**Primary ownership: backend + AI + integration**

Build and own:
- backend API
- authentication/session handling
- patient/session persistence
- speech provider integration
- multilingual processing
- clinical extraction
- embedding/semantic matching
- OCR/document processing
- evidence mapping
- deterministic triage engine
- vitals ingestion
- department/queue services
- hospital service/map data APIs
- emergency/ambulance orchestration interface
- IVR/telephony backend
- doctor dashboard API
- audit/security controls
- database
- integration tests

Do NOT:
- redesign the Flutter patient UI
- embed provider secrets in the mobile app
- return undocumented payloads

---

# 4. SHARED CONTRACT

Developer 1 depends on stable API contracts, not implementation details.

Minimum shared objects:

```text
Session
PatientReference
Consent
IdentityResult
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
```

Every response should include, where appropriate:
- success/failure status
- stable identifier
- timestamp
- user/session correlation identifier
- structured error code
- human-readable message
- data payload

Never make Flutter parse arbitrary prose when a typed JSON contract can be used.

---

# 5. AI + MODEL POLICY

Use provider/model configuration on the backend so models can be changed without rebuilding Flutter.

The backend should select models according to:
- language
- task
- latency
- cost
- medical-domain suitability
- multilingual quality
- privacy/data policy

Recommended architecture:

```text
ASR model/service
        ↓
clinical language processing
        ↓
medical/multilingual embedding model
        ↓
semantic retrieval / terminology mapping
        ↓
structured extraction model
        ↓
deterministic clinical validation
        ↓
triage rules
```

Exact model names must be configured from the current provider documentation at implementation time rather than hard-coded into the mobile UI. If the team has already selected a provider/model, expose it through backend configuration.

### Why embeddings are required
Do not use exact string matching for clinical terminology.

Example:
```text
"seene mein jalan"
"acidity"
"burning in upper abdomen"
"epigastric burning"
```
may refer to related concepts despite very different strings.

Use embeddings/semantic matching for candidate retrieval, then validate the result using clinical terminology/rules. Do not treat embedding similarity alone as clinical truth.

---

# 6. TRIAGE SAFETY FLOW

```text
Patient input
  ↓
ASR/transcript
  ↓
structured candidate facts
  ↓
red-flag rule engine
  ↓
risk classification
```

The rule engine must be deterministic and auditable.

If a configured red flag is detected:
1. create high-priority event
2. send to authorized clinical terminal
3. display simple emergency instruction
4. provide configured hospital escalation
5. stop normal queue progression where policy requires

The AI may extract/categorize information, but it must not be the sole authority for emergency disposition.

---

# 7. DOCUMENT/OCR FLOW

```text
Camera
 ↓
capture
 ↓
quality check
 ↓
upload
 ↓
OCR/document understanding
 ↓
structured fields
 ↓
confidence
 ↓
source bounding/evidence reference
 ↓
doctor dashboard
```

Every important extracted fact should be traceable to:
- source document
- page/image
- region/bounding box if supported
- extraction confidence

Patient UI should not force complex medical corrections.

---

# 8. OFFLINE-FIRST BEHAVIOR

Offline-capable:
- navigation
- UI
- localization
- consent display
- local draft/session state
- mock/demo mode
- basic validation
- previously bundled hospital static information where permitted

Network-dependent:
- cloud speech
- cloud AI
- semantic retrieval
- OCR backend
- ABHA/ABDM
- queue synchronization
- live map/routing
- ambulance dispatch
- doctor dashboard synchronization

If network is unavailable:
- clearly explain what cannot continue
- preserve safe local progress where possible
- never silently lose patient-entered information
- do not pretend cloud AI succeeded

---

# 9. TELEPHONE / IVR BACKUP

The IVR is a secondary access channel for people who cannot use the app/kiosk.

```text
Hospital phone number
 ↓
language selection via keypad
 ↓
patient identification / minimal details
 ↓
voice or keypad answers
 ↓
telephony ASR / DTMF
 ↓
same backend intake schema
 ↓
same semantic extraction
 ↓
same deterministic triage
 ↓
same queue/clinical payload
```

The mobile app and IVR must converge on the same backend data model. Do not build two unrelated clinical workflows.

---

# 10. HOSPITAL MAP + EMERGENCY

Hospital services:
- departments
- counters
- labs/pharmacy where configured
- directions
- queue information

Emergency:
```text
SOS
 ↓
confirm emergency action
 ↓
location permission / manual location fallback
 ↓
backend emergency request
 ↓
configured ambulance/hospital workflow
 ↓
status + ETA if provider supports it
```

Never expose fake ambulance ETA or pretend dispatch succeeded in demo code. Mock mode must label simulated states.

---

# 11. TEST GATES

A phase is not complete until:

### UI gate
- all screens compile
- navigation works
- no overflow
- no inaccessible controls
- loading/error/offline states exist

### Functional gate
- complete mock journey works from beginning to end
- session reset clears sensitive data
- back navigation does not corrupt state

### Integration gate
- API contracts match
- errors map to user-safe messages
- retries are controlled
- no secrets in client

### Safety gate
- red-flag path is deterministic
- emergency state cannot silently fall back to normal flow
- extracted facts retain evidence where required

### Device gate
- Android tested
- iOS tested
- permissions tested
- camera/mic/location failure tested

---

# 12. AI VIBE-CODING RULES

When giving this document to a coding AI:

1. Read the whole document before coding.
2. Read the companion UI prompt before changing UI.
3. Inspect existing files.
4. State the files you plan to change.
5. Implement one phase at a time.
6. Run formatter/analyzer/tests after each phase.
7. Fix errors before continuing.
8. Never replace the architecture just because a simpler implementation is faster.
9. Never create fake production integrations disguised as real integrations.
10. Use mock services only when clearly isolated.
11. Keep business logic out of widgets.
12. Keep secrets out of source control.
13. Preserve the exact patient flow.
14. Do not remove a required feature.
15. Do not add product features without approval.

---

# 13. EXECUTION CHECKLIST

```text
[ ] Inspect repository
[ ] Confirm Flutter SDK/project
[ ] Create/verify architecture
[ ] Create theme
[ ] Create localization
[ ] Create router
[ ] Create state machine
[ ] Create reusable components
[ ] Build Screen 01–24
[ ] Build error/loading/offline states
[ ] Add mock repositories
[ ] Verify complete mock flow
[ ] Connect backend APIs
[ ] Connect speech
[ ] Connect semantic matching
[ ] Connect extraction
[ ] Connect triage
[ ] Connect OCR/evidence
[ ] Connect vitals
[ ] Connect routing/queue
[ ] Connect hospital services/map
[ ] Connect emergency
[ ] Connect secure session reset
[ ] Test Android
[ ] Test iOS
[ ] Test poor/no network
[ ] Test permissions
[ ] Test multilingual flow
[ ] Test safety paths
[ ] Produce release builds
```

---

# 14. DO NOT CHANGE THESE PRODUCT PRINCIPLES

- Flutter is the application implementation technology.
- Figma is optional for design/prototyping, not required for runtime.
- Android and iOS share the Flutter codebase.
- Cloud AI is accessed through backend services.
- Patient interaction is voice/tap/scan-first.
- Patient is not a clinical data editor.
- Doctor performs clinical reconciliation.
- OCR facts must retain evidence where possible.
- Semantic matching is preferred over brittle exact-string matching.
- Triage uses deterministic, auditable rules.
- IVR is the backup channel.
- Offline behavior must be explicit.
- No fake success states in production integration.
- No secret keys in Flutter.
- No unnecessary features.

---

# 15. SOURCE MATERIAL INCLUDED FOR IMPLEMENTATION

The detailed existing technical definitions below remain the reference for the corresponding areas:

# 4. FLUTTER TECH STACK

## 4.1 Required

```text
Flutter
Dart
Material 3
Riverpod
go_router
Freezed / json_serializable where useful
Dio
flutter_secure_storage
shared_preferences or Hive/Isar for local state
intl
permission_handler
camera
image_picker
speech/audio packages as appropriate
```

Choose maintained packages and verify current compatibility before adding them.

## 4.2 State management

Use **Riverpod**.

Separate:

```text
UI state
Domain state
Repository state
API state
Local persistence
```

Do not put business logic inside widgets.

## 4.3 Navigation

Use `go_router`.

Use named routes and route guards.

Example:

```text
/welcome
/language
/consent
/identity
/care-stream
/voice-intake
/conversation
/processing
/summary
/triage
/documents
/document-capture
/ocr-review
/vitals
/queue
/services
/map
/emergency
/ambulance
/complete
```

---

# 6. APPLICATION STATE MACHINE

The patient flow must behave like a state machine.

```text
WELCOME
  ↓
LANGUAGE_SELECTED
  ↓
CONSENT_ACCEPTED
  ↓
IDENTITY_OPTION
  ├── ABHA
  ├── MOBILE
  └── SKIP
  ↓
CARE_STREAM
  ↓
VOICE/TEXT_INTAKE
  ↓
FOLLOW_UP_CONVERSATION
  ↓
AI_PROCESSING
  ↓
STRUCTURED_SUMMARY
  ├── NORMAL → DOCUMENTS/VITALS
  └── RED_FLAG → TRIAGE
  ↓
DOCUMENT_CAPTURE
  ↓
OCR_PROCESSING
  ↓
EVIDENCE_READY
  ↓
VITALS (when available)
  ↓
ROUTING/QUEUE
  ↓
COMPLETION
  ↓
RESET
```

At every stage:

```text
Loading
Success
Retry
Network error
Permission denied
Offline
Timeout
Cancel
```

must be represented.

---

# 12. BACKEND API CONTRACT

Flutter should communicate through typed repositories.

Example endpoints:

```text
POST /sessions
POST /sessions/{id}/consent
POST /sessions/{id}/identity
POST /sessions/{id}/messages
POST /sessions/{id}/audio
POST /sessions/{id}/documents
POST /sessions/{id}/triage
POST /sessions/{id}/vitals
GET  /sessions/{id}
GET  /queue
GET  /hospital/services
GET  /hospital/map
POST /emergency/request
```

Actual routes can differ, but the contract must be documented before integration.

---

# 13. CORE DATA MODEL

Patient session:

```json
{
  "sessionId": "string",
  "language": "ta-IN",
  "consent": true,
  "identity": {
    "type": "abha|mobile|anonymous",
    "reference": "string"
  },
  "chiefComplaint": {},
  "conversation": [],
  "triage": {},
  "documents": [],
  "vitals": [],
  "ayushProfile": {},
  "queue": {},
  "status": "string"
}
```

Clinical fact:

```json
{
  "id": "string",
  "label": "HbA1c",
  "value": "8.4",
  "unit": "%",
  "source": {
    "type": "ocr",
    "documentId": "string",
    "page": 1,
    "region": {}
  },
  "confidence": 0.0,
  "verifiedByDoctor": false
}
```

Never allow unsupported AI output to silently become verified clinical truth.

---

# 14. OFFLINE-FIRST BEHAVIOR

Offline does NOT mean every cloud AI feature can magically continue.

Clearly separate:

## Can work locally

- UI navigation
- language selection
- cached hospital information
- local session state
- draft answers
- local validation
- some device operations
- previously cached static content

## Requires backend/network

- cloud speech recognition
- cloud LLM processing
- cloud embeddings
- server OCR
- ABDM services
- live queue
- live hospital data
- ambulance dispatch
- doctor dashboard synchronization

When offline:

```text
Connection unavailable.

Your temporary information is stored locally while possible.

Some services are unavailable until connection returns.
```

Do not fake successful server submission.

---

# 15. SECURITY

Never put:

```text
API keys
secret tokens
service credentials
```

inside Flutter source code.

Use:

```text
HTTPS
secure token storage
short-lived authentication tokens
server-side secrets
role-based access
audit logging
encrypted storage where appropriate
```

Sensitive data should have defined:

```text
retention
deletion
access
audit
backup
recovery
```

policies.

---

# 16. PERMISSIONS

Request permissions contextually.

## Microphone

Before voice capture.

## Camera

Before QR/document capture.

## Location

Only when hospital navigation/emergency location requires it.

## Notifications

Only when the application genuinely needs them.

If denied, provide a functional fallback wherever possible.

---

# 22. TESTING

## Unit tests

Test:

- validators
- state transitions
- triage rule adapters
- JSON parsing
- repository behavior
- route guards

## Widget tests

Test:

- button actions
- language selection
- microphone state
- confirmation
- error state
- responsive layouts

## Integration tests

Test:

```text
welcome → language → consent → identity → intake
```

and:

```text
intake → processing → triage → completion
```

and:

```text
documents → OCR → evidence
```

## Device testing

Android:

- microphone
- camera
- permissions
- screen sizes
- orientation
- audio

iOS:

- microphone
- camera
- permissions
- audio session behavior
- screen sizes

---

# 24. INTEGRATION CONTRACT BETWEEN BOTH DEVELOPERS

Developer 1 should NEVER depend on unfinished AI services to build UI.

Developer 2 should provide:

```text
API contract
request examples
response examples
error codes
authentication method
mock JSON
```

Developer 1 should implement repository interfaces.

Example:

```text
AIRepository
DocumentRepository
SessionRepository
QueueRepository
EmergencyRepository
HospitalRepository
```

Then:

```text
MockRepository
       ↓
RealRepository
```

can be swapped without rebuilding the UI.

---

# 25. DOCTOR DASHBOARD REQUIREMENTS

The doctor dashboard is a separate web application.

Main structure:

```text
Doctor Header
        ↓
Queue
        ↓
Selected Patient
        ↓
Clinical Summary
        ↓
Patient-reported information
        ↓
AI-structured information
        ↓
AYUSH profile
        ↓
Vitals
        ↓
Document timeline
        ↓
OCR facts
        ↓
Source evidence
        ↓
Triage alerts
        ↓
Doctor verification
```

Actions:

```text
EDIT
DISMISS
VERIFY
SEND TO EMR/FHIR
```

Doctor must be able to distinguish source and verification status.

---

# 27. AI MODEL SELECTION POLICY

Do NOT permanently hardcode a model name into Flutter.

Use backend configuration:

```text
ASR_MODEL=
EMBEDDING_MODEL=
LLM_MODEL=
OCR_ENGINE=
TTS_ENGINE=
```

The final models must be selected based on:

```text
language coverage
clinical-domain performance
latency
cost
API availability
privacy
licensing
Indian-language performance
accuracy
hardware/cloud requirements
```

For multilingual semantic matching, prefer a multilingual embedding model and benchmark it on actual project phrases.

For speech, choose a multilingual ASR system that performs well on the project's target Indian languages and accents.

For OCR, use a document OCR pipeline capable of handling:

- printed text
- low-quality scans
- prescriptions
- handwriting where supported

Do not promise reliable handwriting extraction without testing it.

---

# 29. PRIVACY ON PUBLIC KIOSKS

The application must assume that other people may be standing nearby.

Therefore:

- do not display full sensitive information unnecessarily
- automatically reset after completion
- clear temporary state
- avoid long medical text on patient screens
- provide audio carefully
- avoid exposing identifiers
- do not leave documents visible after completion

---

# 30. AI VIBE-CODING EXECUTION METHOD

When using an AI coding assistant, do NOT ask it to generate the whole application blindly in one step.

Use this order:

```text
PHASE 1
Read this specification.

PHASE 2
Inspect existing Flutter project.

PHASE 3
Create architecture and theme.

PHASE 4
Create reusable components.

PHASE 5
Implement patient flow.

PHASE 6
Run analyzer/tests.

PHASE 7
Fix errors.

PHASE 8
Implement device permissions.

PHASE 9
Implement mock repositories.

PHASE 10
Connect backend contracts.

PHASE 11
Test offline/error states.

PHASE 12
Polish animations/accessibility.

PHASE 13
Build Android.

PHASE 14
Build iOS.
```

Never allow an AI coding assistant to replace working files blindly without inspecting the existing project.

---

---

# 16. FINAL COMMAND TO THE CODING AI

**Read this entire file and the companion UI master prompt first. Then inspect the repository. Do not start by generating random screens. Follow the phase order, preserve the exact MediKiosk logic, implement the complete Flutter Android+iOS patient application in mock mode first, verify the complete flow, and only then connect the backend contracts. After every phase, run analysis/tests and fix all errors before moving forward.**
