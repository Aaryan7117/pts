# MediKiosk --- Master Context & Improvement Brief

> **Purpose:** This file is a reusable context document for an
> AI/developer working on the existing MediKiosk repository for Smart
> India Hackathon problem statement **SIH26047 --- Patient Case-Taking
> Software**.
>
> **Critical instruction for future implementation:** Treat the existing
> repository as the source of truth for current implementation.
> **Inspect the repo before changing architecture or rewriting
> modules.** Preserve working functionality, identify gaps against this
> document, and improve incrementally.

------------------------------------------------------------------------

# 1. Project Identity

## Problem Statement

**SIH26047 --- Patient Case-Taking Software**

Organization: **All India Institute of Ayurveda (AIIA), Ministry of
AYUSH**

The problem is fundamentally about the **first-mile clinical intake
bottleneck** in high-volume hospitals.

The desired product is **MediKiosk**: a patient-facing, pre-consultation
clinical intake system that converts fragmented patient information into
structured, physician-readable, verifiable clinical information before
the consultation.

### Core product framing

> **MediKiosk is an AI-assisted first-mile clinical intake system that
> converts natural patient communication and fragmented medical
> documents into structured, verifiable clinical information and
> connects that case to the hospital's doctor workflow.**

Do **not** frame it as merely: - an AI chatbot - a symptom checker - a
generic OCR application - an appointment app - a replacement EHR - an
autonomous diagnostic system

The strongest product framing is:

> **The AI is not the product. The workflow is the product.**

------------------------------------------------------------------------

# 2. Problem Understanding

Indian high-volume OPDs face a clinical history-taking bottleneck.

Patients may arrive with: - paper prescriptions - lab reports -
discharge summaries - imaging reports - handwritten medical records -
incomplete recollection of previous treatment

Doctors may have only a few minutes per consultation.

The PS identifies the "first-mile" problem: ABDM/FHIR can support
interoperable health information exchange, but the patient's real-world
information still needs to be captured, digitized, structured, verified,
and made useful before consultation.

MediKiosk therefore sits between:

``` text
Patient
   ↓
MediKiosk
   ↓
Structured clinical information
   ↓
Doctor / Hospital HIS
   ↓
FHIR / ABDM where supported
```

### Important ABDM interpretation

ABHA should be treated primarily as an **identity/linkage and
consent-aware interoperability mechanism**, not as a reason to build a
new national centralized health database.

Do NOT claim:

> "Enter ABHA and MediKiosk downloads every medical record from every
> hospital."

Actual access/exchange depends on participating facilities,
interoperability, record availability, consent, and authorized ABDM
workflows.

MediKiosk should solve the missing **data acquisition/structuring
layer**.

------------------------------------------------------------------------

# 3. Full PS Requirement Set

## A. Patient-facing requirements

-   Patient-facing software
-   Self-service workflow
-   Minimal staff assistance
-   Simple interface for elderly / low-literacy / non-technical patients
-   Guided touchscreen interaction
-   Natural voice interaction
-   Multiple Indian languages / accents
-   Audio prompts
-   Visual/icon-based interaction
-   Patient verification before final submission

## B. Clinical history requirements

Capture a comprehensive history including:

-   Chief complaint
-   History of Present Illness (HPI)
-   Past medical history
-   Past surgical history
-   Drug/medication history
-   Allergy history
-   Family history
-   Personal/social history
-   Review of systems
-   Relevant clinical/vital information where available

### Adaptive questioning

The system must dynamically ask relevant follow-up questions based on
the patient's complaint and previous answers.

Example:

``` text
Chest pain
    ↓
Onset
    ↓
Character
    ↓
Location
    ↓
Radiation
    ↓
Aggravating/relieving factors
    ↓
Associated symptoms
```

The PS uses chest pain / SOCRATES-style questioning as an example.

### Dual-mode interaction

Every meaningful question should be answerable by: - speaking -
tapping/selecting

The patient should not be forced into a voice-only or text-only
experience.

------------------------------------------------------------------------

# 4. AYUSH Requirements

MediKiosk must support an AYUSH-aware history workflow, especially for
Ayurvedic OPDs.

The extended Ayurvedic history should account for **Dashavidha
Pariksha**:

1.  Prakriti
2.  Vikriti
3.  Sara
4.  Samhanana
5.  Pramana
6.  Satmya
7.  Sattva
8.  Ahara Shakti
9.  Vyayama Shakti
10. Vaya

Also include: - Ahara - Vihara - relevant Ayurveda-specific
history/context

The AYUSH mode should be a structured clinical workflow, not merely a
prompt saying "you are an Ayurveda assistant."

------------------------------------------------------------------------

# 5. Red-Flag / Safety Requirements

The system must identify potentially dangerous symptoms and escalate
them to human clinical staff.

Examples: - acute chest pain with dyspnoea - stroke-like symptoms -
severe breathing difficulty - severe allergic reaction - uncontrolled
bleeding - other validated red flags

## Recommended safety architecture

Do NOT allow a general LLM to make final emergency decisions.

Preferred:

``` text
Patient language
    ↓
ASR
    ↓
Structured clinical facts
    ↓
Deterministic safety rules
    ↓
Red-flag alert
    ↓
Human triage
```

