# MediKiosk — Master Project Definition, Existing-Solution Gap Analysis, Product Flow, MVP Scope, and Scale Plan

**Problem Statement:** SIH26047 — Patient Case-Taking Software  
**Proposed solution name:** MediKiosk  
**Primary mode:** Patient-facing digital clinical intake before consultation  
**Secondary mode:** Telephone/IVR backup for patients who cannot or do not want to use the digital interface  
**Document purpose:** Single source of truth for what the problem requires, what already exists, what is genuinely missing, what MediKiosk should build, and how the prototype should be demonstrated.

> **Important framing:** Do not pitch MediKiosk as "the world's first digital healthcare intake system" or "no such solution exists anywhere." Existing systems already cover parts of the workflow. The defensible claim is that MediKiosk combines those pieces into a patient-facing, first-mile clinical-intake workflow designed for Indian public-hospital realities: multilingual voice + touch, document digitization, structured history, accessibility, clinician verification, and integration-ready data exchange.

---

## 1. Source Problem — What SIH26047 Actually Requires

The supplied problem statement identifies four connected bottlenecks:

1. **Clinical history-taking bottleneck** — Indian public-hospital OPDs can be extremely high volume, leaving very little time for detailed history-taking. The problem statement describes consultation windows of roughly 2–5 minutes in many settings and notes the resulting risks of incomplete history, repeated questioning, missed comorbidities, and diagnostic error.
2. **Documentation fragmentation** — patients commonly carry paper prescriptions, laboratory reports, discharge summaries, and imaging from multiple providers. These are often handwritten, multilingual, unstructured, and chronologically disordered.
3. **First-mile digital-health gap** — ABDM/ABHA/FHIR infrastructure exists, but the problem statement says there is a gap before the clinical encounter: a patient-facing system that captures structured history and digitizes documents before the patient reaches the doctor.
4. **Accessibility gap** — a solution must work for elderly, low-literacy, rural, first-visit, and low-tech-comfort patients, including multilingual voice/touch interaction.

The document's precise requirement is a patient-facing platform that lets patients independently record comprehensive medical history through natural spoken conversation and guided touchscreen interaction, digitize existing physical medical documents, and generate a structured physician-ready clinical history summary integrated with the hospital information system and ABDM ecosystem before consultation.

### Core requirements extracted from the supplied statement

- Multilingual, multi-accent voice capture in noisy hospital environments.
- Guided touchscreen interaction.
- Adaptive questioning based on the complaint and prior answers.
- Clinical history structure: chief complaint, HPI, past medical/surgical history, drug/allergy history, family history, personal history, review of systems.
- AYUSH/Ayurveda mode with the required additional history fields.
- Red-flag detection with priority/triage escalation.
- OCR for printed and handwritten prescriptions, lab reports, and discharge summaries.
- Intelligent extraction of diagnoses, medications/doses, investigation values, and procedure/surgery history.
- Chronological organization of documents.
- Abnormal-value and possible interaction highlighting for clinician attention.
- Physician-ready summary.
- Physician can edit/confirm/reject the generated summary.
- Patient-facing local-language confirmation and physician-facing standardized summary.
- Consent-first design.
- Secure handling of health information.
- Integration path to HIS/EMR and ABHA/ABDM.
- Session cleanup of temporary data.

These requirements are all explicit in the supplied problem statement.

---

## 2. What the Problem Is NOT

MediKiosk should **not** become an unfocused "everything in healthcare" platform.

The system is not primarily:

- a diagnosis engine,
- a medical prescription generator,
- a hospital billing system,
- an insurance-claims platform,
- a generic chatbot,
- a social health app,
- a replacement for the doctor,
- a generic OCR scanner,
- or only an appointment/queue-management kiosk.

Those functions can be integrated later, but the SIH core is the **pre-consultation clinical intake workflow**.

---

# 3. Existing Solutions — What Already Exists

## 3.1 India: ABHA / ABDM

ABDM provides the digital-health infrastructure around ABHA identities, exchange/interoperability, and consent-driven health-information sharing. The supplied problem statement itself describes ABHA/FHIR/ABDM as existing infrastructure but identifies the first-mile capture problem as the gap.

**What it solves well:**

- Digital identity and health-record linkage ecosystem.
- Consent-aware data sharing architecture.
- Interoperability direction through FHIR and ABDM standards.

