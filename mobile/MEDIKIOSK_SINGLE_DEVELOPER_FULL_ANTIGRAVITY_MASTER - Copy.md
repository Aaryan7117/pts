# MEDIKIOSK — SINGLE-DEVELOPER MASTER IMPLEMENTATION & ANTIGRAVITY PROMPT
## Complete Product Workflow + Technical Architecture + UI/UX + AI/OCR/IVR + Backend Integration + Testing + Definition of Done

> **Document purpose**
>
> This is the implementation master document for **one developer** responsible for taking the existing MediKiosk backend/repository and completing the full product integration.
>
> This is **not a generic Flutter prompt** and it is **not a Figma-only design document**.
>
> The developer must use this document together with the existing repository, the existing backend specification files, `MEDIKIOSK_ANDROID_DESIGN_SPEC.md`, and the existing implementation as the source of truth.
>
> **Critical rule:** do not invent functionality that is not supported by the repository/specification. If a required capability is described in the architecture but is not implemented in code, mark it as `PLANNED / NOT IMPLEMENTED` and build the correct integration boundary or mock only where explicitly permitted.

---

# 1. EXECUTIVE MISSION

Build the complete **MediKiosk AI-powered clinical history and pre-consultation platform** as one coherent production-style prototype.

The system is a **kiosk-first, patient-facing clinical intake system** with:

1. Voice + touch conversational history taking.
2. Multilingual patient interaction.
3. Adaptive clinical questioning using the SOCRATES structure.
4. AYUSH-specific Dashavidha Pariksha capture.
5. Deterministic red-flag detection and escalation.
6. Medical document capture and OCR.
7. Structured extraction from prescriptions/lab reports/discharge summaries.
8. Evidence-linked clinical facts.
9. Temporal medication/history tracking.
10. Contradiction detection between patient statements and documents.
11. Proactive clinical-gap detection.
12. Explain-back verification.
13. Vitals capture.
14. Clinical summary generation.
15. Queue intelligence.
16. Doctor dashboard.
17. Hospital services/map workflow.
18. Emergency/panic workflow.
19. Patient dashboard where specified.
20. ABDM/FHIR-ready routing.
21. Telephone/IVR as a **secondary backup channel**, especially for elderly/basic-phone users.
22. Offline/edge-first resilience.
23. Strong session privacy and automatic purge.

The core principle is:

```text
PATIENT
  |
  +--> KIOSK / PRIMARY CHANNEL
  |
  +--> TELEPHONE IVR / BACKUP CHANNEL
  |
  +--> PATIENT WEB DASHBOARD / SECONDARY CHANNEL
          |
          v
      SAME BACKEND
          |
          +--> Clinical Session Engine
          +--> AI Gateway
          +--> OCR / Document AI
          +--> Deterministic Safety Engine
          +--> Queue / Routing
          +--> Consent / Audit
          +--> FHIR / ABDM boundary
          |
          v
      DOCTOR DASHBOARD
```

The kiosk and IVR must **not become two independent clinical systems**.

---

# 2. SOURCE-OF-TRUTH HIERARCHY

Before changing code, read and reconcile the available project material in this order:

| Priority | Source | How to use it |
|---|---|---|
| 1 | Official problem statement / SIH26047 requirements | Defines what MediKiosk must solve |
| 2 | Existing backend repository and working code | Defines what is actually implemented |
| 3 | `MEDIKIOSK_ANDROID_DESIGN_SPEC.md` | Defines detailed patient UI |
| 4 | Existing MediKiosk architecture / development-flow documents | Defines workflow, safety, AI, data architecture |
| 5 | Existing technical-stack documents | Defines intended AI/edge/cloud strategy |
| 6 | Existing tests/configuration/schema files | Defines actual contracts |
| 7 | This document | Provides the single-developer execution order and Antigravity operating rules |

### Reconciliation rule

Never silently replace an existing project decision.

If two documents conflict:

```text
Official requirement
    >
Working repository contract
    >
Latest finalized architecture
    >
Older draft
    >
Developer assumption
```

When uncertain, inspect the actual code and document the discrepancy in:

```text
IMPLEMENTATION_AUDIT.md
```

---

# 3. PRODUCT POSITIONING

MediKiosk is **not**:

- an autonomous doctor
- an autonomous diagnosis engine
- a generic chatbot
- an LLM wrapper
- a replacement for a clinician
- a consumer symptom-checker clone

MediKiosk is:

> A pre-consultation clinical information capture and intelligence layer that gathers structured patient history, digitizes prior records, detects safety signals, and prepares evidence-linked information for clinician review.

The doctor remains responsible for clinical interpretation and confirmation.

---

# 4. PRIMARY AND SECONDARY CHANNELS

## 4.1 Primary: Physical Kiosk

The kiosk is the main patient-entry point.

The intended patient should not need:

- a smartphone
- an existing app
- prior technical knowledge
- literacy
- a stable internet connection

The kiosk must support:

- large touch controls
- voice interaction
- audio instructions
- camera/document capture
- multilingual UI
- accessibility
- privacy reset
- offline/edge behavior

## 4.2 Secondary: Telephone / IVR

The IVR is **backup**, not the main UI.

Target:

- elderly users
- basic-phone users
- users unable to operate a kiosk
- users who cannot use smartphone apps

Flow:

```text
Hospital phone number
        ↓
IVR greeting
        ↓
Language selection
        ↓
Consent / privacy notice
        ↓
Patient identification
        ↓
Voice or DTMF responses
        ↓
Speech recognition / intent extraction
        ↓
Same clinical interview engine
        ↓
Same red-flag engine
        ↓
Same clinical session schema
        ↓
Same queue / doctor workflow
```

The IVR must produce the same type of structured clinical session as kiosk intake.

### Important implementation distinction

The existing backend may contain **voice-session / call-session APIs**, but that does not automatically prove that a real telephone carrier/PSTN integration exists.

The developer must audit this.

Use status labels:

```text
IMPLEMENTED
PARTIALLY IMPLEMENTED
MOCKED
INTEGRATION READY
NOT IMPLEMENTED
```

Never claim PSTN/telephony is live unless an actual telephony provider integration has been tested.

---

# 5. COMPLETE PATIENT JOURNEY

## Master journey

```text
01 Welcome
   ↓
02 Language
   ↓
03 Consent
   ↓
04 Identify
   ↓
05 Returning patient check
   ↓
06 Care / OPD selection
   ↓
07 Conversational intake
   ↓
08 Adaptive follow-up
   ↓
09 AYUSH branch when applicable
   ↓
10 Safety / red-flag evaluation
   ↓
11 Document scan
   ↓
12 OCR processing
   ↓
13 Evidence review
   ↓
14 Vitals
   ↓
15 Clinical gap detection
   ↓
16 Explain-back
   ↓
17 Summary
   ↓
18 Queue / department routing
   ↓
19 FHIR / ABDM / HIS boundary
   ↓
20 Token / queue status
   ↓
21 Hospital services / map
   ↓
22 Emergency if triggered
   ↓
23 Completion
   ↓
24 Privacy reset
```

---

# 6. UI/UX DESIGN SYSTEM

## 6.1 Design language

Use:

- modern healthcare visual language
- calm and trustworthy presentation
- high contrast
- large controls
- minimal clutter
- clear hierarchy
- restrained rounded cards
- subtle shadows
- subtle animation
- no excessive glassmorphism
- no decorative UI that distracts from the patient task

The interface must look like a serious healthcare product, not a gaming app or generic AI dashboard.

## 6.2 Color system

Use the design-spec tokens as the canonical source.

Important known tokens include:

| Token | Value / intent |
|---|---|
| `mdBrandPrimary` | `#1E3A8A` |
| `mdTextPrimary` | `#0F172A` |
| `mdTextMuted` | `#475569` |
| `mdSurface` | `#FFFFFF` |
| `mdCanvas` | `#F8FAFC` |
| `mdTriageRed` | `#991B1B` |
| `mdAyushGreen` | `#065F46` |
| `mdBorderSelected` | `#1E3A8A` |

Do not introduce a random new color palette.

## 6.3 Accessibility

The design specification targets strong WCAG contrast, including AAA-level contrast for the specified core combinations.

Critical rules:

- never communicate status through color alone
- pair colored states with text
- pair states with semantic icons
- large touch targets
- readable typography
- clear focus/selected states
- no tiny controls
- no gesture-only actions
- voice alternative for clinical questions
- touch alternative for every interview question

---

# 7. MULTILINGUAL ARCHITECTURE

Initial UI specification includes:

1. English (`en`)
2. Hindi (`hi`)
3. Tamil (`ta`)
4. Telugu (`te`)
5. Additional supported languages only after verifying the actual ASR/TTS pipeline.

Do not claim universal Indian-language support.

Every patient-facing text element must be localization-ready.

The language selected by the patient must flow into:

```text
UI language
      +
ASR language
      +
TTS language
      +
clinical normalization context
      +
explain-back language
```

Mixed-language speech should be handled only if the actual backend supports it.

---

# 8. PATIENT UI SCREEN SPECIFICATION

The following screens are the required patient-facing structure.

---

## SCREEN 01 — WELCOME

Route:

```text
/welcome
```

Purpose:

Immediately explain what MediKiosk does.

Layout:

```text
HEADER
MediKiosk logo
Hospital name
Language shortcut
Help

CENTER
Medical/health hero
Welcome to MediKiosk
"Let's gather your health details before you see your doctor."

BOTTOM
[ START ]
[ Listen to Instructions ]
[ Need Staff Assistance? ]
```

Behavior:

- START → language
- Listen → TTS/audio instructions
- Help → assistance flow

Do not use a small START button.

---

## SCREEN 02 — LANGUAGE SELECTION

Route:

```text
/language
```

Display:

- large language cards
- native-language name
- optional audio preview
- selected state

Example:

```text
English
हिन्दी
தமிழ்
తెలుగు
```

After selection:

```text
save locale
configure voice pipeline
continue → consent
```

---

## SCREEN 03 — CONSENT

Route:

```text
/consent
```

Show:

- why information is collected
- what will be processed
- voice/document usage
- clinical review notice
- privacy notice
- consent status

Audio explanation must be available.

Controls:

```text
[ Listen ]
[ I Agree ]
[ I Don't Agree ]
```

Do not represent consent as merely a checkbox.

The system should preserve a consent artifact/status where supported.

---

## SCREEN 04 — IDENTIFICATION

Route:

```text
/identify
```

Support the identification methods defined by the backend/spec:

- ABHA/health identifier path if configured
- existing patient lookup if supported
- manual fallback
- new registration path where supported

Do not make Aadhaar/fingerprint a mandatory dependency unless explicitly supported and required.

---

## SCREEN 05 — RETURNING PATIENT FAST PATH

If an existing patient is found:

```text
Welcome back
We found your previous record.
```

Show a concise confirmation.

Returning-patient flow should prioritize:

```text
What changed since your last visit?
```

instead of unnecessarily repeating the entire history.

This supports the changes-first architecture.

---

## SCREEN 06 — CARE / OPD SELECTION

Show:

- department
- reason for visit
- new complaint / follow-up
- AYUSH/allopathic pathway where configured

The chosen pathway controls later questions.

---

## SCREEN 07 — CONVERSATIONAL INTAKE

This is one of the most important screens.

UI:

```text
Top:
progress
language
connection state

Center:
AI/avatar indicator
current question
large text

Middle:
voice waveform
"Tap and speak"

Bottom:
touch answer options
[Repeat]
[Skip if allowed]
[Go back]
[Need help]
```

Every question must support:

```text
VOICE
OR
TOUCH
```

Never force typing for a clinical interview.

---

## SCREEN 08 — ACTIVE VOICE INTAKE

Show:

- large microphone
- audio visualizer
- live transcript where appropriate
- current recognized phrase
- listening/processing state
- repeat button
- stop button

States:

```text
Listening
Processing
Understood
Didn't catch that
Offline / retry
```

Do not display unverified AI text as confirmed clinical fact.

---

# 9. SOCRATES ADAPTIVE QUESTIONING

The standard complaint interview should capture:

| Component | Meaning |
|---|---|
| S | Site |
| O | Onset |
| C | Character |
| R | Radiation |
| A | Associations |
| T | Time course |
| E | Exacerbating/relieving factors |
| S | Severity |

The question graph must be deterministic.

Architecture:

```text
Chief complaint
     ↓
question graph
     ↓
patient answer
     ↓
structured candidate fact
     ↓
next applicable question
     ↓
clinical gap check
     ↓
complete / continue
```

The LLM may assist language understanding, but the clinical question graph must not become an uncontrolled free-form autonomous diagnostic conversation.

---

# 10. AYUSH MODE

AYUSH is a first-class workflow.

Capture the specified Dashavidha Pariksha fields:

| Field | Meaning |
|---|---|
| Prakriti | Constitution |
| Vikriti | Current imbalance/change |
| Sara | Tissue quality |
| Samhanana | Body build |
| Pramana | Measurements/proportions |
| Satmya | Suitability/tolerance |
| Sattva | Mental/psychological strength |
| Ahara Shakti | Digestive/appetite capacity |
| Vyayama Shakti | Exercise/physical capacity |
| Vaya | Age-related stage |

Also preserve the specified additional blocks:

- Ahara-Vihara
- Agni
- Koshtha
- Nidana
- Samprapti

These must be structured fields, not a generic notes string.

Where the architecture requires clinician examination such as Nadi/Jihva, represent it as a pending clinician/physical examination item rather than inventing a patient answer.

---

# 11. RED-FLAG / SAFETY FLOW

Architecture:

```text
Patient answer
    ↓
transcript / structured candidate
    ↓
deterministic safety rules
    ↓
red-flag event?
    ├── NO → continue
    └── YES
          ↓
     priority alert
          ↓
     emergency instruction
          ↓
     authorized staff/clinical terminal
          ↓
     configured escalation
```

Examples specified in the architecture include:

- acute chest pain with dyspnoea
- stroke-like symptoms

The exact clinical thresholds/rules must be sourced from the project-approved clinical rule set.

### Never do this

```text
LLM says emergency
→ immediately declare diagnosis
```

Instead:

```text
deterministic rule
+
structured evidence
+
configured clinical policy
```

The LLM is not the sole emergency authority.

---

# 12. DOCUMENT SCAN FLOW

## SCREEN 09 — DOCUMENT CAPTURE

Allow:

- camera capture
- retake
- multiple documents
- prescription
- laboratory report
- discharge summary
- other supported medical document

UI:

```text
document frame
quality guidance
flash
capture
retake
add another
continue
```

Quality checks should detect obvious problems such as:

- blur
- insufficient framing
- severe glare
- unreadable image

---

# 13. OCR / DOCUMENT AI

Pipeline:

```text
Image
 ↓
quality check
 ↓
upload / local processing
 ↓
OCR
 ↓
document classification
 ↓
entity extraction
 ↓
normalization
 ↓
confidence
 ↓
evidence reference
 ↓
clinical validation
 ↓
doctor dashboard
```

Extract where supported:

- medications
- dosage
- investigation values
- reference ranges
- diagnoses
- procedures
- document date
- provider information

Printed text should be prioritized.

Handwritten OCR must include human-review/low-confidence handling.

Never fabricate an OCR value.

---

# 14. EVIDENCE-LINKED CLINICAL FACTS