The AI may extract/classify information, but: - no autonomous
diagnosis - no autonomous prescription - no final clinical decision -
all safety alerts require human review

### Conservative principle

Prefer catching potentially dangerous signals and sending them for human
review rather than pretending the system can safely diagnose.

------------------------------------------------------------------------

# 6. Medical Document Digitization

The patient should be able to scan/upload existing medical records.

Expected document types: - prescriptions - lab reports - discharge
summaries - imaging reports - consultation notes - other relevant
records

## Required pipeline

``` text
Image / PDF
    ↓
Document classification
    ↓
OCR / vision extraction
    ↓
Clinical entity extraction
    ↓
Normalization / validation
    ↓
Evidence attachment
    ↓
Timeline
```

## OCR requirements

Support: - printed documents - handwritten documents - multilingual
records

## Extract

### Diagnoses

``` json
{
  "category": "condition",
  "label": "Type 2 Diabetes",
  "source": "document"
}
```

### Medications

``` json
{
  "category": "medication",
  "name": "Metformin",
  "strength": "500 mg",
  "frequency": "twice daily"
}
```

### Investigations

``` json
{
  "category": "measurement",
  "test": "HbA1c",
  "value": "7.8",
  "unit": "%"
}
```

### Procedures

``` json
{
  "category": "procedure",
  "name": "Appendectomy",
  "date": "2024-02-10"
}
```

Also extract where available: - dosage - frequency - duration -
reference ranges - dates - surgery/procedure history

------------------------------------------------------------------------

# 7. Evidence-First Document Architecture

A major design principle for MediKiosk:

> **No receipt, no fact.**

Every important extracted medical fact should ideally retain: - source
document ID - source page - OCR text/evidence - bounding box/polygon
when available - confidence - verification status

Example:

``` json
{
  "fact": "Metformin 500 mg",
  "confidence": 0.91,
  "source_document_id": "DOC-123",
  "page": 1,
  "evidence_text": "Metformin 500 mg",
  "bbox": [120, 330, 480, 370],
  "verified": false
}
```

This is particularly important for handwritten prescriptions where OCR
can be unreliable.

### Never silently invent missing values

If OCR says:

``` text
"Metf... 500"
```

do not silently convert it to:

``` text
Metformin 500 mg
```

unless there is a clearly defined normalization/confidence/verification
path.

------------------------------------------------------------------------

# 8. Contradiction Resolution

Patient-reported history may disagree with a document.

Example:

``` text
Prescription:
Metformin 500 mg twice daily

Patient:
"I stopped taking it months ago."
```

Do not overwrite one with the other.

Use non-destructive dual-fact preservation:

``` text
DOCUMENT FACT
Metformin 500 mg BID
        +
PATIENT REPORT
Patient says medication stopped
        ↓
Conflict
        ↓
Doctor review
```

This preserves provenance and can expose adherence drift.

------------------------------------------------------------------------

# 9. Chronological Medical Timeline

Uploaded documents must be organized into a coherent medical timeline.

Example:

``` text
2019
 └── Diagnosis

2020
 └── Surgery

2021
 └── Lab investigation

2023
 └── Follow-up

2025
 └── Prescription
```

Timeline events should retain: - date - event type - source - extracted
facts - confidence - verification status

Do not fabricate dates. If the date is uncertain:

``` text
date: null
date_confidence: low
date_text: "around March 2023"
```

------------------------------------------------------------------------

# 10. Abnormal Lab / Medication Safety

The system may flag: - out-of-range lab values - possible medication
conflicts - allergy conflicts - clinically important missing information

But these are **alerts for physician attention**, not diagnoses.

Recommended architecture:

``` text
Extracted measurement
      ↓
Validated numeric value
      ↓
Reference range / deterministic rule
      ↓
Flag
      ↓
Doctor review
```

Avoid letting an LLM hallucinate laboratory ranges.

------------------------------------------------------------------------

# 11. Structured Clinical Summary

The final summary should combine:

``` text
Patient-reported history
+
Digitized documents
+
Timeline
+
Safety flags
+
Data gaps
```

Recommended structure:

``` text
PATIENT
Demographics / identity

CHIEF COMPLAINT

HISTORY OF PRESENT ILLNESS

PAST MEDICAL HISTORY

PAST SURGICAL HISTORY

CURRENT MEDICATIONS

ALLERGIES

FAMILY HISTORY

PERSONAL / SOCIAL HISTORY

REVIEW OF SYSTEMS

AYUSH HISTORY
(if applicable)

PRIOR INVESTIGATIONS

DOCUMENT TIMELINE

RED FLAGS

DATA GAPS

EVIDENCE / SOURCE LINKS
```

The summary must be: - concise - physician-readable - structured -
editable - clearly marked as AI-generated/draft where appropriate

### Physician control

``` text
AI draft
   ↓
Doctor reviews
   ↓
Doctor edits
   ↓
Doctor confirms
   ↓
Persist final clinical record
```

------------------------------------------------------------------------

# 12. ABDM / ABHA / FHIR Strategy

## Three distinct layers

Do not confuse these:

### Layer 1 --- Identity

ABHA / patient identity.

### Layer 2 --- MediKiosk clinical data creation