**What it does NOT by itself solve for SIH26047:**

- A conversational clinical history interview at a kiosk.
- Adaptive clinical questioning.
- Handwritten document understanding.
- A unified patient-history summary generated before consultation.

**Implication for MediKiosk:** ABDM should be treated as an integration target and digital-health backbone, not as a competitor to replace.

Official references:
- ABDM: https://abdm.gov.in/
- ABDM ecosystem / public information: https://abdm.gov.in/

---

## 3.2 India: ABHA-based Scan & Share

ABHA Scan & Share lets a patient scan a QR code and share the ABHA profile for quick OPD registration. The Government reported more than 2 crore OPD tokens by February 2024 and more than 4 crore by August 2024.

**What it solves:**

- Reduces registration friction.
- Speeds OPD token generation.
- Uses ABHA for a paperless administrative step.

**What it does not solve as the main objective of this SIH problem:**

- It is primarily registration/access workflow.
- It does not replace comprehensive clinical history-taking.
- It does not itself provide the multimodal clinical interview described in SIH26047.
- It does not become the medical-document-to-structured-history engine described here.

**MediKiosk relationship:** Complementary. MediKiosk can use the same ecosystem after identity/consent, then continue into clinical intake.

Reference: https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2009483&lang=2&reg=48

---

## 3.3 India: NextGen eHospital / Hospital Information Systems

NextGen eHospital already provides hospital-side capabilities such as registration, appointments, EHR, laboratory, radiology, pharmacy, billing, clinics, and more. NIC states that the platform supports standards including ABDM, FHIR, DICOM, LOINC, SNOMED CT, and ICD-10.

**What it solves:**

- Core hospital operations.
- Clinical record management.
- Department workflow.
- Interoperability and standards support.

**Gap relative to MediKiosk:**

The SIH opportunity is the **patient-side intake layer before consultation**: capturing history and previous documents in a way that reduces the cognitive/time burden on the physician.

Reference: https://www.nic.gov.in/project/nextgen-ehospital/

---

## 3.4 India: Existing Patient Apps / Tele-triage Chatbots

Patient apps and chatbots can collect symptoms, provide guidance, or support remote interactions.

**Typical strengths:**

- Familiar mobile interface.
- Self-service.
- Questionnaire/chat workflows.
- Remote accessibility.

**Problem for the SIH target population:**

The SIH document explicitly highlights smartphone literacy, connectivity, enrolment, and usability barriers for elderly, rural, low-literacy, and first-visit populations.

**MediKiosk advantage:**

- Physical/shared device.
- No personal smartphone requirement.
- Guided touch.
- Audio prompts.
- Multilingual voice.
- Staff-minimal flow.

---

## 3.5 India: Manual Nurse-led History / Triage Desk

Many hospitals rely on staff to collect information.

**Strength:** Human judgement and familiarity with local workflow.

**Weakness:**

- Human-resource bottleneck.
- Difficult to scale to thousands of OPD visits.
- Repeated data entry.
- Transcription burden.
- Same bottleneck moves instead of disappearing.

**MediKiosk position:** Automation should reduce repetitive collection, while leaving the clinician in control.

---

## 3.6 Generic OCR / Document Scanning

Standard scanners and OCR systems can convert an image into text.

But generic OCR is not the same as clinical document intelligence.

A useful clinical pipeline needs:

**Image → OCR → layout understanding → entity extraction → medical normalization → chronology → structured record → clinician review**

For example:

```text
"Metformin 500 mg twice daily"

should become

Medication: Metformin
Dose: 500 mg
Frequency: twice daily
Source: prior prescription
Date: extracted/confirmed date
Confidence: model confidence
```

The SIH requirement goes beyond flat image storage and asks for structured clinical content.

---

# 4. Existing Solutions Outside India

## 4.1 NHS Online Consultation Tools

NHS England documents three common approaches:

1. Questionnaire-based consultation.
2. Chatbot-style history-taking with questions changing based on prior answers.
3. Online messaging/free-text interaction.

Some tools combine these approaches. The NHS also uses online forms and red-flag pathways in patient-facing systems.

**What this proves:**

- Pre-consultation history capture is already a mature concept.
- Adaptive/questionnaire-based intake exists.
- Red-flag escalation exists in digital patient workflows.

**What MediKiosk must add for the SIH context:**