Every important extracted fact should preserve provenance where supported:

```text
Fact
 ↓
source type
 ↓
document
 ↓
page/image
 ↓
region/bounding box if available
 ↓
confidence
 ↓
verification status
```

Doctor UI should distinguish:

```text
PATIENT SAID
AI EXTRACTED
OCR EXTRACTED
SYSTEM FLAGGED
DOCTOR VERIFIED
```

Core principle:

> No evidence → do not silently promote the item to a verified clinical fact.

---

# 15. MEDICATION TIMELINE

Medication history must not be treated as one static list.

Where the schema supports it, preserve:

```text
medication
dose
frequency
route
valid_from
valid_until
source
confidence
verification
```

This allows the doctor to see:

```text
OLD
 ↓
CURRENT
 ↓
STOPPED / CHANGED
 ↓
PATIENT REPORTS ACTUAL USE
```

This is especially important when a prescription and the patient's current statement disagree.

---

# 16. CONTRADICTION RESOLUTION

Example:

```text
Document:
Metformin 500 mg

Patient:
"I stopped taking it two months ago."
```

Do not overwrite one with the other.

Represent:

```text
Document evidence:
Metformin 500 mg
        +
Patient statement:
stopped two months ago
        ↓
Temporal contradiction / reconciliation required
```

Doctor should see both sources.

---

# 17. SEMANTIC NORMALIZATION

Do not rely solely on:

```text
exact string matching
Levenshtein distance
```

Example:

```text
"seene mein jalan"
"acidity"
"burning in upper abdomen"
"epigastric burning"
```

can be semantically related.

Architecture:

```text
patient phrase
 ↓
language normalization
 ↓
embedding
 ↓
semantic retrieval
 ↓
candidate concepts
 ↓
deterministic validation
 ↓
confidence threshold
 ↓
direct map OR explain-back
```

Embeddings assist retrieval.

They do not independently diagnose.

The technical specification describes a multilingual ONNX sentence-transformer/embedding approach and confidence-based explain-back behavior. Preserve the project's chosen thresholds/configuration in backend configuration rather than scattering them through UI code.

---

# 18. EXPLAIN-BACK VERIFICATION

When confidence is uncertain:

```text
System:
"I understood that you have burning in the upper abdomen. Is that correct?"

[ YES ]
[ NO, SAY AGAIN ]
```

For low-literacy users:

- audio explanation
- large visual controls
- minimal medical jargon

This is a hard safety mechanism, not decorative UX.

---

# 19. PROACTIVE CLINICAL GAP DETECTION

The system should identify missing important information based on the selected complaint pathway.

Example:

```text
Complaint:
abdominal pain

Captured:
site
onset
severity

Missing:
duration
vomiting
bleeding
food relation
etc.
```

The system should ask only relevant missing questions.

Do not turn gap detection into diagnosis.

---

# 20. VITALS FLOW

Where hardware/API support exists, capture:

- blood pressure
- pulse
- SpO2
- temperature
- weight/height or configured measurements

Every value should carry:

```text
value
unit
timestamp
source/device
confidence/status
```

If hardware is unavailable:

```text
manual entry / unavailable
```

Do not fake live sensor readings.

---

# 21. SUMMARY FLOW

The patient-facing summary should be simple.

The clinician-facing summary should be structured.

Recommended clinical ordering:

```text
Chief Complaint
HPI
Relevant history
Medications
Allergies
Investigations
Vitals
AYUSH history
Clinical gaps
Safety flags
Evidence references
```

The summary generator must assemble facts from validated structured data.

LLM-generated prose must not invent facts.

---

# 22. BILINGUAL / MULTILINGUAL SUMMARY

Patient:

```text
local language
```

Doctor:

```text
English
+
patient language where useful
```

The doctor must be able to distinguish translated content from original patient statements where relevant.

---

# 23. QUEUE INTELLIGENCE

After intake:

```text
clinical session
      ↓
department
      ↓
priority
      ↓
queue
      ↓
doctor dashboard
```

The system can assist prioritization using configured rules.

Do not let an LLM silently reorder patients based on an opaque score.

Priority should be:

```text
deterministic / auditable
+
clinical policy
+
visible reason
```

---

# 24. DOCTOR DASHBOARD

The doctor dashboard is a first-class product surface.

## Dashboard

Show:

- current queue
- patient token
- priority
- age
- chief complaint
- red flags
- waiting time
- completion status

## Patient clinical view

Show:

```text
PATIENT
TOKEN
DEPARTMENT

CHANGES FIRST
----------------
What changed since previous visit

CHIEF COMPLAINT
----------------

HPI / SOCRATES
----------------

VITALS
----------------

MEDICATION TIMELINE
----------------

DOCUMENTS
----------------

EVIDENCE
----------------

AYUSH
----------------

CLINICAL GAPS
----------------

SAFETY FLAGS
----------------

DOCTOR ACTION
[Edit]
[Verify]
[Confirm]
[Route]
```

### Evidence presentation

Every important fact should be traceable.

Example:

```text
HbA1c 8.2%
[OCR]
[View source]
[Page 1]
[Confidence: ...]
```

---

# 25. CHANGES-FIRST DOCTOR VIEW

For returning patients, prioritize:

```text
NEW
CHANGED
STOPPED
WORSENED
MISSING
CONTRADICTORY
```

Do not make the physician read the entire historical record before seeing what changed.

---

# 26. HOSPITAL SERVICES

Provide the specified hospital-service information:

- departments
- pharmacy
- blood bank
- toilets
- counters
- configured facilities
- floor/distance
- directions

Component pattern:

```text
HospitalServiceCard
```

Use icons + text.

Do not depend on color alone.

---

# 27. HOSPITAL MAP

Flow:

```text
Hospital map
 ↓
choose destination
 ↓
show route
 ↓
floor / distance
 ↓
directions
```

If live indoor mapping is not actually implemented:

```text
DEMO / STATIC MAP
```

must be clearly distinguishable from a live routing service.

---

# 28. EMERGENCY / PANIC FLOW

Provide:

```text
SOS
 ↓
confirmation
 ↓
location permission
 ↓
emergency request
 ↓
configured hospital/ambulance path
 ↓
status
```

Location fallback:

```text
GPS
OR
manual hospital/location selection
```

Do not claim ambulance dispatch unless the real integration exists.

Do not show fake ETA as real.

---

# 29. TELEPHONE IVR BACKUP — FULL ARCHITECTURE

This is a **separate access channel**, not a Flutter page.

## IVR

```text
Hospital number
       ↓
Telephony provider
       ↓
IVR application
       ↓
Language
       ↓
Consent
       ↓
Identification
       ↓
Voice / DTMF
       ↓
ASR / intent extraction
       ↓
Clinical session engine
       ↓
SOCRATES
       ↓
AYUSH branch
       ↓
Red-flag rules
       ↓
Queue
       ↓
Doctor dashboard
```

## DTMF example

```text
Press 1 — English
Press 2 — Hindi
Press 3 — Tamil
Press 4 — Telugu
```

The exact language menu must match actual supported languages.

## IVR constraints

- telephone audio quality is lower than kiosk microphone quality
- DTMF fallback is mandatory for critical navigation
- do not assume ASR will understand everything
- allow repetition
- confirm important extracted facts
- terminate safely
- persist session ID
- avoid exposing sensitive data unnecessarily over audio

## Integration rule

Kiosk and IVR must share:

```text
ClinicalSession
ClinicalFact
Consent
RedFlagEvent
Document
QueueItem
Summary
```

or their exact repository equivalents.

---

# 30. EDGE-FIRST / CLOUD HYBRID AI ARCHITECTURE

The technical documents describe an edge-first multi-model hybrid.

Conceptual architecture:

```text
                    MEDIKIOSK CLIENT
                           |
                           v
                    BACKEND GATEWAY
                           |
              +------------+------------+
              |                         |
            ONLINE                    OFFLINE
              |                         |
              v                         v
        CLOUD ROUTING              EDGE SERVICES
              |                         |
       +------+-------+           +-----+------+
       |              |           |            |
     FAST           QUALITY      ASR       LLM/AI
     ROUTE          ROUTE        local      local
       |              |
     Groq           Gemini
```

The finalized technical material identifies:

- edge/local model path using Ollama
- Gemma/Qwen-class local models
- CPU OCR path
- cloud routing using services such as Groq/Gemini
- vendor-agnostic gateway
- deterministic core around the models

### Important

Treat exact provider/model versions as **configuration**, not UI logic.

Do not hardcode:

```text
API keys
provider secrets
model names everywhere
```

Use backend environment/configuration.

---

# 31. AI RESPONSIBILITY BOUNDARY

## AI MAY

- transcribe
- translate
- normalize language
- extract structured candidate facts
- assist semantic retrieval
- summarize validated facts
- classify documents
- extract OCR entities
- suggest relevant follow-up questions
- assist routing

## AI MUST NOT

- invent clinical facts
- invent medication dosage
- independently diagnose
- independently determine emergency disposition
- overwrite evidence
- hide uncertainty
- silently alter doctor-confirmed information

---

# 32. DETERMINISTIC CORE

The surrounding system must remain deterministic wherever safety/interoperability requires it.

Core examples:

```text
Question state machine
Clinical schema validation
Red-flag rules
Confidence thresholds
Evidence linking
Temporal logic
Queue priority rules
Session lifecycle
Consent state
FHIR structure validation
Data purge
```

The LLM is interchangeable.

The deterministic clinical data model is not.

---

# 33. FHIR / ABDM / HIS

Architecture:

```text
Validated clinical data
        ↓
FHIR R4 mapping
        ↓
FHIR validation
        ↓
ABDM sandbox boundary
        ↓
HIS/EMR adapter
```

Do not claim full production ABDM compliance unless actually validated.

Status must be one of:

```text
FHIR READY
FHIR VALIDATED
ABDM SANDBOX TESTED
ABDM PRODUCTION INTEGRATED
```

Do not use "ABDM compliant" casually.

---

# 34. BACKEND INTEGRATION

The repository already contains backend modules for important MediKiosk areas, including structures associated with:

- call/voice sessions
- doctor workflows
- documents
- encounters
- queue

The developer must inspect the actual source before writing integration code.

Do not invent endpoint names.

Create a contract table from the actual backend:

| Feature | Actual endpoint | Method | Request | Response | Auth | Status |
|---|---|---|---|---|---|---|
| Session | inspect repo | | | | | |
| Consent | inspect repo | | | | | |
| Messages | inspect repo | | | | | |
| Audio | inspect repo | | | | | |
| Documents | inspect repo | | | | | |
| Triage | inspect repo | | | | | |
| Vitals | inspect repo | | | | | |
| Queue | inspect repo | | | | | |
| Doctor | inspect repo | | | | | |
| Calls/IVR | inspect repo | | | | | |

Save this as:

```text
API_CONTRACT_AUDIT.md
```

---

# 35. FRONTEND ARCHITECTURE

The exact framework/library versions must be compatible with the existing repository.

For Flutter patient UI, use a maintainable architecture such as:

```text
lib/
├── app/
│   ├── router/
│   ├── theme/
│   ├── localization/
│   └── config/
│
├── core/
│   ├── errors/
│   ├── network/
│   ├── storage/
│   ├── permissions/
│   └── utilities/
│
├── features/
│   ├── onboarding/
│   ├── consent/
│   ├── identity/
│   ├── intake/
│   ├── ayush/
│   ├── documents/
│   ├── vitals/
│   ├── summary/
│   ├── queue/
│   ├── hospital/
│   ├── emergency/
│   └── privacy/
│
├── shared/
│   ├── widgets/
│   ├── components/
│   └── models/
│
└── main.dart
```

If the existing repository already has a different clean architecture, preserve it rather than rewriting everything.

---

# 36. STATE MANAGEMENT

Use the project's existing state-management choice if one exists.

If no state-management system exists, use one consistent solution such as Riverpod.

Do not mix:

```text
Riverpod
Provider
Bloc
GetX
setState
```

randomly throughout the project.

Use `setState` only for genuinely local ephemeral UI state.

---

# 37. NAVIGATION

Use a typed/centralized routing approach.

Routes should correspond to product states.

Example:

```text
/welcome
/language
/consent
/identify
/care
/intake
/ayush
/documents
/ocr-review
/vitals
/summary
/queue
/hospital
/emergency
/completed
```

Do not duplicate navigation logic across widgets.

Back navigation must be safe:

- do not lose patient data
- do not accidentally submit
- do not bypass consent
- do not bypass red-flag escalation

---

# 38. REPOSITORY PATTERN

UI must not directly call HTTP clients everywhere.

Use:

```text
Screen
 ↓
Controller / ViewModel
 ↓
Repository
 ↓
API client
 ↓
Backend
```

For example:

```text
IntakeRepository
DocumentRepository
QueueRepository
HospitalRepository
EmergencyRepository
```

Exact names can follow the project's conventions.

---

# 39. MOCK MODE

Mock mode is mandatory for development/demo resilience.

Mock mode may simulate:

- sample patient
- voice transcript
- OCR result
- queue
- doctor dashboard
- map
- emergency state

But every simulated feature must be labeled internally as:

```text
MOCK
DEMO
SIMULATED
```

Never mix mock data into production backend data accidentally.

---

# 40. OFFLINE-FIRST

Offline-capable:

- navigation
- localization
- consent display
- local session draft
- local validation
- demo mode
- static hospital information where permitted
- queued local operations

Network-dependent unless local edge implementation exists:

- cloud AI
- cloud ASR
- cloud OCR
- live queue synchronization
- live hospital routing
- ABDM
- live ambulance dispatch

When offline:

```text
show status
preserve state
queue safe operations
retry
never silently lose data
never pretend success
```

---

# 41. SESSION PRIVACY

The kiosk is shared between patients.

At completion or inactivity:

```text
PrivacyResetOverlay
```

Show:

```text
Session Ending for Your Privacy

10
9
8
...
```

Buttons:

```text
[Reset Immediately]
[I'm Still Here]
```

On reset:

```text
clear
- patient details
- temporary images
- temporary transcripts
- temporary clinical state
- temporary documents
- language state where required
```

Return to:

```text
/welcome
```

Do not leave previous patient's information visible.

---

# 42. SECURITY

Never commit:

```text
API keys
JWT secrets
database credentials
ABDM credentials
LLM keys
OCR keys
telephony secrets
```

Use environment/configuration.

Protect:

- data in transit
- stored session data
- document files
- audio
- authentication tokens
- audit logs

Do not log raw medical information unnecessarily.

---

# 43. WHAT THE DEVELOPER MUST NOT DO

## DO NOT

1. Delete working backend code without evidence.
2. Rewrite the backend because the frontend is inconvenient.
3. Invent API routes.
4. Invent database fields.
5. invent FHIR mappings.
6. invent clinical thresholds.
7. make the LLM the emergency decision-maker.
8. display hallucinated facts.
9. hardcode API keys.
10. claim real telephony when only call-session APIs exist.
11. claim live ambulance dispatch without integration.
12. claim live ABDM integration without sandbox evidence.
13. fake sensor readings.
14. fake OCR results as real.
15. replace evidence with LLM-generated text.
16. remove the AYUSH branch.
17. remove voice/touch dual input.
18. make typing mandatory.
19. remove elderly/basic-phone IVR architecture.
20. create a separate IVR clinical data model.
21. overuse animations.
22. use tiny text.
23. use color as the only state indicator.
24. build only static screenshots.
25. stop after the UI looks good.
26. skip `flutter analyze`.
27. skip tests.
28. modify FHIR/schema-critical files silently.
29. silently downgrade accessibility.
30. silently remove features because they are difficult.