MediKiosk creates: - structured history - observations - medication
facts - allergies - documents - encounters - timeline -
physician-verified summary

### Layer 3 --- Interoperability

FHIR / ABDM mechanisms can be used to exchange/link information with
participating systems under appropriate consent and authorization.

------------------------------------------------------------------------

# 13. FHIR Strategy

Use FHIR as the canonical interoperability model where practical.

Potential resources:

``` text
Patient
Encounter
Condition
Observation
MedicationStatement / MedicationRequest
AllergyIntolerance
Procedure
DiagnosticReport
DocumentReference
Questionnaire
QuestionnaireResponse
Consent
Practitioner
Organization
```

### Intake architecture

``` text
ClinicalFact
    ↓
Validation
    ↓
FHIR mapper
    ↓
FHIR resources / Bundle
```

Do not make the UI depend directly on FHIR details.

The internal `ClinicalFact` model should be the application-level source
of truth, with a mapper/export layer for FHIR.

------------------------------------------------------------------------

# 14. ClinicalFact --- Core Shared Model

The system should have one canonical internal representation.

Conceptually:

``` text
ClinicalFact
├── patient
├── encounter
├── complaint
├── HPI
├── past_history
├── surgical_history
├── medications
├── allergies
├── family_history
├── personal_history
├── ROS
├── AYUSH
├── observations
├── documents
├── timeline
├── safety
├── gaps
├── provenance
├── confidence
├── verification
└── timestamps
```

All access channels should produce the same structure.

------------------------------------------------------------------------

# 15. Primary + Secondary Channels

## Primary: Web / Physical Kiosk

Hardware: - touchscreen - microphone - camera - speaker

Workflow:

``` text
Identify
 ↓
Consent
 ↓
Language
 ↓
Voice / Touch interview
 ↓
Scan documents
 ↓
Verify facts
 ↓
Safety / gaps
 ↓
Specialty routing
 ↓
Doctor / queue
```

## Secondary: IVR

For: - basic phones - elderly users - users without smartphones - users
uncomfortable with apps

Workflow:

``` text
Telephone
 ↓
Language selection
 ↓
Speech / DTMF
 ↓
ASR
 ↓
same ClinicalFact pipeline
 ↓
same safety
 ↓
same routing
 ↓
same doctor dashboard
```

### Important

IVR is an **access channel**, not a second backend.

``` text
Kiosk ─────┐
           ├──> SAME BACKEND
IVR ───────┘
```

Also:

> Basic phone != offline AI.

The phone is simple, but IVR still requires telephony
infrastructure/backend/cloud connectivity.

------------------------------------------------------------------------

# 16. Optional Android / BYOD Channel

Android/mobile should be treated as another access channel, not another
MediKiosk backend.

``` text
Android
   ↓
Same Encounter
   ↓
Same ClinicalFact
   ↓
Same Safety
   ↓
Same Routing
   ↓
Same Doctor
```

The kiosk remains the controlled environment for the full offline AI
floor.

------------------------------------------------------------------------

# 17. Offline-First Architecture

One major proposed differentiation is an offline-capable local floor.

Target architecture from previous planning:

``` text
Browser / kiosk
     ↓
FastAPI
     ↓
Local AI services
     ├── ASR
     ├── OCR
     ├── embeddings
     ├── TTS
     └── local LLM
```

Proposed hardware budget for a laptop with 16 GB RAM / 8 GB VRAM:

``` text
GPU
Qwen 2.5 7B Q4_K_M       ~4.70 GB
KV cache                  ~0.60 GB
CUDA/runtime              ~0.40 GB
Display/OS                 ~1.00 GB
Total                      ~6.70 GB

RAM
OS                         ~3.50 GB
Browser                    ~1.00 GB
IndicWhisper               ~0.90 GB
RapidOCR                   ~0.80 GB
MiniLM                     ~0.15 GB
Piper                      ~0.05 GB
FastAPI + SQLite           ~0.30 GB
Total                      ~6.70 GB
```

These numbers are architecture estimates, not universal performance
guarantees. Benchmark on the actual target hardware.

------------------------------------------------------------------------

# 18. Proposed AI / Edge Stack

Previously considered:

### ASR

-   AI4Bharat IndicWhisper
-   Bhashini
-   Sarvam
-   cloud Whisper alternatives

### TTS

-   Piper
-   Bhashini
-   browser SpeechSynthesis fallback

### OCR

-   RapidOCR
-   PaddleOCR
-   Tesseract
-   multimodal VLM fallback
-   document-type-specific OCR

### Local LLM

-   Qwen 2.5 7B Q4_K_M via Ollama

### Embeddings

-   multilingual MiniLM
-   BGE-M3 as a stronger candidate for semantic retrieval

### Backend

-   FastAPI
-   SQLite/WAL for edge prototype
-   PostgreSQL for centralized/cloud deployment

### Frontend

-   React / Vite
-   or existing frontend stack if repository already has one

------------------------------------------------------------------------

# 19. Multilingual Pipeline

Target languages from previous architecture:

1.  English
2.  Hindi
3.  Tamil
4.  Telugu
5.  Marathi

Potential pipeline:

``` text
Patient speaks
     ↓
ASR
     ↓
Raw transcript
     ↓
Language normalization
     ↓
Negation detection
     ↓
Clinical concept mapping
     ↓
ClinicalFact
```

### Critical issue: negation

Do not use pure embeddings for clinical facts.

Example:

``` text
"bukhar hai"
"bukhar nahi hai"
```

Both contain the same word.

The second must not become:

``` text
fever = true
```

Use a hybrid:

``` text
rules / negation detection
+
semantic embeddings
+
clinical normalization
```

------------------------------------------------------------------------

# 20. Recommended Conversational Architecture

Do NOT use an unconstrained autonomous agent.

Preferred:

``` text
Clinical schema
     ↓
Find next required field
     ↓
LLM receives ONLY relevant context
     ↓
LLM extracts answer
     ↓
LLM phrases next question
     ↓
Validate structured result
     ↓
Update ClinicalFact
```

### Deterministic field selection

Example:

``` python
FIELDS = [
    "chief_complaint",
    "onset",
    "duration",
    "location",
    "character",
    "radiation",
    "aggravating_factors",
    "relieving_factors",
    "associated_symptoms",
    "past_medical_history",
    "medications",
    "allergies",
    "family_history",
    "personal_history",
    "ros",
]
```

The backend selects the next missing field.

The LLM should not be allowed to randomly skip critical fields.

------------------------------------------------------------------------

# 21. State Model

During the interview:

``` text
session_id
language
consent
current_field
asked_fields
ClinicalFact
red_flags
last_transcript
```

Prefer in-memory session state during rapid turn-taking.

Persist: - completed ClinicalFact - important safety flags - documents -
verified facts

Avoid a database round-trip for every conversational turn unless
required for durability.

------------------------------------------------------------------------

# 22. LLM Responsibilities

Good uses:

-   speech/text normalization
-   extracting explicit clinical facts
-   phrasing questions naturally
-   summarization
-   document semantic extraction
-   multilingual conversational interaction

Bad uses:

-   autonomous diagnosis
-   autonomous prescribing
-   inventing medical facts
-   inventing lab ranges
-   deciding emergency treatment
-   silently resolving contradictory evidence
-   deciding what medical fields can be skipped

------------------------------------------------------------------------

# 23. Document Pipeline Recommendation

A robust implementation:

``` text
Upload
  ↓
Virus/file validation
  ↓
Document classifier
  ↓
Preprocessing
  ↓
OCR/VLM
  ↓
Raw extracted text
  ↓
Clinical extraction
  ↓
Normalization
  ↓
Confidence
  ↓
Evidence attachment
  ↓
Human/patient verification where needed
  ↓
ClinicalFact
  ↓
Timeline
```

Process multiple documents independently/in parallel.

------------------------------------------------------------------------

# 24. Confidence Model

Every extracted clinical fact should ideally have:

``` text
confidence
source
evidence
verification_status
```

Example:

``` json
{
  "value": "Hemoglobin 12.5 g/dL",
  "confidence": 0.98,
  "verification_status": "unverified",
  "source_document": "lab_2025_01.pdf",
  "evidence": "Hemoglobin: 12.5 g/dL"
}
```

Possible statuses:

``` text
UNVERIFIED
PATIENT_CONFIRMED
PHYSICIAN_VERIFIED
REJECTED
CONFLICT
```

------------------------------------------------------------------------

# 25. Privacy / Security

Requirements:

-   consent-first workflow
-   minimal data collection
-   encrypted sensitive data
-   access control
-   audit logging
-   role-based access
-   session termination
-   raw audio retention minimization
-   secure document handling
-   DPDP Act 2023 considerations
-   ABDM consent framework considerations

Proposed edge design:

``` text
Temporary kiosk token
        ↓
Session
        ↓
Clinical processing
        ↓
Verification
        ↓
Persist required clinical data
        ↓
Purge ephemeral audio
```

Potential database protection: - SQLCipher / database encryption -
encryption at rest - TLS in transit - doctor PIN/RBAC

Do not claim production compliance merely because encryption exists.
Compliance requires legal, organizational and technical controls.

------------------------------------------------------------------------

# 26. Privacy Design Decision

Avoid passwords for elderly kiosk users.

Use:

``` text
temporary encounter token
+
ABHA/QR where available
+
hospital identity where required
+
staff-controlled access
```

Do not force ABHA as a hard prerequisite.

Recommended patient entry:

``` text
How would you like to continue?

[ Scan ABHA QR ]

[ I have an ABHA number ]

[ Continue without ABHA ]
```

If the hospital requires it, staff can guide the patient through
appropriate registration.

------------------------------------------------------------------------

# 27. Database Model

A useful starting relational model:

``` text
patients
sessions / encounters
clinical_facts
clinical_history
documents
document_facts
timeline_events
red_flags
consents
audit_logs
doctors
specialties
availability
appointments / queue
```

Do not store the whole history only as a giant text blob.

Use structured fields so the data can be: - queried - validated -
routed - exported to FHIR - compared over time

------------------------------------------------------------------------

# 28. Doctor Workflow

Doctor should receive:

``` text
Patient snapshot
        +
Chief complaint
        +
Clinical summary
        +
Timeline
        +
Documents
        +
Evidence
        +
Red flags
        +
Data gaps
        +
Current medications
        +
Allergies
```