- Public-hospital kiosk workflow.
- Indian-language/Indian-accent focus.
- Low-literacy voice/touch mode.
- Local document ecosystem: handwritten prescriptions, Indian-language reports.
- ABDM/HIS integration path.

Official references:
- https://www.england.nhs.uk/long-read/online-consultation-tools/
- https://digital.nhs.uk/services/nhs-app/nhs-app-features/contact-your-gp-surgery-in-the-nhs-app

---

## 4.2 Oracle Health Patient Portal

Oracle Health Patient Portal supports pre-visit questionnaires, including health-history categories such as allergies, medications, procedures, conditions, immunizations, social history, and family history.

**What it proves:**

- Structured pre-visit history collection is already used in enterprise healthcare.
- Patient responses can be captured before a consultation.

Reference: https://docs.oracle.com/en/industries/health/health-patient-portal/hppug/complete-questionnaires.html

**MediKiosk differentiation:** physical kiosk + Indian multilingual voice/touch + document intelligence + first-mile government-hospital workflow.

---

# 5. Existing-Solution Comparison Matrix

| Capability | ABHA / ABDM | OPD Scan & Share | eHospital / HIS | Online consultation tools | Generic OCR | MediKiosk target |
|---|---|---|---|---|---|---|
| Digital identity | Yes | Yes | Usually via hospital systems | Varies | No | Yes / integration |
| OPD registration | Ecosystem | Strong | Strong | Varies | No | Optional |
| Clinical history intake | Not primary | No | Depends on deployment | Yes | No | **Core** |
| Adaptive questions | No | No | Usually not the core | Some tools | No | **Core** |
| Voice input | Not the core | No | Not the core | Some tools | No | **Core** |
| Touch input | Not the core | QR-led | Yes in some front desks | Yes | No | **Core** |
| Indian multilingual focus | Ecosystem-level | Limited to service design | Depends on deployment | Depends on vendor | Depends on OCR | **Core** |
| Handwritten medical OCR | No | No | Usually separate | Sometimes attachments | OCR only | **Core** |
| Clinical entity extraction | Not core | No | Existing EHR data | Varies | Usually weak | **Core** |
| Chronological document timeline | Not primary | No | EHR capability varies | Varies | No | **Core** |
| Red-flag routing | Not the main function | No | Hospital workflow may have triage | Yes in some tools | No | **Core, rule-based** |
| Physician-ready synthesis | Not primary | No | EHR contains records | Yes in some tools | No | **Core** |
| Physician editable/confirmable summary | N/A | N/A | Yes at EHR level | Often yes | No | **Core** |
| ABHA/FHIR integration | **Core ecosystem** | Yes | **Yes** | Depends | No | **Integration target** |
| No personal smartphone required | Yes, depending on service | Yes at QR station | Depends | Usually no | Yes | **Yes** |
| Telephone/IVR backup | No | No | Not the core | Some systems | No | **Secondary channel** |

### Key conclusion

The opportunity is not a single missing algorithm. It is the **integration of multiple partially solved capabilities into a single first-mile workflow**.

---

# 6. MediKiosk — Correct Product Definition

## Product statement

> MediKiosk is a patient-facing, multilingual clinical intake platform that collects a patient's current symptoms and medical history through voice and touch, digitizes previous medical documents, structures both sources into a physician-reviewable clinical summary, flags possible emergency symptoms for triage, and prepares integration-ready health information for the hospital and ABDM ecosystem before the consultation.

## Primary design principle

**The system prepares the doctor. It does not replace the doctor.**

All generated clinical content must remain:

- traceable to an input,
- editable,
- reviewable,
- and explicitly non-diagnostic unless a qualified clinical workflow later approves a separate regulated use case.

---

# 7. Correct Identity Model — Important Correction to the Current Idea

Do **not** build the system around:

> Aadhaar number = patient's medical-record primary key.

That is a poor architecture and creates unnecessary privacy/security risk.

Instead use:

```text
internal_patient_id
        |
        +---- ABHA ID (when available and consented)
        |
        +---- hospital_mrn / UHID (if available)
        |
        +---- verified mobile number
        |
        +---- optional external identifiers under controlled access
```

### ABHA creation

Do not implement "give name + phone = automatically generate ABHA" as if your app owns ABHA issuance.

For the prototype, provide:

- ABHA lookup/linking placeholder, or
- QR/official identity-link flow mock, or
- a synthetic ABHA identifier in the demo dataset.

For production, use official ABDM integration/consent mechanisms and the hospital's approved onboarding process.

### Aadhaar

Treat Aadhaar as an identity/onboarding input only where the approved workflow explicitly requires it. Do not store raw Aadhaar everywhere as the clinical record key.

---

# 8. Two-Mode Product Strategy

## Mode A — Primary: MediKiosk / Web + Touchscreen

```text
Patient arrives
    ↓
Identity / patient lookup
    ↓
Language selection
    ↓
Consent
    ↓
Current complaint
    ↓
Adaptive voice + touch history
    ↓
Red-flag rules
    ↓
Document scan/upload
    ↓
OCR + extraction + normalization
    ↓
Timeline
    ↓
Structured summary
    ↓
Patient confirmation
    ↓
Doctor portal
    ↓
Doctor review / edit / confirm
    ↓
HIS / ABDM integration layer
```

## Mode B — Backup: IVR / Telephone

Target user:

- very elderly patient,
- no smartphone,
- no touchscreen confidence,
- remote/basic-phone user,
- accessibility case.

Flow:

```text
Patient calls hospital number
        ↓
Language selection
        ↓
Identity verification
        ↓
Consent
        ↓
Voice questions
        ↓
Speech-to-text
        ↓
Same clinical history schema
        ↓
Same red-flag engine
        ↓
Same summary generator
        ↓
Same doctor portal
```

**Important architectural principle:** IVR must NOT create a second clinical database. Both channels write to the same backend data model.

---

# 9. Patient Portal — Required Inputs

## Identity / onboarding

- Full name
- Date of birth / age
- Sex (as required by hospital workflow)
- Mobile number
- Preferred language
- Address or locality if required by hospital
- Internal patient ID
- Hospital MRN/UHID if existing
- ABHA ID if available and consented
- Optional insurance/payer information if the hospital workflow needs it

## Clinical intake

- Chief complaint
- Symptom onset
- Duration
- Severity
- Location
- Character / quality
- Radiation
- Aggravating factors
- Relieving factors
- Associated symptoms
- Fever
- Pain score if appropriate
- Relevant past medical history
- Past surgical history
- Current medication
- Allergies
- Family history
- Personal history
- Review of systems

## Documents

- Prescription
- Laboratory report
- Discharge summary
- Imaging/report document
- Medication list
- Procedure/surgery record

## Optional multimodal patient evidence

For the prototype, allow:

- image of visible external symptom/injury, if clinically appropriate,
- voice note,
- scanned document.

**Do not let an image module claim a diagnosis.** The prototype should label these as patient-provided evidence for clinician review.

---

# 10. Doctor Portal — Required Inputs

## Doctor identity

- Doctor ID
- Name
- Specialty
- Department
- Hospital
- Role
- Verified credential placeholder for prototype

## Doctor queue

Show:

- Patient name
- Patient ID
- Queue/encounter number
- Chief complaint
- Red-flag status
- Completion status
- Time submitted

## Patient clinical view

1. Current complaint
2. Structured HPI
3. Previous medical history
4. Surgical history
5. Medicines
6. Allergies
7. Family history
8. Personal history
9. Review of systems
10. Previous investigations
11. Document timeline
12. Extracted values
13. Patient images/evidence
14. AI-generated summary
15. Source traceability
16. Consent status
17. ABHA link status

## Doctor actions

- Edit
- Confirm
- Reject section
- Add note
- Mark verified
- Escalate to triage
- Request clarification
- Upload prescription
- Complete encounter

---

# 11. Source Traceability — A Major Feature for Trust

Every extracted/generated field should ideally have a source.

Example:

```json
{
  "condition": "Diabetes mellitus",
  "value": true,
  "source": "patient_voice",
  "source_reference": "session_01_turn_07",
  "confidence": 0.94,
  "clinician_verified": false
}
```

For document extraction:

```json
{
  "medication": "Metformin",
  "dose": "500 mg",
  "frequency": "BID",
  "source": "document",
  "document_id": "DOC-001",
  "page": 1,
  "confidence": 0.91
}
```

This is much safer than showing an AI summary with no provenance.

---

# 12. Red-Flag Design — Use Rules First, AI Second

For the SIH prototype, do not allow an LLM alone to decide emergencies.