---

# 44. WHAT THE DEVELOPER SHOULD DO

1. Inspect first.
2. Document actual repository state.
3. Freeze the API/schema contracts.
4. Build around existing backend behavior.
5. Implement patient workflow.
6. Implement doctor workflow.
7. Implement IVR integration boundary.
8. Add mock mode.
9. Add real API integration.
10. Add offline behavior.
11. Add security/privacy.
12. Test every state.
13. Test real Android hardware.
14. Test microphone/camera permissions.
15. Test network interruption.
16. Test session reset.
17. Test multilingual UI.
18. Test OCR confidence/review.
19. Test red-flag escalation.
20. Test FHIR validation where available.
21. Produce evidence and reports.

---

# 45. DEVELOPMENT PHASES

## PHASE 0 — REPOSITORY AUDIT

Before changing code:

```text
inspect:
- repository tree
- backend
- frontend
- database/schema
- environment files
- API routes
- tests
- existing docs
- existing integrations
```

Create:

```text
IMPLEMENTATION_AUDIT.md
API_CONTRACT_AUDIT.md
FEATURE_STATUS.md
```

Feature status:

| Feature | Backend | Frontend | Integration | Test | Final status |
|---|---|---|---|---|---|
| Voice | | | | | |
| Touch intake | | | | | |
| AYUSH | | | | | |
| OCR | | | | | |
| Evidence | | | | | |
| Triage | | | | | |
| Queue | | | | | |
| Doctor dashboard | | | | | |
| IVR | | | | | |
| Emergency | | | | | |
| FHIR | | | | | |
| Privacy purge | | | | | |

---

# 46. PHASE 1 — CONTRACT FREEZE

Verify:

- clinical session schema
- ClinicalFact schema
- AYUSH schema
- document schema
- consent schema
- red-flag event schema
- queue schema
- summary schema
- auth
- error format
- language codes
- status enums
- FHIR mappings

Do not redesign these casually.

If changes are required:

```text
document reason
show diff
update dependent code
run tests
```

---

# 47. PHASE 2 — APPLICATION FOUNDATION

Implement/verify:

- theme
- localization
- routing
- state management
- API client
- repository layer
- secure storage
- permissions
- connectivity detection
- mock mode
- error handling
- logging
- analytics only where appropriate and privacy-safe

Run:

```text
flutter pub get
flutter analyze
flutter test
```

---

# 48. PHASE 3 — PATIENT ONBOARDING

Implement:

```text
Welcome
Language
Consent
Identification
Returning patient
Care selection
```

Test:

- first-time patient
- returning patient
- consent rejected
- microphone denied
- camera denied
- back navigation
- language change

---

# 49. PHASE 4 — CONVERSATIONAL ENGINE

Implement:

```text
Voice
Touch
SOCRATES
Adaptive questions
Semantic normalization
Explain-back
Clinical gap detection
AYUSH branch
```

Test:

- English
- Hindi
- Tamil
- Telugu
- mixed speech where supported
- ASR error
- no speech
- low confidence
- network loss
- malformed AI response
- invalid schema response

---

# 50. PHASE 5 — SAFETY ENGINE

Implement/verify:

```text
red-flag rules
priority events
staff alert
emergency instruction
safe stop / escalation
audit event
```

The rule engine must be deterministic.

Test deliberate red-flag scenarios.

---

# 51. PHASE 6 — DOCUMENT AI

Implement:

```text
capture
quality
upload
OCR
classification
extraction
confidence
evidence
review
chronology
contradictions
medication timeline
```

Test:

- printed prescription
- lab report
- discharge summary
- multiple documents
- out-of-order documents
- low-quality image
- low-confidence extraction
- handwriting
- multilingual document

---

# 52. PHASE 7 — VITALS + SUMMARY

Implement:

```text
vitals
clinical gap view
summary
explain-back
patient confirmation
doctor-ready summary
```

Use structured templates.

Do not let free-form LLM output become the source of truth.

---

# 53. PHASE 8 — QUEUE + DOCTOR

Implement:

```text
queue
priority
doctor dashboard
changes-first view
clinical summary
evidence
documents
vitals
AYUSH
clinical gaps
verification
```

Doctor must be able to edit/confirm according to backend capabilities.

---

# 54. PHASE 9 — HOSPITAL + EMERGENCY

Implement:

```text
services
map
directions
SOS
location
emergency status
```

Clearly distinguish:

```text
LIVE
MOCK
UNAVAILABLE
```

---

# 55. PHASE 10 — IVR

First audit existing call APIs.

Then:

```text
IVR adapter
language
consent
identity
voice/DTMF
session
clinical engine
triage
queue
doctor
```

If PSTN provider is not configured:

```text
implement provider-neutral interface
implement local/mock call simulation
document production integration steps
```

Do not pretend it is live.

---

# 56. PHASE 11 — FHIR / ABDM

Implement only what the repository/project supports.

Minimum architecture:

```text
clinical model
 ↓
FHIR mapping
 ↓
validation
 ↓
sandbox integration
```

Test actual bundle validity.

---

# 57. PHASE 12 — OFFLINE + PRIVACY HARDENING

Test:

- network lost before interview
- network lost during interview
- network lost during upload
- network returns
- retry
- duplicate submission
- app restart
- kiosk timeout
- privacy reset
- second patient begins

Verify no previous patient information leaks.

---

# 58. PHASE 13 — FINAL TESTING

Required test groups:

### UI

- navigation
- responsiveness
- accessibility
- typography
- touch targets
- localization

### Voice

- microphone
- ASR
- timeout
- retry
- low confidence

### AI

- schema validation
- malformed output
- hallucination resistance
- confidence handling
- explain-back

### OCR

- printed
- handwritten
- multilingual
- poor quality
- multiple documents
- evidence

### Clinical safety

- red flags
- escalation
- priority
- contradiction
- clinical gaps

### Backend

- auth
- API errors
- retries
- idempotency
- offline sync

### FHIR/ABDM

- mapping
- validation
- sandbox if available

### Privacy

- reset
- purge
- no cross-patient leakage

---

# 59. REAL DEVICE TESTING

The developer must test on a physical Android device/tablet.

Test:

```text
camera
microphone
speaker
permissions
orientation
screen size
touch
network loss
reconnect
background/foreground
session reset
```

A desktop browser demo is not sufficient.

---

# 60. ERROR STATES

Every network/API feature needs:

```text
Loading
Success
Empty
Retryable error
Permanent error
Offline
Unauthorized
Timeout
Malformed response
```

Never leave the patient staring at a blank screen.

Patient messages should be simple.

Example:

```text
"We couldn't connect right now.
Your information is still safe.
Please try again."
```

---

# 61. COMPONENT LIBRARY

Build reusable components rather than one-off widgets.

Required concepts include:

```text
PrimaryCTA
SecondaryCTA
LanguageCard
ConsentCard
VoiceInputCard
TranscriptCard
QuestionCard
AnswerChoice
ProgressIndicator
OfflineBanner
HospitalServiceCard
EvidenceChip
ClinicalFactCard
MedicationTimeline
RedFlagBanner
VitalsCard
QueueTokenCard
PrivacyResetOverlay
ActiveCallCard
DocumentCaptureCard
OCRReviewCard
DoctorSummaryCard
```

The existing Android design specification specifically defines components such as:

- `HospitalServiceCard`
- `OfflineBanner`
- `PrivacyResetOverlay`
- `ActiveCallCard`

Preserve these concepts.

---

# 62. ACTIVE CALL UI

For a call/intake simulation surface, use:

```text
Top:
AI/doctor avatar
call timer
AI Intake Active

Center:
audio visualizer
rolling transcript

Bottom:
symptom chips

Controls:
speaker
mute
large red end-call button
```

This is useful for demonstrating the voice-session concept.

But distinguish:

```text
CALL SIMULATION
```

from a real PSTN call.

---

# 63. TECHNICAL STACK

Use the existing repository stack where already established.

Target architecture:

| Layer | Technology / role |
|---|---|
| Patient client | Flutter |
| Patient platform | Android kiosk; iOS where required |
| Patient web | Flutter Web where specified |
| Backend | Existing FastAPI backend/repository |
| API | REST/HTTP as defined by repository |
| Database | PostgreSQL where established |
| Vector search | pgvector where established |
| Backend schemas | Pydantic / repository equivalents |
| Local state | project-selected Flutter persistence |
| Auth | existing backend auth |
| OCR | existing configured OCR pipeline |
| ASR | existing configured ASR/Bhashini/AI4Bharat or provider |
| TTS | configured multilingual TTS |
| Embeddings | multilingual model as configured |
| Local AI | Ollama + project-approved model configuration |
| Cloud AI | vendor-agnostic gateway; configured providers |
| FHIR | FHIR R4 |
| ABDM | sandbox integration boundary |
| Telephony | provider-neutral IVR adapter unless real provider already exists |
| Storage | secure object/local storage according to architecture |
| Testing | Flutter tests + backend tests + integration tests |

### Important

The names above describe architecture roles.

The developer must inspect actual repository dependencies before replacing anything.

---

# 64. ENVIRONMENT CONFIGURATION

Use configuration such as:

```text
BACKEND_BASE_URL
API_ENV
AI_PROVIDER
AI_MODEL
ASR_PROVIDER
OCR_PROVIDER
EMBEDDING_PROVIDER
ABDM_ENV
TELEPHONY_PROVIDER
```

Secrets:

```text
DATABASE_URL
LLM_API_KEY
ASR_API_KEY
OCR_API_KEY
ABDM credentials
JWT/auth secret
telephony credentials
```

must remain outside source control.

---

# 65. API ERROR CONTRACT

Normalize backend errors into a frontend-safe model.

Example:

```text
ApiError
  code
  message
  retryable
  statusCode
  requestId
```

Patient sees a simple message.

Developer logs the technical detail safely.

---

# 66. DATA STATUS MODEL

Use explicit states where appropriate:

```text
DRAFT
CAPTURED
PROCESSING
LOW_CONFIDENCE
NEEDS_REVIEW
CONFIRMED
SUBMITTED
SYNC_PENDING
SYNCED
FAILED
PURGED
```

Never overload one boolean such as:

```text
isComplete
```

for multiple meanings.

---

# 67. OBSERVABILITY

Log safely:

- request ID
- session ID where appropriate
- timing
- error code
- subsystem
- model/provider status
- retry count

Do not log raw:

- patient speech
- medical documents
- identifiers
- sensitive clinical information

unless explicitly required and protected.

---

# 68. PERFORMANCE TARGETS

Treat the following as project targets/projections unless actually measured:

- fast patient interaction
- rapid recovery from network interruptions
- low doctor review time
- high evidence coverage
- low duplicate submission rate

Never present a target as a measured result.

---

# 69. DEMO MODE

The demo should prove the entire chain.

Recommended demonstration:

```text
1. Patient approaches kiosk
2. Selects language
3. Gives audio-explained consent
4. Identifies
5. Speaks complaint
6. Answers adaptive questions
7. Show AYUSH branch
8. Trigger one deliberate red flag
9. Scan 2–3 documents
10. Show chronological ordering
11. Show abnormal/low-confidence flags
12. Show evidence
13. Show summary
14. Show queue token
15. Open doctor dashboard
16. Show changes-first view
17. Show evidence-linked facts
18. Show FHIR boundary / bundle if actually available
19. Show IVR backup concept
20. Complete and privacy-reset session
```

---

# 70. DEMO DATA RULE

Use clearly synthetic demo patients.

Never use real patient information in a public demonstration.

Synthetic examples should be labeled:

```text
DEMO DATA
```

---

# 71. TESTING MATRIX

| Area | Test |
|---|---|
| Onboarding | Start → language → consent |
| Consent | agree / reject |
| Identity | existing / new / fallback |
| Voice | speak / repeat / no speech |
| Touch | every question answerable |
| SOCRATES | branching |
| AYUSH | all required structured fields |
| Red flag | deliberate trigger |
| OCR | printed document |
| OCR | handwriting low confidence |
| Documents | multiple/out of order |
| Evidence | source traceability |
| Contradiction | patient vs document |
| Medication | temporal status |
| Vitals | valid / invalid |
| Summary | structured output |
| Queue | priority |
| Doctor | edit/verify |
| Hospital | service card |
| Emergency | SOS flow |
| IVR | language / DTMF / voice |
| Offline | network loss |
| Sync | reconnect |
| Privacy | purge |
| Localization | all supported languages |
| Accessibility | large text/touch |
| Android | physical device |
| FHIR | validation |
| Security | secrets not committed |

---

# 72. QUALITY GATES

The developer cannot call a phase complete merely because:

```text
the screen appears
```

A phase is complete only when:

```text
UI works
+
state works
+
API boundary works
+
error state works
+
loading state works
+
offline state works where applicable
+
tests pass
+
no analyzer errors
+
no obvious privacy leak
```

---

# 73. DEFINITION OF DONE

MediKiosk is considered complete only when:

### Patient

- [ ] Welcome
- [ ] Language
- [ ] Consent
- [ ] Identification
- [ ] Returning-patient path
- [ ] Care selection
- [ ] Voice intake
- [ ] Touch fallback
- [ ] SOCRATES
- [ ] AYUSH
- [ ] Red flags
- [ ] Document capture
- [ ] OCR
- [ ] Evidence
- [ ] Medication timeline
- [ ] Contradictions
- [ ] Vitals
- [ ] Clinical gaps
- [ ] Explain-back
- [ ] Summary
- [ ] Queue
- [ ] Hospital services
- [ ] Emergency
- [ ] Privacy reset

### Doctor

- [ ] Queue
- [ ] Priority
- [ ] Changes-first
- [ ] Summary
- [ ] Vitals
- [ ] Documents
- [ ] Evidence
- [ ] AYUSH
- [ ] Gaps
- [ ] Red flags
- [ ] Verification

### Backup

- [ ] IVR architecture
- [ ] call session integration
- [ ] DTMF fallback
- [ ] same clinical schema
- [ ] same queue/doctor workflow
- [ ] real telephony status clearly documented

### Technical

- [ ] API contract documented
- [ ] mock mode
- [ ] offline mode
- [ ] secure config
- [ ] error handling
- [ ] tests
- [ ] Android device test
- [ ] FHIR validation where available
- [ ] ABDM sandbox status documented
- [ ] session purge verified

---

# 74. REQUIRED FINAL DOCUMENTS

At completion produce:

```text
IMPLEMENTATION_AUDIT.md
API_CONTRACT_AUDIT.md
FEATURE_STATUS.md
ARCHITECTURE.md
IVR_INTEGRATION_STATUS.md
AI_MODEL_STATUS.md
FHIR_ABDM_STATUS.md
TEST_REPORT.md
SECURITY_CHECKLIST.md
FINAL_IMPLEMENTATION_REPORT.md
```

`FINAL_IMPLEMENTATION_REPORT.md` must contain:

1. What was already implemented.
2. What was changed.
3. What was newly implemented.
4. What remains mocked.
5. What remains unimplemented.
6. Real API endpoints used.
7. AI providers/models used.
8. OCR status.
9. IVR status.
10. FHIR status.
11. ABDM status.
12. Tests run.
13. Test results.
14. Known limitations.
15. Exact commands to run the system.

---

# 75. ANTIGRAVITY OPERATING RULES

The AI agent must work like a senior engineer, not a code generator.

For every task:

```text
CONTEXT
SOURCE OF TRUTH
TASK
CONSTRAINTS
FILES ALLOWED
API
ACCEPTANCE CRITERIA
TEST
DO NOT
```

Before editing:

```text
inspect files
understand dependencies
understand existing behavior
```

After editing:

```text
format
analyze
test
review diff
```

Do not make broad unrelated changes.

---

# 76. SINGLE-DEVELOPER WORKTREE RULE

Because one developer owns the implementation:

```text
main
  |
  +-- feature/onboarding
  +-- feature/intake
  +-- feature/documents
  +-- feature/doctor-dashboard
  +-- feature/ivr
  +-- feature/fhir
```

Even as one person, use focused commits.

Commit examples:

```text
feat: implement multilingual consent flow
feat: connect intake session API
feat: add OCR evidence review
feat: add doctor changes-first dashboard
feat: add IVR adapter boundary
fix: preserve session during network loss
test: add red-flag rule integration tests
```

---

# 77. FULL MASTER ANTIGRAVITY PROMPT

## COPY EVERYTHING BELOW THIS LINE INTO ANTIGRAVITY

```text
You are the sole senior full-stack developer responsible for completing the MediKiosk project.

This is NOT a greenfield project.

The existing MediKiosk backend/repository already contains project code and API structures. Your first responsibility is to understand and reuse the existing implementation rather than replacing it.

============================================================
SOURCE OF TRUTH
============================================================

Before changing code, read:

1. The complete existing repository.
2. MEDIKIOSK_ANDROID_DESIGN_SPEC.md
3. Existing MediKiosk development-flow / architecture documents.
4. Existing technical-stack documents.
5. Existing backend README and API documentation.
6. Existing schema/model files.
7. Existing tests.
8. Existing environment/configuration files.

Treat the official problem requirements and working repository behavior as higher priority than assumptions.

Do not invent APIs, database schemas, FHIR mappings, clinical thresholds, or integrations.

If something is specified but not implemented, mark it clearly as:

IMPLEMENTED
PARTIALLY IMPLEMENTED
MOCKED
INTEGRATION READY
NOT IMPLEMENTED

============================================================
MISSION
============================================================

Complete MediKiosk as a coherent patient-facing pre-consultation clinical intake platform.

The final product must preserve the complete product architecture:

PRIMARY:
Physical kiosk / patient application

SECONDARY:
Telephone / IVR backup for elderly/basic-phone users

DOCTOR:
Clinical dashboard consuming the same backend session

The kiosk and IVR MUST converge into the same clinical data model and doctor workflow.

============================================================
NON-NEGOTIABLE FEATURES
============================================================

Do not remove any of these:

- multilingual onboarding
- audio-explained consent
- patient identification
- returning-patient fast path
- voice intake
- touch fallback
- SOCRATES adaptive questioning
- AYUSH Dashavidha Pariksha
- Ahara-Vihara
- Agni
- Koshtha
- Nidana
- Samprapti
- deterministic red-flag engine
- staff escalation
- document capture
- OCR
- printed document extraction
- handwriting low-confidence review
- evidence-linked facts
- medication timeline
- temporal history
- patient/document contradiction handling
- semantic normalization
- explain-back verification
- clinical gap detection
- vitals
- structured summary
- bilingual/multilingual summary
- queue intelligence
- doctor dashboard
- changes-first clinical view
- hospital services
- hospital map/directions
- emergency/SOS
- privacy reset
- offline/edge behavior
- telephone/IVR backup
- FHIR boundary
- ABDM sandbox boundary where supported
- mock/demo mode

============================================================
IMPORTANT SAFETY RULE
============================================================

The LLM is NOT the doctor.

AI may:

- transcribe
- translate
- normalize
- extract candidate facts
- retrieve semantic concepts
- summarize validated facts
- classify documents

AI must NOT:

- invent facts
- invent medication doses
- independently diagnose
- independently determine emergency disposition
- overwrite source evidence
- hide uncertainty

Emergency/red-flag decisions must use deterministic, auditable rules and configured clinical policy.

============================================================
STEP 0 — AUDIT BEFORE CODING
============================================================

Inspect:

- repository tree
- Flutter code if present
- backend code
- API routes
- Pydantic/schema definitions
- database models
- migrations
- auth
- document pipeline
- voice/call session code
- doctor APIs
- queue APIs
- tests
- environment configuration

Create:

IMPLEMENTATION_AUDIT.md
API_CONTRACT_AUDIT.md
FEATURE_STATUS.md

Do not begin a major rewrite until the audit is complete.

============================================================
STEP 1 — FREEZE CONTRACTS
============================================================

Identify the actual contracts for:

- clinical session
- consent
- identity
- message/audio
- clinical facts
- AYUSH history
- documents
- OCR
- evidence
- vitals
- red flags
- queue
- doctor
- summary
- FHIR
- call/IVR

Document:

endpoint
method
request
response
auth
errors
status values

Do not invent endpoints.

============================================================
STEP 2 — APPLICATION FOUNDATION
============================================================

Implement/verify:

- routing
- theme
- localization
- state management
- API client
- repository layer
- secure storage
- permissions
- connectivity detection
- mock mode
- error states
- loading states
- offline states

Preserve existing architecture if it is already clean.

============================================================
STEP 3 — PATIENT FLOW
============================================================

Implement the complete sequence:

WELCOME
→ LANGUAGE
→ CONSENT
→ IDENTIFY
→ RETURNING PATIENT
→ CARE/OPD
→ CONVERSATIONAL INTAKE
→ ADAPTIVE QUESTIONS
→ AYUSH
→ RED FLAG
→ DOCUMENTS
→ OCR
→ EVIDENCE REVIEW
→ VITALS
→ CLINICAL GAPS
→ EXPLAIN BACK
→ SUMMARY
→ QUEUE
→ HOSPITAL SERVICES
→ COMPLETION
→ PRIVACY RESET

Every transition must work.

Every important state must have:

loading
success
error
retry
offline
empty where applicable

============================================================
STEP 4 — UI REQUIREMENTS
============================================================

Use MEDIKIOSK_ANDROID_DESIGN_SPEC.md as the detailed visual source.

Do not create a generic Material UI.

Use:

- large healthcare-oriented controls
- high contrast
- restrained rounded cards
- clear hierarchy
- large typography
- semantic icons
- subtle motion
- accessible touch targets
- multilingual support

Preserve the defined components:

HospitalServiceCard
OfflineBanner
PrivacyResetOverlay
ActiveCallCard
and the other reusable components specified by the design document.

Every clinical question must support:

VOICE
OR
TOUCH

Do not force typing.

============================================================
STEP 5 — VOICE / CONVERSATIONAL ENGINE
============================================================

Connect the Flutter/client workflow to the actual backend voice/session APIs.

Support:

- listening
- processing
- transcript
- confirmation
- retry
- repeat
- low confidence
- offline behavior

Implement the SOCRATES flow.

Do not turn the conversation into an uncontrolled diagnostic chatbot.

============================================================
STEP 6 — AYUSH
============================================================

Implement structured AYUSH fields:

Prakriti
Vikriti
Sara
Samhanana
Pramana
Satmya
Sattva
Ahara Shakti
Vyayama Shakti
Vaya

Plus:

Ahara-Vihara
Agni
Koshtha
Nidana
Samprapti

Do not replace these with a notes field.

============================================================
STEP 7 — RED FLAGS
============================================================

Use deterministic rules.

When triggered:

- create red-flag event
- alert authorized clinical/staff terminal
- show simple emergency instruction
- stop or alter queue progression according to configured policy
- preserve audit state

Do not let an LLM independently decide emergency status.

============================================================
STEP 8 — DOCUMENT AI
============================================================

Implement:

camera capture
→ quality check
→ upload/local processing
→ OCR
→ document classification
→ entity extraction
→ confidence
→ evidence
→ review

Important facts must preserve source provenance where supported.

Low-confidence handwriting must go to review rather than being silently accepted.

============================================================
STEP 9 — SEMANTIC NORMALIZATION
============================================================

Use the configured multilingual embedding/semantic matching architecture.

Pipeline:

patient phrase
→ language normalization
→ embedding
→ vector retrieval
→ candidate concept
→ deterministic validation
→ confidence
→ direct mapping OR explain-back

Do not hardcode provider/model details in UI.

============================================================
STEP 10 — CONTRADICTIONS / MEDICATION TIMELINE
============================================================

Do not overwrite conflicting sources.

Example:

Document:
Metformin 500 mg

Patient:
Stopped two months ago

Store/display both facts with temporal/source context.

Use valid_from / valid_until or the exact repository equivalent where supported.

============================================================
STEP 11 — DOCTOR DASHBOARD
============================================================

Build the physician view around:

- queue
- priority
- changes-first
- chief complaint
- HPI
- vitals
- medications
- documents
- evidence
- AYUSH
- clinical gaps
- red flags
- verification

Clearly distinguish:

Patient said
AI extracted
OCR extracted
System flagged
Doctor verified

============================================================
STEP 12 — IVR BACKUP
============================================================

First inspect the repository's existing call/voice-session implementation.

Do not assume that call-session APIs equal PSTN telephony.

If real telephony exists:
integrate it.

If it does not:
build a provider-neutral IVR adapter and mock/simulation layer.

The IVR flow is:

hospital number
→ language
→ consent
→ identification
→ voice/DTMF
→ ASR
→ same clinical session
→ SOCRATES
→ AYUSH
→ red flags
→ queue
→ doctor dashboard

Do NOT create a separate IVR clinical database/schema.

============================================================
STEP 13 — OFFLINE
============================================================

Support safe offline operation.

When offline:

- preserve local progress
- show status
- queue safe operations
- retry
- do not fake success
- do not lose patient data

When online again:

- synchronize safely
- prevent duplicates
- handle conflicts

============================================================
STEP 14 — PRIVACY
============================================================

Implement the privacy reset overlay.

On timeout/reset:

clear:

patient identity
temporary documents
temporary images
temporary transcripts
session state
sensitive UI state

Then return to welcome.

Test that patient B cannot see patient A's data.

============================================================
STEP 15 — FHIR / ABDM
============================================================

Inspect existing FHIR/ABDM implementation.

Do not claim production integration unless actually tested.

Where supported:

clinical data
→ FHIR R4
→ validation
→ ABDM sandbox

Document exact status.

============================================================
STEP 16 — SECURITY
============================================================

Never commit:

API keys
database credentials
JWT secrets
ABDM credentials
telephony credentials

Use environment configuration.

Do not log sensitive clinical content unnecessarily.

============================================================
STEP 17 — TESTING
============================================================

Run:

flutter pub get
flutter analyze
flutter test

Run backend tests where applicable.

Add integration tests for:

- onboarding
- voice
- touch
- SOCRATES
- AYUSH
- red flags
- OCR
- evidence
- contradictions
- vitals
- summary
- queue
- doctor dashboard
- IVR
- offline/reconnect
- privacy reset

Test on a real Android device.

============================================================
STEP 18 — NO STATIC MOCKING OF CORE FEATURES
============================================================

Do not build screens that only look correct.

Buttons must have real behavior.

If a feature cannot yet connect to a real backend:

create a repository/service boundary and explicit mock implementation.

Do not bury fake API responses directly inside widgets.

============================================================
STEP 19 — FINAL VALIDATION
============================================================

Before declaring completion:

1. Run analyzer.
2. Run tests.
3. Build Android.
4. Install/run on physical Android device.
5. Test microphone.
6. Test camera.
7. Test permissions.
8. Test offline.
9. Test reconnect.
10. Test privacy reset.
11. Test red flag.
12. Test OCR.
13. Test doctor dashboard.
14. Test IVR status.
15. Test FHIR status.
16. Review git diff.
17. Remove debug prints/secrets.
18. Document remaining limitations.

============================================================
FINAL OUTPUTS
============================================================

Create:

IMPLEMENTATION_AUDIT.md
API_CONTRACT_AUDIT.md
FEATURE_STATUS.md
ARCHITECTURE.md
IVR_INTEGRATION_STATUS.md
AI_MODEL_STATUS.md
FHIR_ABDM_STATUS.md
TEST_REPORT.md
SECURITY_CHECKLIST.md
FINAL_IMPLEMENTATION_REPORT.md

FINAL_IMPLEMENTATION_REPORT.md must explicitly separate:

IMPLEMENTED
MOCKED
INTEGRATION READY
NOT IMPLEMENTED

Do not hide incomplete integrations.

============================================================
FINAL RULE
============================================================

Do not stop when the UI looks good.

MediKiosk is complete only when:

PATIENT UI
+
VOICE
+
TOUCH
+
AYUSH
+
RED FLAGS
+
OCR
+
EVIDENCE
+
VITALS
+
SUMMARY
+
QUEUE
+
DOCTOR DASHBOARD
+
IVR BACKUP
+
OFFLINE
+
PRIVACY
+
FHIR/ABDM BOUNDARY
+
TESTING

are connected into one coherent workflow.

Work incrementally, inspect before editing, preserve working code, and never invent unsupported clinical or integration behavior.
```