Doctor actions:

``` text
Review
Edit
Verify
Reject
Continue consultation
```

Potential queue:

``` text
Emergency
Priority
Normal
```

But priority should come from validated rules and/or human triage rather
than opaque LLM judgment.

------------------------------------------------------------------------

# 29. Routing / Hospital Workflow Extension

The latest project planning expanded the core intake into:

``` text
ClinicalFact
    ↓
Validation
    ↓
Safety
    ↓
Specialty identification
    ↓
Doctor availability
    ↓
Appointment / queue
    ↓
Doctor dashboard
    ↓
Clinical review
```

Example:

``` text
Patient reports chronic knee pain
        ↓
Orthopedics / relevant specialty
        ↓
Available doctor
        ↓
Queue number
        ↓
Doctor dashboard
```

This is an extension of the PS workflow and should not replace the core
case-taking deliverable.

------------------------------------------------------------------------

# 30. Two-Developer Division Previously Planned

## THOUFIKUR

Primary responsibility:

``` text
Patient
 ↓
Web / Android
 ↓
Voice / Touch / OCR
 ↓
AI
 ↓
ClinicalFact
 ↓
Verification
 ↓
Evidence
```

Focus: - patient UI - voice - conversational engine - OCR - extraction -
clinical intelligence - evidence/provenance

## MUBASHIR

Primary responsibility:

``` text
ClinicalFact
 ↓
Backend
 ↓
Safety
 ↓
Specialty
 ↓
Doctor
 ↓
Availability
 ↓
Appointment / Queue
 ↓
Dashboard
```

Focus: - FastAPI/backend - database - doctor/specialty master -
routing - doctor dashboard - availability - appointments/queue -
integrations

## Shared

``` text
ClinicalFact schema
API contracts
FHIR
integration
testing
deployment
```

------------------------------------------------------------------------

# 31. Most Important Development Rule

Do NOT start with:

``` text
IVR
Maps
FHIR
Fancy UI
Hardware
```

before the core vertical slice works.

Start with:

### Patient side

``` text
Patient UI
+
ClinicalFact schema
+
Voice auto-fill
```

### Backend side

``` text
FastAPI
+
SQLite/PostgreSQL
+
Doctor/Specialty master
+
Routing API
```

Then connect:

``` text
VOICE
  ↓
ClinicalFact
  ↓
ROUTING
  ↓
DOCTOR
```

Only after that add: - OCR - FHIR - ABDM - IVR - appointment
automation - Android

------------------------------------------------------------------------

# 32. Definition of Done

MediKiosk is NOT complete merely because:

> "the UI works."

The complete workflow should be:

``` text
PATIENT
 ↓
VOICE / TOUCH
 ↓
ASR / INPUT
 ↓
AI
 ↓
SEMANTIC MATCHING
 ↓
ClinicalFact
 ↓
VALIDATION
 ↓
SAFETY
 ↓
SPECIALTY
 ↓
DOCTOR
 ↓
AVAILABILITY
 ↓
APPOINTMENT / QUEUE
 ↓
DOCTOR DASHBOARD
 ↓
CLINICAL REVIEW
```

For IVR:

``` text
BASIC PHONE
 ↓
IVR
 ↓
SAME ClinicalFact
 ↓
SAME SAFETY
 ↓
SAME ROUTING
 ↓
SAME DOCTOR DASHBOARD
```

------------------------------------------------------------------------

# 33. Existing Solutions / Repositories to Study

## SIH26047 implementations

### Clu3lesss/SIH26047

https://github.com/Clu3lesss/SIH26047

Important because it uses: - deterministic clinical field selection -
structured Pydantic state - LLM extraction/question phrasing - red-flag
classification - document extraction - MySQL - React/Next.js -
FastAPI/LangChain

The repository's architecture specifically avoids allowing the LLM to
control the whole interview.

### MihirMaurya-dev/medikiosk-sih26047

https://github.com/MihirMaurya-dev/medikiosk-sih26047

Useful for: - FastAPI - Gemini - Groq/OpenAI fallback - voice UI -
document scanning - doctor queue - SSE - ABHA/consent UI - summary
approval

### palaks-acc/MediKiosk-SIH26047

https://github.com/palaks-acc/MediKiosk-SIH26047

Useful for: - patient identification - consent - adaptive history -
AYUSH - OCR - medical entity extraction - timeline - physician summary -
FHIR-compatible JSON - SQLite

### SaumyaKhobragade/SIH26047-Sliding-Window-Prototype

https://github.com/SaumyaKhobragade/SIH26047-Sliding-Window-Prototype

Useful for: - service separation - ACI engine - prescription OCR - RAG -
voice service - summary generation - React + Vite - FastAPI - Docker
Compose

### Neelesh573/MediKiosk-SIH26047-Prototype

https://github.com/Neelesh573/MediKiosk-SIH26047-Prototype

Useful for: - React/TypeScript/Vite - Express - PostgreSQL - Drizzle -
OpenAPI - generated React Query client - Zod validation - structured API
contracts

------------------------------------------------------------------------

# 34. Clinical Conversational AI Research

## AMIE