Use a deterministic rule layer first.

Example:

```text
Chest pain + severe breathlessness
        ↓
priority = HIGH
        ↓
show emergency message
        ↓
notify triage dashboard
        ↓
continue only if workflow permits
```

Possible prototype red-flag rules:

- severe chest pain + dyspnea
- stroke-like symptoms
- severe bleeding
- loss of consciousness
- severe respiratory distress
- anaphylaxis-like symptoms

The model can help normalize the wording, but deterministic business rules should decide the prototype priority state.

---

# 13. AYUSH Mode

The SIH statement specifically adds AYUSH/Ayurvedic assessment complexity.

Create a separate configurable intake profile:

```text
AYUSH MODE

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
Ahara-Vihara
Nidana
Samprapti
```

Do not hard-code these into every allopathic flow.

The history engine should load a **clinical profile**:

```text
profile = GENERAL_MEDICINE
profile = AYUSH_AYURVEDA
profile = CARDIOLOGY
profile = ORTHOPEDICS
...
```

This makes the system scalable.

---

# 14. Proposed Technical Architecture

```text
                 ┌─────────────────────┐
                 │  Patient Kiosk UI   │
                 │ React / Flutter Web │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │ API Gateway / BFF    │
                 │ FastAPI              │
                 └──────────┬──────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   Conversation       Document AI       Identity/Consent
     Service             Service             Service
          │                 │                 │
          ▼                 ▼                 ▼
       STT/TTS           OCR/vision          ABHA/HIS
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                  Clinical Structuring
                            │
                            ▼
                  Safety / Rule Engine
                            │
                            ▼
                     Summary Engine
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
        Doctor Dashboard            IVR Gateway
               │                         │
               └────────────┬────────────┘
                            ▼
                      PostgreSQL
                     + object store
```

---

# 15. Recommended Prototype Technology Stack

## Frontend

Preferred for the existing MediKiosk project:

- Flutter for the kiosk/mobile-style patient UI.
- Responsive web doctor dashboard can be React if the team already has a React dashboard.

If your existing project already has Flutter + FastAPI, keep it rather than rewriting the stack.

## Backend

- FastAPI
- Python
- Pydantic
- SQLAlchemy
- PostgreSQL
- Redis optional for session/queue events
- WebSocket for live queue/doctor updates

## Authentication

- Patient: phone/OTP or demo patient ID flow.
- Doctor: username/password for prototype, with role-based access control.
- Production: hospital-approved identity, stronger authentication, official ABHA/consent integration.

---

# 16. AI Model Recommendations for the Prototype

## 16.1 Speech-to-text

**Recommended Indian-language option:** Sarvam Speech-to-Text (Saaras family), because the current API documentation explicitly supports Indian languages, code-mixing, transcription and multiple output modes.

Prototype choice:

```text
STT_PROVIDER = sarvam
STT_MODEL = saaras:v4 (or currently supported stable model)
```

Keep the service behind an interface:

```python
class SpeechToTextProvider:
    async def transcribe(...): ...
```

So the provider can be changed without rewriting the clinical logic.

Reference: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe

## 16.2 Text-to-speech

Sarvam Bulbul is suitable for Indian-language prompts if API access is available.

Alternative: platform/cloud TTS provider behind the same adapter.

## 16.3 LLM / clinical structuring

Use a general-purpose model for **structuring and summarization**, not diagnosis.

A strong prototype option is **Gemini 2.5 Flash** because Google's current documentation lists image/audio/text input and structured outputs, which fit document and clinical-summary workflows.

Reference: https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash

Alternative Indian-language reasoning option: Sarvam-105B, depending on available access and evaluation.

## 16.4 Document OCR

For the fastest prototype:

- Cloud document AI / vision model if allowed with synthetic data.
- Sarvam Vision for Indian-language document digitization.
- PaddleOCR / PP-Structure when you want a local/open deployment path.

PaddleOCR's PP-Structure supports layout analysis, table recognition, OCR, and document-structure workflows.

Reference: https://www.paddleocr.ai/main/en/version2.x/ppstructure/overview.html

**Do not rely on basic Tesseract alone for handwritten prescriptions.** Its own documentation warns that it is designed primarily for printed text.

Reference: https://github.com/tesseract-ocr/tesseract/wiki/FAQ

---

# 17. LLM Responsibilities vs Non-LLM Responsibilities