---

# 78. FINAL COMMAND CHECKLIST FOR THE DEVELOPER

After implementation:

```bash
flutter pub get
flutter analyze
flutter test
flutter build apk
flutter run
```

Backend commands must follow the existing repository README.

For final verification, run the application on a physical Android device and walk through the complete journey from:

```text
Welcome
→ Language
→ Consent
→ Identify
→ Intake
→ AYUSH
→ Red Flag
→ Documents
→ OCR
→ Evidence
→ Vitals
→ Summary
→ Queue
→ Doctor
→ Completion
→ Privacy Reset
```

Then separately validate:

```text
IVR
FHIR/ABDM
Offline
Security
```

---

# 79. PROJECT COMPLETION PRINCIPLE

The final MediKiosk system should demonstrate one continuous clinical information pipeline:

```text
                   PATIENT
                      |
        +-------------+-------------+
        |                           |
      KIOSK                        IVR
        |                           |
        +-------------+-------------+
                      |
              CLINICAL SESSION
                      |
        +-------------+-------------+
        |             |             |
      VOICE          TOUCH        DOCUMENTS
        |             |             |
        +-------------+-------------+
                      |
              STRUCTURED FACTS
                      |
        +-------------+-------------+
        |             |             |
       AYUSH       SAFETY         VITALS
        |             |             |
        +-------------+-------------+
                      |
            EVIDENCE + GAPS
                      |
                 SUMMARY
                      |
              QUEUE / ROUTING
                      |
              DOCTOR DASHBOARD
                      |
        +-------------+-------------+
        |                           |
       HIS                      FHIR/ABDM
                      |
                 PRIVACY PURGE
```

That is the product.

Do not implement disconnected pages.
Do not implement disconnected AI demos.
Do not implement a fake IVR.
Do not implement a fake doctor dashboard.

Build one coherent system.