Nature: https://www.nature.com/articles/s41586-025-08866-7

Study: - conversational diagnostic AI - history-taking - dialogue
quality - clinical reasoning - evaluation methodology

## Voice-interactive history taking in neurosurgical patients

PubMed: https://pubmed.ncbi.nlm.nih.gov/42134168/

Study: - voice interview - sequential questions - transcription -
EMR-compatible summary - real patient pilot

## Dementia pre-visit voice interviews

Emory: https://emorynlp.org/papers/2026-sigdial-breithaupt/

Study: - older adults - voice interaction - specialist-written interview
scripts - conditional branching - conversational AI

## Agentic AI vs physicians in history taking

medRxiv: https://www.medrxiv.org/content/10.64898/2026.01.23.26344723v1

Study: - iterative history completion - missing-information detection -
targeted follow-up

## Systematic review

JMIR: https://medinform.jmir.org/2024/1/e56628/

Study: - medical history-taking chatbots - feasibility - acceptance -
usability - clinical effectiveness

------------------------------------------------------------------------

# 35. OCR / Medical Document References

## DocIQ

https://github.com/pierremontanov/DocIQ

Useful for: - document classification - OCR - medical extraction -
structured output - FHIR artifacts

## Medical Prescription OCR

https://github.com/JonSnow1807/Medical-Prescription-OCR

Useful for: - prescription OCR - Donut - synthetic training data

## Another Medical Prescription OCR

https://github.com/Aniket025/Medical-Prescription-OCR

Useful for: - handwritten prescription recognition - medical entity
extraction

## Handwritten prescription research

https://www.aimsciences.org/article/doi/10.3934/jdg.2026016

Useful for: - handwriting recognition - digital medical record
generation

------------------------------------------------------------------------

# 36. FHIR / EHR References

## Medplum Patient Intake

https://github.com/medplum/medplum-patient-intake-demo

Study: - Questionnaire - QuestionnaireResponse - FHIR extraction -
intake workflow

## Medplum intake documentation

https://github.com/medplum/medplum/blob/main/packages/docs/docs/intake/intake-questionnaires.mdx

Study: - structured intake - SDC extraction - FHIR resource generation

## TriageAide

https://github.com/musketeers-br/TriageAide

Study: - FHIR-based triage - patient context - adaptive questions - FHIR
writes

## Strand

https://github.com/potalora/strand

Study: - longitudinal records - document ingestion - OCR - FHIR
normalization - timeline reconstruction

## HAPI FHIR

https://github.com/smart-on-fhir/hapi

Use for: - local FHIR server - R4 testing - synthetic data

------------------------------------------------------------------------

# 37. ABDM References

## ABDM Wrapper

https://github.com/NHA-ABDM/ABDM-wrapper

Study: - ABDM HIP - HIU - consent - discovery - linking - data
transfer - FHIR mapping

## ABDM

https://abdm.gov.in/

## ABDM About

https://ahpr.abdm.gov.in/about

## Bhashini

https://bhashini.gov.in/

## Bhashini ULCA

https://github.com/bhashini-dibd/ULCA

------------------------------------------------------------------------

# 38. Other Product References

## Ottehr

https://github.com/masslight/ottehr

Useful for: - open EHR workflow - patient intake - clinical workflow -
doctor-facing system

## Infermedica

https://developer.infermedica.com/

Useful for studying: - adaptive questioning - symptom evidence -
clinical interview engine

Do not blindly import diagnostic functionality into MediKiosk. The PS is
primarily about clinical history acquisition.

## Anamnesis.ai

https://github.com/osl-incubator/anamnesis.ai

Useful for: - conversational anamnesis - FHIR-oriented history capture

------------------------------------------------------------------------

# 39. Competitive Positioning

Existing categories:

  ---------------------------------------------------------------------------------
  Category                Examples                      Gap relative to MediKiosk
  ----------------------- ----------------------------- ---------------------------
  Generic chatbots        AI symptom/chat apps          Often cloud-only,
                                                        unstructured, not
                                                        hospital-integrated

  Symptom checkers        Ada, Infermedica, Ubie        Adaptive questioning but
                                                        not the full Indian
                                                        kiosk/document/AYUSH
                                                        workflow

  Ambient AI scribes      DAX, Abridge, Nabla           Primarily doctor-facing
                                                        during consultation

  EHR systems             Ottehr and others             Hospital/EHR oriented, not
                                                        necessarily first-mile
                                                        kiosk

  OCR systems             Tesseract/PaddleOCR/medical   Digitize documents but do
                          OCR projects                  not create the complete
                                                        clinical story

  ABDM                    National interoperability     Provides
                          ecosystem                     identity/interoperability
                                                        infrastructure, not the
                                                        complete first-mile capture
                                                        experience
  ---------------------------------------------------------------------------------

### MediKiosk gap

``` text
Patient-facing
+
Pre-consultation
+
Voice
+
Touch
+
Indian languages
+
AYUSH
+
Paper records
+
OCR
+
Clinical structuring
+
Evidence
+
Timeline
+
Safety
+
Doctor workflow
+
FHIR/ABDM interoperability
```

The novelty should be presented as the **integrated workflow**, not any
one AI model.

------------------------------------------------------------------------

# 40. Strong Product Narrative