## LLM should do

- Convert patient language into normalized concepts.
- Generate the next question from a constrained clinical question tree.
- Summarize structured history.
- Explain extracted information in patient-friendly language.
- Normalize synonyms.

## LLM should NOT do alone

- Decide emergency priority.
- Issue a prescription.
- Make a final diagnosis.
- Decide insurance eligibility.
- Decide whether a patient is medically fit.
- Write irreversible data into a clinical record without validation.

Use a combination of:

**rules + schema + LLM + validator + clinician review**

---

# 18. Data Model — Minimal MVP

### Patient

```text
id
name
dob
age
sex
mobile
preferred_language
internal_patient_id
abha_id_nullable
hospital_mrn_nullable
consent_status
created_at
updated_at
```

### Encounter

```text
id
patient_id
hospital_id
department
specialty
status
priority
started_at
completed_at
```

### HistoryAnswer

```text
id
encounter_id
section
question_id
question_text
answer_text
answer_structured
source
source_reference
confidence
verified_by_doctor
```

### Document

```text
id
patient_id
encounter_id
file_uri
file_type
document_type
captured_at
document_date
ocr_text
extracted_json
confidence
verified
```

### ClinicalSummary

```text
id
encounter_id
summary_json
summary_text
model_version
created_at
verified_by_doctor
verified_at
```

### Doctor

```text
id
name
specialty
department
hospital
role
is_verified
```

### ConsentRecord

```text
id
patient_id
purpose
scope
status
given_at
withdrawn_at
consent_method
```

### AuditEvent

```text
id
actor_id
actor_type
action
resource_type
resource_id
timestamp
metadata
```

---

# 19. FHIR-Oriented Integration Strategy

For the prototype, do not claim full ABDM conformance unless you actually implement and validate the relevant profiles in the sandbox.

Instead create an **FHIR adapter layer**.

Potential mappings:

| MediKiosk object | FHIR concept |
|---|---|
| Patient | Patient |
| Encounter | Encounter |
| Structured questionnaire answer | QuestionnaireResponse |
| Lab value | Observation |
| Clinical condition | Condition |
| Medication information | MedicationStatement / MedicationRequest depending on workflow |
| Uploaded report | DocumentReference / Binary as appropriate |
| Clinician | Practitioner / PractitionerRole |
| Summary | Composition or another approved clinical-document representation depending on implementation |

FHIR `QuestionnaireResponse` is explicitly designed to represent a structured set of questions and answers, making it a useful basis for the intake layer.

Reference: https://hl7.org/fhir/questionnaireresponse.html

---

# 20. Dataset Strategy — Do NOT Start With Real Patient Data

For the SIH prototype, use **synthetic data only**.

Create:

### Patient profiles

At least 30–50 synthetic patients across:

- Tamil
- Hindi
- English
- Telugu
- Bengali or another Indian language

### Clinical categories

- fever
- cough
- chest pain
- abdominal pain
- headache
- diabetes follow-up
- hypertension follow-up
- musculoskeletal complaint
- skin complaint
- common AYUSH intake case

### Documents

Generate synthetic:

- prescriptions,
- CBC reports,
- glucose/HbA1c reports,
- discharge summaries,
- medication lists,
- handwritten-style mock prescriptions.

### Annotation fields

For every sample document store expected values:

```json
{
  "patient_id": "P-001",
  "document_type": "prescription",
  "medications": [
    {
      "name": "Metformin",
      "dose": "500 mg",
      "frequency": "BID"
    }
  ]
}
```

### Why this is enough for SIH

The prototype is demonstrating the **workflow and integration architecture**, not claiming regulatory-grade diagnostic performance.

---

# 21. Prototype Demo Dataset — Recommended Seed

Use a small fixed dataset so the demo is deterministic.

### Demo Patient 001

```text
Name: Lakshmi Devi
Age: 58
Language: Tamil
Complaint: Chest pain for 3 days
Past history: Diabetes, hypertension
Medication: Metformin, Amlodipine
Previous report: HbA1c 7.8%
```

### Demo flow

```text
Patient selects Tamil
        ↓
Speaks complaint
        ↓
STT → Tamil text
        ↓
Question engine asks follow-ups
        ↓
Patient answers by voice
        ↓
Patient scans old prescription
        ↓
OCR extracts medication
        ↓
Timeline created
        ↓
Chest-pain red-flag rule activates if criteria are met
        ↓
Doctor dashboard displays structured summary
        ↓
Doctor edits/approves
```