Use:

> **"Don't digitize the patient's documents. Reconstruct the patient's
> medical story."**

Then demonstrate:

``` text
Patient says:
"I had diabetes for many years..."

       +

Old prescription

       +

Lab report

       +

Discharge summary

       ↓

MediKiosk

       ↓

Structured clinical facts

       ↓

Chronological medical story

       ↓

Evidence-linked physician summary

       ↓

Doctor verification

       ↓

Hospital / FHIR / ABDM workflow
```

------------------------------------------------------------------------

# 41. Strong Demo Story

The demo should show one continuous story:

1.  Patient enters/scans identity
2.  Consent
3.  Language selection
4.  Patient speaks
5.  Fields auto-fill
6.  Patient confirms
7.  AI asks only relevant missing questions
8.  Patient scans an old prescription
9.  Medication/history becomes structured
10. Evidence remains attached
11. Safety/gap checks run
12. Specialty is identified
13. Available doctor/slot is shown
14. Queue/appointment generated
15. Doctor sees complete case
16. Doctor reviews and edits
17. Final record is stored/exported

Do not demonstrate disconnected features one after another.

------------------------------------------------------------------------

# 42. Existing Repository Improvement Strategy

When an AI is asked to improve the existing repository:

## Step 1 --- Inspect before modifying

Determine:

``` text
Frontend framework
Backend framework
Database
Current API
Current schema
Current AI providers
Current OCR
Current ASR/TTS
Current authentication
Current persistence
Current FHIR/ABDM implementation
Current tests
Current deployment
```

## Step 2 --- Map implementation to this context

Create a matrix:

  Requirement    Existing implementation   Status    Gap   Priority
  -------------- ------------------------- --------- ----- ----------
  Voice          ...                       partial   ...   P0
  Touch          ...                       done      ...   P0
  ClinicalFact   ...                       missing   ...   P0
  OCR            ...                       partial   ...   P1
  Timeline       ...                       ...       ...   P1
  FHIR           ...                       ...       ...   P2
  ABDM           ...                       ...       ...   P2

## Step 3 --- Preserve working code

Do not rewrite the entire repository merely to match this architecture.

Prefer:

``` text
existing module
    ↓
adapter / refactor
    ↓
ClinicalFact
```

rather than:

``` text
delete existing repo
↓
build everything again
```

## Step 4 --- Build a vertical slice

First achieve:

``` text
Voice / Touch
    ↓
ClinicalFact
    ↓
Validation
    ↓
Safety
    ↓
Doctor Dashboard
```

Then add:

``` text
OCR
↓
Timeline
↓
FHIR
↓
ABDM
↓
IVR
```

------------------------------------------------------------------------

# 43. Priority System

## P0 --- Core PS

Must work:

-   patient kiosk
-   voice
-   touch
-   adaptive history
-   structured clinical state
-   patient confirmation
-   clinical summary
-   physician edit/confirm
-   document upload
-   OCR/extraction
-   red-flag safety
-   doctor dashboard
-   persistence

## P1 --- Strong differentiators

-   evidence bounding boxes
-   multilingual ASR/TTS
-   AYUSH mode
-   timeline
-   confidence
-   contradiction handling
-   deterministic safety
-   offline floor
-   robust document classification

## P2 --- Integration / production

-   FHIR R4
-   ABDM sandbox
-   real ABDM workflows
-   HIS integration
-   doctor availability
-   queue
-   appointment
-   audit logging
-   RBAC
-   encryption

## P3 --- Ecosystem extensions

-   IVR
-   Android/BYOD
-   omnichannel identity
-   advanced analytics
-   large-scale deployment
-   cross-facility longitudinal record reconstruction

------------------------------------------------------------------------

# 44. Engineering Rules

1.  **LLM is not the source of truth.**
2.  **ClinicalFact is the application source of truth.**
3.  **Patient/document evidence must remain traceable.**
4.  **Never silently infer uncertain medical facts.**
5.  **Never let an LLM make the final clinical decision.**
6.  **Use deterministic rules where deterministic logic is
    appropriate.**
7.  **Keep patient confirmation and physician verification explicit.**
8.  **Every AI-generated fact should have provenance/confidence where
    practical.**
9.  **Do not make ABHA a mandatory blocker unless the actual hospital
    workflow requires it.**
10. **Do not claim real ABDM integration unless it is actually
    implemented.**
11. **Do not claim production compliance from prototype controls
    alone.**
12. **Offline capability should degrade gracefully rather than fail
    completely.**
13. **All channels must converge on the same ClinicalFact model.**
14. **Do not build separate backends for kiosk, Android and IVR.**
15. **Build the complete workflow, not isolated features.**

------------------------------------------------------------------------

# 45. Testing Strategy

## Clinical extraction

Test: - direct statements - negation - uncertainty - Hinglish - regional
languages - multiple symptoms - contradictory answers - missing answers

Example:

``` text
"mujhe bukhar nahi hai"
```

must not produce:

``` text
fever = true
```

## Safety

Test: - true positive red flags - negated red flags - combinations -
false-positive-prone language - incomplete answers

## OCR

Test: - printed - handwritten - low quality - rotated - multilingual -
prescription - lab report - discharge summary