This is enough to show the entire pipeline without building every hospital feature.

---

# 22. What to Build for the SIH Prototype

## Must-have

### Patient side

- language selection
- consent screen
- patient identification
- voice input
- text/touch input
- adaptive questions
- document upload/camera capture
- extracted history preview
- completion screen

### Doctor side

- login
- queue
- patient list
- red-flag badge
- structured history
- document timeline
- extracted values
- clinician edit/confirm
- final summary

### Backend

- patient API
- encounter API
- conversation session API
- document API
- extraction API
- summary API
- doctor API
- audit log API

### AI

- STT
- TTS
- LLM structuring
- OCR
- rule-based red flags

### Integration demo

- mock FHIR export
- mock ABHA link
- mock HIS push

---

# 23. What NOT to Build First

Do not spend the first sprint on:

- real insurance claim processing,
- real Aadhaar integration,
- production ABHA registration,
- national-scale telephony deployment,
- fully autonomous diagnosis,
- advanced medical image diagnosis,
- 20+ hospital departments,
- real-world clinical deployment.

Those are scale/production phases.

---

# 24. MVP vs Scale Roadmap

## Phase 1 — SIH demo

```text
1 language or 2–3 languages
+
voice
+
touch
+
1–2 clinical complaint pathways
+
OCR
+
structured summary
+
doctor dashboard
+
synthetic FHIR export
+
mock ABHA
+
synthetic data
```

## Phase 2 — Pilot

- more languages
- noisy-environment ASR evaluation
- multiple specialties
- real hospital workflow integration
- approved identity and consent integration
- auditability
- better document extraction
- IVR pilot

## Phase 3 — Scale

- regional language expansion
- multiple hospitals
- offline/edge capabilities where needed
- load balancing
- observability
- production security
- formal clinical safety evaluation
- validated FHIR/ABDM integration
- formal procurement/compliance work

---

# 25. Scale Architecture

For scale:

```text
CDN / Edge
   ↓
API Gateway
   ↓
Auth Service
   ↓
Conversation Service      Document Service
        ↓                       ↓
   Queue/Event Bus          OCR workers
        ↓                       ↓
Clinical Structuring       Extraction workers
        \                       /
         \                     /
          └────── Summary ─────┘
                    ↓
              PostgreSQL
                    +
              Object Storage
                    +
             Audit / SIEM
                    +
             FHIR Adapter
                    +
             HIS Connectors
```

Use asynchronous workers for OCR/document processing so a large queue of scans does not block the patient UI.

---

# 26. Security and Privacy — Non-negotiable

Health information is highly sensitive.

The design must include:

- explicit consent,
- least-privilege access,
- encryption in transit,
- encryption at rest,
- audit logs,
- role-based access control,
- short-lived temporary files,
- data retention policy,
- deletion workflow,
- session timeout,
- no PHI in client logs,
- no sensitive data in debug output,
- secure secrets management.

India's Digital Personal Data Protection Act, 2023 is enacted law, and the Digital Personal Data Protection Rules, 2025 were notified with a phased commencement timeline. Your production design therefore needs a proper legal/compliance review rather than treating privacy as a UI checkbox.

Official references:
- DPDP Act 2023: https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf
- DPDP Rules 2025: https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf

WHO also emphasizes human autonomy, safety, transparency, accountability, inclusiveness, and equity for AI in health.

Reference: https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-artificial-intelligence-ai-in-health-and-six-guiding-principles-for-its-design-and-use

---

# 27. Most Important Product Principle

### MediKiosk is not an "AI doctor."

It is a:

> **Clinical intake and information-preparation system.**

Its job is:

```text
Ask better questions
+
Capture more complete information
+
Read previous documents
+
Structure the data
+
Highlight important signals
+
Give the doctor a better starting point
```

The doctor remains responsible for clinical reasoning and decisions.

---

# 28. The Strong SIH Pitch

## Problem

> In high-volume Indian OPDs, doctors receive patients with only minutes to understand the complaint, reconstruct history, and review fragmented paper records.

## Existing ecosystem

> India already has digital-health infrastructure, hospital information systems, registration systems, and digital consultation tools. Internationally, digital questionnaires and adaptive online history-taking are also established.

## Gap

> What remains difficult is the first-mile, patient-facing workflow for multilingual, low-literacy, elderly, first-visit users that combines voice/touch history capture, medical document digitization, structured summarization, red-flag routing, and integration-ready output before the clinical encounter.

## Solution

> MediKiosk creates that bridge.

## Why it matters

> The doctor spends less time collecting repetitive information and more time examining, reasoning, counselling, and making the final clinical decision.

---

# 29. Final End-to-End Flow

```text
                 PATIENT ARRIVES
                       |
                       v
                IDENTIFY / LOGIN
                       |
                       v
                  LANGUAGE
                       |
                       v
                    CONSENT
                       |
                       v
          +------------+------------+
          |                         |
          v                         v
     VOICE INPUT               TOUCH INPUT
          |                         |
          +------------+------------+
                       v
              ADAPTIVE HISTORY
                       |
                       v
                RED-FLAG RULES
                       |
             +---------+---------+
             |                   |
          NORMAL               ALERT
             |                   |
             v                   v
       CONTINUE INTAKE      TRIAGE ALERT
             |
             v
        DOCUMENT SCAN
             |
             v
       OCR / DOCUMENT AI
             |
             v
       ENTITY EXTRACTION
             |
             v
       CHRONOLOGICAL VIEW
             |
             v
     STRUCTURED HISTORY MODEL
             |
             v
     CLINICAL SUMMARY ENGINE
             |
             v
       PATIENT REVIEW
             |
             v
       DOCTOR DASHBOARD
             |
             v
      EDIT / CONFIRM / REJECT
             |
             v
       HIS / FHIR ADAPTER
             |
             v
       ABDM / RECORD LINKAGE
```

### Secondary IVR channel

```text
PHONE CALL
   ↓
LANGUAGE
   ↓
IDENTITY + CONSENT
   ↓
VOICE HISTORY
   ↓
STT
   ↓
SAME CLINICAL HISTORY SCHEMA
   ↓
SAME RED-FLAG ENGINE
   ↓
SAME SUMMARY
   ↓
SAME DOCTOR PORTAL
```

---

# 30. Final Positioning Statement

> **MediKiosk does not try to replace the hospital, ABHA, HIS, doctor, or patient portal. It acts as the intelligent first-mile clinical intake layer that connects the patient to those systems more effectively.**

That is the most defensible and technically coherent interpretation of SIH26047.

---

# 31. Sources

1. SIH26047 supplied problem statement — authoritative project brief supplied by the user.
2. ABHA Scan & Share milestone — Press Information Bureau / National Health Authority: https://www.pib.gov.in/Pressreleaseshare.aspx?PRID=2009483&lang=2&reg=48
3. NextGen eHospital — National Informatics Centre: https://www.nic.gov.in/project/nextgen-ehospital/
4. NHS England — Online consultation tools: https://www.england.nhs.uk/long-read/online-consultation-tools/
5. NHS England Digital — Online consultation/red-flag pathway: https://digital.nhs.uk/services/nhs-app/nhs-app-features/contact-your-gp-surgery-in-the-nhs-app
6. Oracle Health Patient Portal — Questionnaires: https://docs.oracle.com/en/industries/health/health-patient-portal/hppug/complete-questionnaires.html
7. HL7 FHIR QuestionnaireResponse: https://hl7.org/fhir/questionnaireresponse.html
8. Sarvam Speech-to-Text documentation: https://docs.sarvam.ai/api-reference/speech-to-text/transcribe
9. Sarvam India-language stack: https://docs.sarvam.ai/api/getting-started/building-for-india
10. Sarvam model documentation: https://docs.sarvam.ai/api/getting-started/models
11. Google Gemini 2.5 Flash: https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash
12. PaddleOCR PP-Structure: https://www.paddleocr.ai/main/en/version2.x/ppstructure/overview.html
13. Tesseract FAQ: https://github.com/tesseract-ocr/tesseract/wiki/FAQ
14. Digital Personal Data Protection Act, 2023: https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf
15. Digital Personal Data Protection Rules, 2025: https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf
16. WHO — Ethics and governance of AI for health: https://www.who.int/news/item/28-06-2021-who-issues-first-global-report-on-artificial-intelligence-ai-in-health-and-six-guiding-principles-for-its-design-and-use