## Persistence

Test: - session completion - browser refresh - server restart -
duplicate uploads - incomplete sessions - concurrent patients

## FHIR

Validate generated resources against an R4 server/schema.

------------------------------------------------------------------------

# 46. Failure Handling

Every major component should define:

``` text
Why?
Where?
Input?
Output?
Model/technology?
Why this?
Why not alternative?
Owner?
Failure behavior?
Testing?
Integration?
```

Examples:

### ASR failure

``` text
Voice
 ↓
ASR fails
 ↓
show transcript retry
 ↓
touch input fallback
```

### TTS failure

``` text
TTS
 ↓
failure
 ↓
browser/native TTS
 ↓
text + visual controls
```

### OCR failure

``` text
OCR
 ↓
low confidence
 ↓
show original image
 ↓
ask patient/doctor to verify
```

### LLM failure

``` text
LLM unavailable
 ↓
deterministic questionnaire fallback
```

The system should degrade gracefully.

------------------------------------------------------------------------

# 47. Important Research Caveat

Medical handwriting OCR remains difficult.

Therefore:

> **Do not market OCR as perfectly accurate.**

The architecture should assume errors are possible and use: -
confidence - evidence - human verification - source-image access

This is one of the strongest arguments for an evidence-first
architecture.

------------------------------------------------------------------------

# 48. Current Strategic Recommendation

The best version of MediKiosk is NOT:

``` text
Chatbot + OCR + ABHA
```

It is:

``` text
              MEDIKIOSK
                  │
       First-mile clinical layer
                  │
       ┌──────────┴──────────┐
       │                     │
  Patient input         Existing records
       │                     │
 Voice / Touch          Scan / OCR
       │                     │
       └──────────┬──────────┘
                  ↓
           ClinicalFact
                  ↓
       Validation + Evidence
                  ↓
        Safety + Gap Detection
                  ↓
       Timeline + Summary
                  ↓
        Physician Verification
                  ↓
       Hospital / FHIR / ABDM
```

The key value is:

> **Turning fragmented patient information into structured, verifiable
> clinical information before the doctor sees the patient.**

------------------------------------------------------------------------

# 49. Immediate Next Action for an AI Working on the Existing Repo

When given this file plus the repository, the AI should NOT immediately
code.

It should first return:

### A. Current architecture

``` text
Frontend:
Backend:
Database:
AI:
OCR:
ASR:
TTS:
FHIR:
ABDM:
Auth:
Deployment:
```

### B. Existing workflow

``` text
Current patient journey:
Current doctor journey:
Current data lifecycle:
```

### C. Requirement matrix

``` text
PS requirement
→ existing code
→ implemented / partial / missing
→ recommended change
```

### D. Technical debt

Identify: - duplicate state models - unstructured LLM output - missing
validation - missing provenance - unsafe AI decisions - missing
persistence - weak error handling - missing tests - hardcoded values -
fake/mocked integrations - missing security

### E. Implementation plan

Produce a prioritized plan:

``` text
P0
 ↓
P1
 ↓
P2
 ↓
P3
```

Only then modify the repository.

------------------------------------------------------------------------

# 50. Final Mental Model

Keep this architecture in mind:

``` text
                ┌───────────────────────┐
                │       PATIENT         │
                └───────────┬───────────┘
                            │
                 Voice / Touch / OCR
                            │
                            ▼
                ┌───────────────────────┐
                │     AI INTERFACE      │
                │ ASR / LLM / OCR / TTS │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │     CLINICALFACT      │
                │ Structured truth      │
                └───────────┬───────────┘
                            │
               ┌────────────┼────────────┐
               ▼            ▼            ▼
           Validation     Safety       Evidence
               │            │            │
               └────────────┼────────────┘
                            ▼
                     Clinical Timeline
                            │
                            ▼
                    Physician Summary
                            │
                            ▼
                     DOCTOR REVIEW
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
             Hospital HIS          FHIR/ABDM
```

## The single most important principle

> **MediKiosk should be an intelligent first-mile clinical data layer,
> not an autonomous medical decision-maker.**

And:

> **The AI is not the product. The workflow is the product.**

------------------------------------------------------------------------

# Source / Reference Documents Used

Internal project context previously developed: - `SIH26047.pdf` ---
official problem statement supplied in the project context -
`MediKiosk_Full_Context_Handoff.md` -
`MediKiosk_Master_Build_Specification-1.md` -
`MediKiosk_Two_Developer_Execution_Plan.md` -
`MediKiosk_Android_Two_Developer_Execution_Plan.md` -
`MediKiosk_Architecture_Review_v2.md` -
`MediKiosk_Tech_Stack_Finalized.md` - `SIH26047.md`

Important internal evidence: - The SIH-specific implementations document
the structured clinical interview, OCR, timeline, doctor dashboard, and
FHIR-oriented architecture. - The master build specification explicitly
says MediKiosk should not replace doctors/EHRs, independently diagnose,
prescribe, or claim ABDM integration unless implemented. - The
two-developer plan prioritizes a vertical slice from patient input →
ClinicalFact → routing → doctor. - The architecture review emphasizes
token-based intake, audio purge, encrypted local storage, contradiction
preservation, and omnichannel ingestion.
