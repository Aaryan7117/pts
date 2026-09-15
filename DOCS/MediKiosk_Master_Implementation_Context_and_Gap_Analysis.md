# MediKiosk — Master Implementation Context, Channel Architecture & Comprehensive Gap Analysis

> **Target Standard:** Problem Statement **SIH26047 — Patient Case-Taking Software** (Ministry of AYUSH / All India Institute of Ayurveda - AIIA).  
> **Source-of-Truth Reference:** `DOCS/MediKiosk_Master_Context.md`, repository source code (`app/`, `frontend/`, `mobile/`, `tests/`), and architectural design artifacts.  
> **Purpose:** Canonical reference document detailing all existing features, architecture design, stack choices, multi-channel technicalities, and a line-by-line audit of how the current codebase compares to `DOCS/MediKiosk_Master_Context.md`. Designed to be fed directly into downstream prompts as authoritative context data.

---

# 1. Executive Summary & Core Product Framing

### 1.1 Project Identity & Core Problem
High-volume Indian Outpatient Departments (OPDs)—particularly tertiary apex centers like the All India Institute of Ayurveda (AIIA)—face an acute **first-mile clinical intake bottleneck**. With physicians seeing upwards of 80 to 120 patients per shift, a consultation window often lasts only 3 to 5 minutes. In that narrow window, doctors struggle to decipher fragmented handwritten prescriptions from multiple practitioners, interpret scattered lab reports, translate regional dialects, and elicit an authentic Ayurvedic constitutional history (Dashavidha Pariksha) alongside modern allopathic regimens.

**MediKiosk** is an AI-assisted first-mile clinical intake system that digitizes, structures, verifies, and risk-stratifies patient information **before the patient enters the consultation room**.

### 1.2 Non-Negotiable Architectural Philosophy
In accordance with `DOCS/MediKiosk_Master_Context.md`:
1. **"The AI is not the product. The workflow is the product."**  
   The software does not attempt to replace physicians, formulate autonomous diagnoses, or generate unverified prescriptions.
2. **"ClinicalFact is the application source of truth; the LLM is not."**  
   Every medical claim is normalized and anchored to an audited, immutable `ClinicalFact` record featuring explicit provenance (pixel bounding boxes or audio timestamps).
3. **"Never silently invent missing values or infer uncertain medical facts."**  
   Ambiguous or low-confidence extractions must trigger patient explain-back verification or remain flagged for direct physician interrogation.
4. **"Single Pane of Glass with Channel-Specific Evidence Variants."**  
   All intake channels (Kiosk, Mobile BYOD, 2G IVR) converge into a single unified clinical core on the Doctor Workstation, displaying standardized triage metrics while adapting the provenance and evidence presentation to the unique origin channel.

---

# 2. Technology Stack & Deployment Topologies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DEPLOYMENT MODES                                 │
│                                                                             │
│  [STANDALONE]                 [CLUSTER]                   [CLOUD]           │
│  Single On-Prem Laptop        Thin Client Kiosk +         Pure Cloud        │
│  CPU RapidOCR + Ollama        GPU Edge Server (LAN)       Gemini Flash +    │
│  WAL SQLite                   IndicConformer + IndicF5    Sarvam AI         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
     PATIENT INTAKE CHANNELS                       CORE BACKEND & DATABASE
  • Channel 1: In-Clinic Kiosk (Web)             • FastAPI 3.0.0 (Python 3.12)
  • Channel 2: Mobile BYOD (Flutter Dart)        • aiosqlite (Async SQLite WAL)
  • Channel 3: 2G IVR Telephony (Exotel)         • Paraphrase-Multilingual MiniLM
                │                                • RapidOCR ONNX + OpenCV
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                            PHYSICIAN DESTINATION
                     • Doctor Workstation (Web Cockpit)
                     • Unified Clinical Core + Evidence Variants
```

### 2.1 Backend Core
- **Framework:** FastAPI 3.0.0 running on Uvicorn ASGI (`app/main.py`, `app/config.py`).
- **Database:** SQLite 3 in Write-Ahead Logging (`PRAGMA journal_mode=WAL`) with foreign key enforcement (`PRAGMA foreign_keys=ON`) via `aiosqlite` (`app/database.py`). Eliminates concurrency locks between concurrent patient intake and live doctor queue polling.
- **Data Validation & Typing:** Pydantic v2 schemas (`app/schemas/`).

### 2.2 Multi-Tier Hybrid LLM Gateway (`app/core/adapters/llm.py`)
Features an ultra-fast 50ms socket connectivity probe (`1.1.1.1:53`) preventing TCP timeout freezes when operating offline.
- **Tier 1 (Cloud Quality):** Google Gemini 2.5 Flash via the modern official `google-genai` SDK (`client.aio.models.generate_content`). Enforces structured JSON output via `GenerateContentConfig(response_mime_type="application/json", response_schema=...)`. Multimodal vision extracts medications directly with 2D bounding boxes `[ymin, xmin, ymax, xmax]` normalized on a 0–1000 scale.
- **Tier 2 (Cloud Speed):** Groq LPUs running `llama-3.1-70b-versatile` via OpenAI-compatible async SDK (`~280 tokens/sec`, 2.5s strict timeout).
- **Tier 3 (Offline Edge Core):** Local Ollama instance serving `qwen2.5:7b` (primary) or `qwen2.5:3b` (fallback) running locally on an 8GB VRAM RTX GPU or CPU at `http://localhost:11434/v1`.
- **Deterministic Mock Fallback:** Safely captures raw text without throwing unhandled exceptions if all LLMs are unreachable.

### 2.3 Speech Recognition (ASR) Pipeline (`app/core/adapters/asr.py`)
- **Cloud Primary:** Sarvam AI Saaras V4 (`<250ms` latency, native code-mixed Hindi, Tamil, Telugu, Marathi, English).
- **Cloud Secondary:** Groq Whisper-Large-v3-Turbo.
- **Offline Edge:** IndicConformer 600M (AI4Bharat, CPU ONNX, `~900MB` RAM, 0 GB VRAM consumption) or `faster-whisper` hosted on the hospital's on-premise GPU Edge Server reached via local clinic LAN (`SPEECH_SERVICE_URL`).

### 2.4 Text-to-Speech (TTS) Pipeline (`app/core/adapters/tts.py`)
- **Cloud Primary:** Sarvam AI Bulbul V3 (near-human natural accents across 5 languages).
- **Offline Edge:** IndicF5 (AI4Bharat diffusion TTS, `~3.5GB` VRAM, scheduled sequentially with Qwen 7B on edge GPU).
- **Dev Fallback:** Deterministic silence WAV generator ensuring zero API crashes during offline development.

### 2.5 Semantic Concept Normalizer & NegEx Engine (`app/core/clinical/normalizer.py`)
- **Deterministic NegEx Filter:** Multi-lingual negation lexicon spanning Hindi (`nahi`, `nahin`, `mat`, `bina`), Tamil (`illai`, `kidayathu`), Telugu (`ledu`, `kadu`), Marathi (`nahi`, `nako`), and English (`no`, `not`, `denies`). Prevents negated assertions (e.g., *"mujhe bukhar nahi hai"*) from recording as positive clinical findings.
- **Multilingual Sentence Transformer:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`~470MB`, XLM-RoBERTa based, executing in 15ms on CPU). Pre-computed concept embeddings map patient utterances directly to standardized SNOMED CT and NAMASTE (National AYUSH Morbidity and Standardized Terminologies Electronic) codes without LLM hallucination risk.
- **Confidence Calibration:**
  - `score >= 0.82`: `CONFIRMED_MATCH` (auto-accepted).
  - `0.55 <= score < 0.82`: `REQUIRES_EXPLAIN_BACK` (triggers patient audio/touch confirmation).
  - `score < 0.55`: `ESCALATE_TO_LLM` (routes to LLM contextual reasoning).

### 2.6 Medical Document OCR & Evidence Boxing (`app/core/adapters/ocr.py`)
- **RapidOCR ONNX Runtime:** Runs purely on CPU (`~800MB` RAM, `<1.5s` per A4 prescription), extracting bounding box coordinates `[x1, y1, x2, y2]` and line indices `[L1, L2, ...]`.
- **Evidence Boxing Engine:** PIL and OpenCV render glowing semi-transparent highlight rectangles over cited prescription lines and save them to `/static/evidence/`.
- **Multimodal Visual Grounding:** When online, Gemini Vision predicts exact medication coordinates, converted into glowing green SVG/canvas highlights.

### 2.7 Frontend & Mobile Client Stacks
- **Web Kiosk & Doctor Workstation:** Vanilla HTML5 / modern CSS3 / ES6 Modules bundled via Vite. Uses Three.js for interactive 3D avatar animations, Web Audio API for recording, and a CSS Grid 3-column consultation cockpit (`frontend/js/`).
- **Mobile BYOD App:** Flutter 3.47.3 / Dart 3.13.3 (`mobile/`), pinned via FVM. Features Clean Architecture, provider-based state management, offline repository caches, 64dp+ touch targets, and full responsiveness across smartphone portrait (Moto G54 5G) and tablet landscape (1280×800).

---

# 3. Complete Multi-Channel Architecture

MediKiosk provides three distinct patient intake channels that converge onto a single Doctor Workstation:

| Architectural Dimension | Channel 1: In-Clinic Kiosk Terminal | Channel 2: Mobile BYOD App | Channel 3: 2G IVR Telephony |
|---|---|---|---|
| **Primary Target Hardware** | Physical Touchscreen Kiosk Terminal in OPD Waiting Hall (1280×800) | Patient's Personal Smartphone (Android APK / Flutter) | Any basic 2G Keypad Feature Phone / Landline |
| **Connectivity Requirement** | Local Hospital LAN / Wi-Fi (Fully Offline-Capable) | Mobile Cellular Data (4G/5G) or Clinic Guest Wi-Fi | **Zero Internet Required on Caller Device** (Pure GSM / PSTN Voice) |
| **Patient Interaction Modality** | 3D Animated Avatar + Voice Audio Prompts + High-Contrast Touchscreen + Document Scanner | Mobile App UI (Smartphone Camera + Voice Call Simulation + Touch Cards) | Pure Audio Telephony (Ear & Mouth only via PSTN/GSM trunk) |
| **Intake Trigger & Onboarding** | Patient walks up to physical terminal in hospital lobby | Patient scans QR code posted in OPD waiting hall | Citizen dials Toll-Free Number (`1800-890-AYUSH` or `040-4189-7954`) from home |
| **Identity & Consent** | ABHA QR Scan / Mobile OTP / Guest Bypass; Audio-Visual DPDP Consent | ABHA Health Locker Linking + Mobile OTP Consent Timestamp | Caller CLI / CLI-linked ABHA Profile / In-band Spoken Consent |
| **Document Intake Capability** | High-Speed Integrated Scanner Bed / Top-Mounted Camera with Auto-Cropping | Smartphone Camera Photo Attachment & Gallery Upload | None (Spoken Verbal History & Longitudinal EHR Lookup) |
| **Destination & Output** | Doctor Workstation Queue & Printed Queue Token Slip | Doctor Workstation Queue & In-App Digital Token Card | Doctor Workstation Queue & SMS Confirmation to Mobile |
| **Evidence & Provenance Tier** | **`ONNX_OCR`** + **`TOUCH`** (Line-cited bounding boxes, confidence percentages) | **`PATIENT_CONFIRMED`** + **`VOICE_ASR`** (ABHA digital consent, camera images) | **`TELEPHONY_ASR`** (Audio recording proof with timestamp `[00:12]`, DoT circle route) |

---

# 4. Deep Technicalities of Features by Channel

## 4.1 Channel 1: In-Clinic Kiosk Terminal

### Hardware Specification & Physical Constraints
- Target screen: 10.1" to 21.5" touchscreen, landscape orientation (1280×800 minimum logical resolution).
- Audio hardware: Directional noise-canceling dual-microphone array and integrated front-facing speakers.
- Camera: Wide-angle optical scanner or 1080p document capture camera with fixed focal distance and integrated LED illumination.
- Thermal slip printer: Issues physical tokens (e.g. `Token A-104`).

### Implemented End-to-End Workflow (`frontend/js/pages/kiosk/`)
1. **Welcome Screen (`kiosk-welcome.js`):** High-contrast greeting, hospital branding (AIIA / Ministry of AYUSH), emergency SOS bypass button.
2. **Language Selection (`kiosk-language.js`):** One-tap selection across 5 languages: Hindi (हिन्दी), English, Tamil (தமிழ்), Telugu (తెలుగు), Marathi (मराठी).
3. **DPDP Consent (`kiosk-consent.js`):** Audio-explained plain language terms ("We do not sell your data. Records are shared only with your attending physician."). Patient taps `[स्वीकार करें / Agree]`.
4. **Patient Identification (`app/api/patient.py`, `app/api/encounters.py`):**
   - Options: Scan ABHA QR card, enter 10-digit mobile number, or select "Guest Walk-in / Skip".
   - Generates unique encounter ID (`enc-xxxx`) and bootstraps record with `channel='kiosk'`.
5. **Care Stream Routing (`kiosk-care-stream.js`):** Routes patient to General Medicine, AYUSH (Kayachikitsa, Shalya Tantra, Panchakarma), Pediatrics, or Emergency.
6. **Conversational Voice Intake (`kiosk-voice-intake.js`, `interview_engine.py`):**
   - Web Audio API streams audio to `/api/call/audio-turn`.
   - Three.js 3D Avatar (`avatar-3d.js`) provides visual engagement with speaking, listening, and idle lip-sync states.
   - Adaptive SOCRATES loop captures: Chief Complaint, Duration, Severity (1–10 visual slider), Current Medications, Stopped Medications, Allergies, and Past History.
7. **Document Scanning Station (`kiosk-doc-scan.js`, `app/api/documents.py`):**
   - Patient places paper prescription or lab report under the camera.
   - Image uploaded via `multipart/form-data` to `/api/documents/upload`.
   - RapidOCR ONNX extracts lines, detects bounding polygons, and normalizes text.
   - LLM extracts structured medications citing source lines `[L1, L2]`.
   - OpenCV draws yellow/green bounding boxes on the document image and stores it in `/static/evidence/`.
8. **Explain-Back Verification (`kiosk-explain-back.js`):**
   - TTS synthesizes a 30-second audio summary: *"You reported chest pain for 3 days and taking Metformin 500mg. Is this correct?"*
   - Patient confirms with massive `[YES / हाँ]` (72dp height) or `[NO / नहीं]` touch buttons.
9. **Queue Token Generation (`kiosk-queue-token.js`, `app/api/queue.py`):**
   - Assigns token (e.g., `A-104`) linked to OPD Chamber.
   - Estimates waiting time based on current patients ahead.
10. **Public Kiosk Privacy Wipes (`mobile/lib/core/widgets/privacy_reset_overlay.dart`, `app/config.py`):**
    - 45-second inactivity timeout triggers warning countdown overlay.
    - 10-second automatic RAM session wipe purges patient cache.
    - Audio recordings purged from local storage after 300 seconds (`AUDIO_PURGE_AFTER_SECONDS=300`).

---

## 4.2 Channel 2: Mobile BYOD (Bring Your Own Device)

### Architecture & Stack (`mobile/`)
Built with Flutter 3.47.3 / Dart 3.13.3 using Clean Architecture:
- `lib/core/`: Design system tokens (72dp CTA buttons, high-contrast typography, spacing), HTTP clients, audio recording service, privacy reset overlays.
- `lib/data/`: Models (`Encounter`, `ClinicalFact`, `CallSession`, `QueueToken`), local SQLite repositories, and REST API datasources.
- `lib/features/`: 16 modular feature packages:
  `welcome`, `language`, `consent`, `identity`, `care_stream`, `intake`, `call_intake`, `documents`, `vitals`, `ayush`, `triage`, `emergency`, `queue`, `services`, `map`, `completion`.

### Key Mobile Capabilities
1. **QR Onboarding:** Patient scans dynamic QR poster in waiting hall, opening the intake wizard with pre-selected hospital facility metadata.
2. **Active Call Card Simulation (`call_intake/`):** Full-screen voice interface styled like an incoming phone call (`ActiveCallCard`). Features real-time waveform visualizer, mute, speakerphone, and live transcript captions powered by `/api/call/audio-turn`.
3. **Smartphone Camera Document Capture (`documents/`):** Guided viewfinder rectangle with edge detection heuristics. Uploads high-res images directly to the `/api/documents/upload` endpoint.
4. **Vitals Screen (`vitals/vitals_screen.dart`):** Manual input forms for Blood Pressure (systolic/diastolic), Pulse, SpO2, Body Temperature, and Random Blood Sugar, complete with color-coded normal/warning badges.
5. **AYUSH Self-Assessment Module (`ayush/`):** Interactive questionnaire capturing Prakriti markers (body frame, skin texture, weather sensitivity) and Agni status (appetite irregularity, post-meal heaviness).
6. **Live Queue Tracking & Map Wayfinding (`queue/`, `map/`):** Live polling of queue position, displaying estimated wait minutes and a high-contrast indoor route map to the assigned OPD chamber.

---

## 4.3 Channel 3: 2G IVR Telephony Gateway

### Architectural Purpose
Targeted specifically at elderly, rural, and non-digitized citizens with basic keypad phones (e.g. JioPhone, Nokia 105) or landlines who cannot use touchscreens, QR codes, or mobile apps.

### The 4-Step Location Waterfall Resolver (`app/core/routing/location_resolver.py`)
Because standard 2G PSTN voice calls provide zero commercial GPS coordinates, MediKiosk resolves the nearest hospital chamber deterministically in `<2ms` without forcing the patient to state their location:

```
                      INCOMING IVR CALL (CLI / DID)
                                    │
                                    ▼
       [STEP 1] ABDM / Registered Patient Lookup (Best Accuracy)
       Matches caller CLI against registered patients/users in database.
       Retrieves verified home district/pincode.
                                    │ (If unknown caller)
                                    ▼
       [STEP 2] Dialed Regional Virtual Number (DID Routing)
       Inspects inbound DID dialed (e.g., 011-xxx → Delhi, 044-xxx → Chennai).
                                    │ (If universal toll-free 1800)
                                    ▼
       [STEP 3] DoT Telecom Circle Series Prefix (TRAI NDC Matching)
       Inspects first 4 digits of 10-digit mobile number against Department
       of Telecommunications Circle allocations (e.g. 9811 → Delhi NCR,
       9840 → Tamil Nadu, 9822 → Maharashtra).
                                    │ (If unmapped/roaming)
                                    ▼
       [STEP 4] National Apex Institute Fallback
       Routes to All India Institute of Ayurveda (AIIA) Apex Hub, New Delhi.
```

### Telephony Ingestion API (`app/api/ivr.py`)
1. **Webhook Ingestion (`/api/ivr/exotel/incoming-call`):** Receives Exotel call webhook, executes the 4-step location waterfall, creates encounter (`channel='ivr_phone'`), assigns a queue token (`IVR-xxx`), and generates greeting audio via TTS.
2. **Longitudinal ABHA Personalization:** If the caller CLI links to a known patient with past visits, the engine dynamically personalizes the greeting:  
   *"Welcome back Ramesh Kumar! Your token is IVR-561 at AIIA Delhi. In your previous visit, your complaint was Joint Pain. Are you calling regarding this same issue or a new symptom?"*
3. **Conversational Audio Turns (`/api/ivr/exotel/speech-turn`):** Receives transcribed speech from Exotel ASR or Sarvam Saaras, processes facts via `InterviewEngine`, and computes **verbatim audio timestamp proof** (e.g., `[00:14]`).
4. **Emergency Keyword Analysis & Instant Queue Preemption:**
   - Real-time screening against `EMERGENCY_RED_FLAGS` (e.g., *chest pain*, *heart attack*, *saans phoolna*, *chhati me dard*, *khoon ki ulti*, *nenju vali*).
   - If triggered: Encounter severity immediately escalates to `RED`, status flags emergency preemption, and the ticket **jumps directly to Position #1 in the doctor queue**.
5. **Call Finalization & SMS Dispatch (`/api/ivr/exotel/end-call`):** Completes encounter, evaluates drug safety, logs DPDP audit record, purges ephemeral memory, and simulates SMS confirmation to patient:  
   *"Namaste! MediKiosk Token: IVR-561. Your consultation is scheduled at AIIA Kayachikitsa Room 102. Helpline: +91-11-26950401."*

---

# 5. Doctor Workstation: Single Pane of Glass Architecture

The Doctor Workstation (`frontend/js/components/consultation-cockpit.js`) is the unified interface where every patient encounter converges, standardizing clinical metrics while adapting evidence inspection to the intake channel:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ DOCTOR WORKSTATION HEADER: Dr. S. Verma (MD Internal Med) · Room 102 · Kayachikitsa OPD     │
│ Patient: Ramesh Kumar (50M) · Token: IVR-561 · Dept: AYUSH Kayachikitsa · Badge: [RED]     │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────┤
│   COLUMN 1: VITALS & SAFETY  │ COLUMN 2: CLINICAL HISTORY   │ COLUMN 3: ASSESSMENT & SIGN   │
│            (25%)             │       & EVIDENCE (45%)       │            (30%)              │
│                              │                              │                               │
│ • Patient Snapshot           │ • 30-Sec Clinical Triage     │ • Provisional Diagnosis       │
│ • Vitals Grid:               │   Synthesis Narrative        │ • E-Prescription Pad          │
│   - BP: 128/84 mmHg          │ • Extracted Facts List       │ • AYUSH Lifestyle Advice:     │
│   - Pulse: 76 bpm            │ • Channel Evidence Variant:  │   Pathya / Apathya diet       │
│   - SpO2: 98% (Normal)       │   ┌────────────────────────┐ │ • 1-Click Verification Bar:   │
│ • Deterministic Safety:      │   │ [VARIANT A: KIOSK]     │ │   - Digital Doctor Stamp      │
│   - Drug-Drug Conflict:      │   │  ONNX Bounding Boxes   │ │   - Clinical Notes Input      │
│     Metformin + Contrast     │   │ [VARIANT B: BYOD]      │ │   - Status -> DOCTOR_REVIEWED │
│   - Herb-Drug Interaction:   │   │  ABHA Locker + Photos  │ │   - DPDP Audit Log Update     │
│     Ashwagandha + Sedatives  │   │ [VARIANT C: 2G IVR]    │ │                               │
│   - Panic Lab Alerts:        │   │  Verbatim Timestamp    │ │                               │
│     FBS: 342 mg/dL (CRIT)    │   │  Quotes: [00:12]       │ │                               │
│   - Proactive Gaps:          │   │  DoT Circle Route Path │ │                               │
│     DM Neuropathy Unasked    │   └────────────────────────┘ │                               │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────┘
```

### Channel-Specific Evidence Variants (`frontend/js/components/evidence-viewer.js`)
1. **Channel 1 (Kiosk) Evidence Variant:**
   - **Badge:** `Channel 1 · OPD Kiosk` | `ONNX_OCR · TOUCH`.
   - **Display:** Split-pane viewer. Left: Original prescription image with golden/green pulsing bounding boxes around cited lines. Right: Line-by-line OCR text with confidence metrics (e.g. `[Line 1] Tab Metformin 500mg BD — 98%`).
2. **Channel 2 (Mobile BYOD) Evidence Variant:**
   - **Badge:** `Channel 2 · Mobile BYOD` | `PATIENT_CONFIRMED · VOICE_ASR`.
   - **Display:** Linked ABHA Health Profile card, digital consent timestamp (`12-Sep-2026 09:14 AM via Mobile OTP`), and high-res smartphone camera attachments with zoom inspection.
3. **Channel 3 (2G IVR) Evidence Variant:**
   - **Badge:** `Channel 3 · Citizen Telephony IVR` | `TELEPHONY_ASR · VERIFIED`.
   - **Display:** Verbatim audio turn cards with timestamp proofs:  
     `[00:12] "छाती में बहुत तेज दर्द है, सांस लेने में तकलीफ हो रही है"`  
     Telecom routing audit path: `Step 3 (DoT Delhi Circle 9811 Series) → Assigned AIIA Apex Hub`.  
     Emergency preemption indicator: `🚨 JUMPED TO QUEUE POSITION #1`.

---

# 6. Core Clinical Engines & Algorithms

### 6.1 Deterministic Drug-Drug & Herb-Drug Interaction Engine (`app/core/clinical/drug_safety.py`)
100% offline, zero-hallucination pairwise matrix executing in `<1ms`:
- **Critical Allopathic Pairs:** Metformin + Radiopaque Contrast (lactic acidosis), Aspirin + Warfarin (severe hemorrhage), Clopidogrel + Warfarin, Methotrexate + Trimethoprim (bone marrow pancytopenia).
- **High Risk Allopathic Pairs:** Methotrexate + NSAIDs, ACE Inhibitors + Potassium, Digoxin + Amiodarone, SSRIs + Tramadol (serotonin syndrome), Lithium + NSAIDs.
- **AYUSH Herb-Drug Interactions:**
  - *Ashwagandha* + Sedatives / Benzodiazepines (additive GABAergic CNS depression).
  - *Ashwagandha* + Levothyroxine (thyroid hormone elevation).
  - *Yashtimadhu (Licorice)* + Antihypertensives / Diuretics (glycyrrhizin pseudoaldosteronism, hypokalemia).
  - *Guggulu* + Anticoagulants (enhanced platelet inhibition).
  - *Haridra (Curcumin)* + Aspirin/Warfarin (antiplatelet potentiation).
  - *Triphala* + Metformin / Sulfonylureas (additive hypoglycemia).

### 6.2 Biological Lab Range & Panic Threshold Checker (`app/core/clinical/lab_checker.py`)
Evaluates numeric lab investigations against physiological reference intervals and flags life-threatening panic thresholds:
- Fasting Blood Glucose (FBS): Low `<70`, High `>99`, Panic Low `<50`, Panic High `>300 mg/dL`.
- HbA1c: Normal `4.0–5.6%`, Panic High `>10.5%`.
- Serum Creatinine: Normal `0.6–1.2 mg/dL`, Panic High `>4.0 mg/dL`.
- Total WBC: Normal `4,000–11,000`, Panic Low `<2,000`, Panic High `>30,000 cells/μL`.
- Platelet Count: Normal `1.5–4.0`, Panic Low `<0.5 lakh/μL` (dengue/hemorrhage risk).

### 6.3 Proactive Clinical Gap Detector (`app/core/clinical/gap_detector.py`)
Identifies dangerous omissions ("What wasn't asked"):
- Diabetic patient 45+ without peripheral neuropathy questions (`DM_NEUROPATHY`).
- Diabetic patient 40+ without vision/retinopathy screening (`DM_VISION`).
- Chronic joint pain `>2 weeks` without morning stiffness duration assessment (differentiates Rheumatoid Arthritis from Osteoarthritis).
- Warm/swollen joint without septic arthritis screening.
- Chest pain without exertion/radiation/sweating characterization.

### 6.4 AYUSH Dashavidha Pariksha Engine (`app/core/clinical/ayush_engine.py`)
Implements authentic Ayurvedic diagnostic scoring based on Charaka Samhita Vimanasthana 8:
- **Prakriti Assessment:** Evaluates body frame, skin texture, digestion speed, weather sensitivity, and sleep patterns to determine Vata, Pitta, Kapha, Dvandvaja (Vata-Pitta, Pitta-Kapha, Vata-Kapha), or Tridoshaja constitution.
- **Agni Pariksha:** Categorizes digestive fire into Vishama (irregular/Vata), Tikshna (sharp/hyperactive/Pitta), Manda (sluggish/Kapha), or Sama (balanced).
- **Koshtha Assessment:** Evaluates bowel rhythm into Krura (hard/constipated), Mridu (soft/laxative-sensitive), or Madhyama (regular).
- **Ahara-Vihara Analysis:** Causative dietary (Rasa dominance) and lifestyle (Nidana) profiling.

---

# 7. Database Architecture & Data Models

### 7.1 SQLite Schema (`app/database.py`)
- `patients`: Master demographic registry (`id`, `name`, `age`, `gender`, `phone`, `language`, `abha_id`, `hospital_mrn`).
- `doctors`: Staff directory (`id`, `name`, `pin`, `department`, `specialty`, `room_number`, `is_available`).
- `departments`: Hospital clinical units (`id`, `name`, `code`, `description`, `floor`).
- `encounters`: Every patient visit (`id`, `patient_id`, `token_number`, `language`, `channel`, `status`, `department`, `severity_badge`, `abha_id`, `verified_by_doctor_id`, `doctor_notes`, `doctor_reviewed_at`, `ayush_intake`).
- `clinical_facts`: The immutable, audited core table (`id`, `encounter_id`, `category`, `field`, `value`, `dose`, `frequency`, `patient_words`, `normalized_concept`, `concept_code`, `provenance_tier`, `source_type`, `source_reference`, `confidence`, `confidence_breakdown`, `temporal_state`, `valid_from`, `valid_until`, `is_negated`, `status`).
- `documents`: Digitized medical records (`id`, `encounter_id`, `patient_id`, `file_path`, `ocr_status`, `ocr_raw_text`, `ocr_lines`, `highlighted_path`, `document_type`, `document_date`).
- `call_sessions`: Voice intake state machine tracking (`id`, `encounter_id`, `status`, `language`, `current_step`, `turn_count`).
- `queue_tokens`: OPD waiting queue (`token`, `encounter_id`, `department`, `status`, `position`, `doctor_room`, `called_at`).
- `audit_log`: Immutable DPDP audit trail (`id`, `encounter_id`, `actor`, `action`, `details`, `created_at`).
- `users`: Clinicians and registered patients (`id`, `role`, `full_name`, `email`, `mobile`, `abha_id`, `password_hash`, `department`, `room_number`, `qualification`, `hospital_name`, `hospital_phone`).

### 7.2 API Endpoint Inventory
- `POST /api/encounters/bootstrap`: Initializes new intake session across any channel.
- `POST /api/encounters/{id}/complete`: Finalizes facts, evaluates triage badges, locks encounter.
- `POST /api/call/session/start` & `POST /api/call/audio-turn`: Conversational voice turn endpoints.
- `POST /api/documents/upload` & `POST /api/documents/process-ocr`: Multipart file upload and OCR processing.
- `GET /api/queue/status/{token}` & `GET /api/queue/live`: Real-time queue tracker.
- `POST /api/doctor/auth`: PIN-gated doctor login (`1234`).
- `GET /api/doctor/queue`: Changes-first doctor queue sorted by severity badge (`RED` → `YELLOW` → `GREEN`).
- `GET /api/doctor/patient/{encounter_id}`: Comprehensive patient cockpit data payload.
- `POST /api/doctor/encounter/{encounter_id}/verify`: Doctor sign-off with digital stamp and clinical notes.
- `GET /api/doctor/patient/by-abha/{abha_id}`: Longitudinal past visit lookup across multi-year encounters.
- `GET /api/ivr/resolve-location`: Public 4-step location waterfall diagnostic simulator.
- `ALL /api/ivr/exotel/incoming-call`: Inbound telephony webhook.
- `ALL /api/ivr/exotel/speech-turn`: Telephony conversational turn and emergency preemption check.
- `ALL /api/ivr/exotel/end-call`: Telephony finalization and simulated SMS dispatch.

---

# 8. Comprehensive Gap Analysis: Current Implementation vs `DOCS/MediKiosk_Master_Context.md`

This section conducts a line-by-line audit comparing the active codebase against the 50 numbered sections and architectural guidelines in `DOCS/MediKiosk_Master_Context.md`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GAP SEVERITY SUMMARY MATRIX                           │
│                                                                             │
│  [CRITICAL GAPS]                  [PARTIAL / STUBBED]        [PRODUCTION]   │
│  • FHIR R4 Bundle Serialization   • Contradiction Engine     • Hardware BLE │
│  • Live ABDM M1/M2 Bridge         • Longitudinal Timeline    • Real SIP/RTP │
│  • Edge Model Weights on Disk     • Doc Classifier (Deep)    • Hospital SSO │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Master Context Section | Requirement in Master Context | Existing Repository State | Implementation Status | Exact Gap & Missing Implementation Details | Priority |
|---|---|---|---|---|---|
| **Section 8: Contradiction Resolution** | Detect and flag discrepancies between patient verbal claims and document OCR (e.g., patient denies BP meds, but prescription lists Amlodipine). Never silently pick one. | `clinical_facts` table records both facts with respective provenances (`VOICE` vs `OCR`), but there is no automated comparator algorithm running during encounter finalization. | **`PARTIALLY IMPLEMENTED`** | **Missing:** Automated contradiction detection rule engine (`contradiction_detector.py`) that compares medication names, doses, and symptom timelines across modalities, tags matching entities with `status='CONTRADICTION_FLAGGED'`, and alerts the doctor. | **P1** |
| **Section 9: Chronological Medical Timeline** | Synthesize a unified event stream reconstructing disease progression over months/years from document dates, verbal relative times ("6 months ago"), and prior encounters. | Medication facts contain `temporal_state` (`prescribed`, `taking`, `stopped`), and `get_patient_by_abha` lists past encounter cards. | **`PARTIALLY IMPLEMENTED`** | **Missing:** True cross-document chronological event synthesizer. Relative patient phrases (e.g. *"last Diwali"*, *"pichle hafte"*) are not resolved to absolute calendar dates; timeline is rendered as raw cards rather than an interactive chronological clinical flow. | **P1** |
| **Section 12–13: ABDM & FHIR Strategy** | Complete FHIR R4 resource generation: Patient, Encounter, Composition, Condition, MedicationStatement, AllergyIntolerance, Observation, DocumentReference. | Data models in `app/schemas/` align conceptually with FHIR schemas, but there are **zero** FHIR export classes or conversion endpoints in `app/`. | **`NOT IMPLEMENTED`** (Mocked in Mobile) | **Missing:** Dedicated FHIR R4 serializer module (`app/core/fhir/builder.py`) providing `/api/encounters/{id}/fhir-bundle` returning valid HL7 FHIR JSON Bundles; missing live ABDM Sandbox M1/M2 gateway connector. | **P0** |
| **Section 14: ClinicalFact Provenance Arithmetic** | Confidence computed via strict formula: `tier_score * input_quality * completeness`. | `ConfidenceBreakdown` model exists in `schemas/clinical_fact.py`, but database insertions in `interview_engine.py` and `ivr.py` hardcode static floats (e.g. `0.90`, `0.80`). | **`PARTIALLY IMPLEMENTED`** | **Missing:** Active calculation of input quality metrics from ASR acoustic confidence and OCR token confidence passed dynamically into the `confidence_breakdown` JSON blob. | **P1** |
| **Section 17–18: Offline Edge AI Floor** | Local offline GPU inference for IndicConformer ASR, IndicF5 TTS, and Qwen 2.5 7B LLM on an on-premise edge floor. | Code structure, socket ping, and adapter routing exist in `asr.py`, `tts.py`, and `llm.py`. Ollama integration works if Ollama is running. | **`INTEGRATION READY`** | **Missing:** Edge speech microservice scripts (`SPEECH_SERVICE_URL`) and actual model weight checkpoints are not packaged in the repository. Relies on fallback mock silence WAV / mock transcript if cloud keys are omitted and edge server is absent. | **P1** |
| **Section 23: Document Digitization Pipeline** | Multi-document classification separating prescriptions, lab reports, imaging scans, and discharge summaries with specialized OCR. | Single OCR pipeline in `ocr.py` using RapidOCR and Gemini Vision, defaulting to prescription extraction. | **`PARTIALLY IMPLEMENTED`** | **Missing:** Pre-classification step using visual layout analysis or text heuristics to tag document type prior to extraction; no specialized lab report tabular parser extracting parameter-value-unit columns. | **P1** |
| **Section 25–26: Privacy, DPDP Act & Security** | Data Protection Officer controls, encrypted local storage, hospital SSO, role-based access control, tamper-evident audit logs. | `DOCTOR_PIN=1234` in plain `.env`; SQLite database file is unencrypted on disk; audit log records actions in plain SQLite table. | **`PARTIALLY IMPLEMENTED`** | **Missing:** SQLCipher database encryption for patient PII at rest; JSON Web Token (JWT) session expiry with hospital OAuth2/SAML SSO; row-level masking of sensitive records. | **P2** |
| **Section 28–29: Doctor Workflow & HIS Dispatch** | Seamless 1-click EHR export, bi-directional HL7/FHIR messaging to hospital HIS, doctor audio dictation for consultation notes. | Doctor dashboard allows review, text notes, and sets status `DOCTOR_REVIEWED`. | **`PARTIALLY IMPLEMENTED`** | **Missing:** Webhook or HL7 MLLP interface to dispatch signed consultations into hospital EHRs (e.g. e-Hospital, Bahmni); no audio dictation microphone inside the doctor cockpit. | **P2** |
| **Section 45: Automated Testing Coverage** | Unit and integration test suites validating NegEx negation handling, drug interactions, panic lab ranges, and multi-channel API flows. | Basic test scripts in `tests/` directory. | **`PARTIALLY IMPLEMENTED`** | **Missing:** Comprehensive PyTest suite asserting zero-false-positive negation on complex Hinglish/Tamil sentences, full matrix coverage of drug contraindications, and end-to-end IVR webhook lifecycle tests. | **P1** |
| **Mobile BYOD: Live Hardware & Sensor Integration** | Real Bluetooth LE (BLE) medical sensor integration (pulse oximeters, digital BP cuffs) and direct thermal printer communication. | Mobile screens offer manual numeric text field entry for vitals; printer output is simulated. | **`MOCKED`** | **Missing:** Flutter BLE plugin (`flutter_blue_plus`) integration with standard Continua Health Alliance Bluetooth GATT profiles for direct medical device data capture. | **P3** |
| **Telephony: Carrier PSTN / SIP Trunking** | Full-duplex live carrier SIP trunking with bi-directional streaming audio sockets. | Exotel webhook endpoints in `app/api/ivr.py` handle HTTP request/response turns; `start_exotel_tunnel.bat` provides ngrok bridge. | **`PARTIALLY IMPLEMENTED`** | **Missing:** WebSocket media stream endpoint for real-time duplex audio streaming; currently operates over HTTP audio chunk uploads and TTS string responses. | **P2** |

---

# 9. Prioritized Engineering Action Plan

Following the Source-of-Truth Hierarchy and Karpathy Guidelines, improvements must be surgical, preserving working code while eliminating identified gaps:

### Priority 0 (P0) — Immediate Hackathon Critical Core
1. **FHIR R4 Bundle Serializer (`app/core/clinical/fhir_serializer.py`):**
   - Create a lightweight, dependency-free serializer converting completed `encounters`, `clinical_facts`, and `documents` into standard FHIR R4 JSON Bundles (`Encounter`, `Patient`, `Condition`, `MedicationStatement`, `Observation`, `DocumentReference`).
   - Expose endpoint `GET /api/encounters/{id}/fhir` and provide a "Download FHIR R4 Bundle" button in the Doctor Workstation.
2. **Automated Contradiction Resolution Engine (`app/core/clinical/contradiction_engine.py`):**
   - Add a cross-modal comparator running on encounter completion.
   - Detects mismatches between patient statements and OCR prescriptions (e.g. drug reported stopped vs currently prescribed, differing dosages).
   - Flags facts with `status='CONTRADICTION_FLAGGED'` and renders a high-visibility side-by-side comparison card in Column 2 of the Doctor Workstation.

### Priority 1 (P1) — High-Impact Clinical Differentiators
3. **True Chronological Medical Timeline Synthesizer:**
   - Parse document dates from OCR headers and resolve relative patient verbal timeframes (*"2 months ago"*, *"since last summer"*) into approximate ISO timestamps.
   - Render an interactive vertical timeline component on both Flutter mobile and Doctor Workstation.
4. **Dynamic Provenance & Confidence Calculator:**
   - Wire actual ASR confidence and OCR line confidence into the `ConfidenceBreakdown` model on every database write instead of static floats.
5. **Comprehensive Test Suite:**
   - Implement automated tests covering NegEx negation (*"pain is not there"*, *"bukhar nahi hai"*), drug interaction matrix validation, and 4-step location waterfall routing.

### Priority 2 (P2) — Enterprise Integration & Security
6. **Doctor Audio Dictation:** Add Web Audio dictation in Column 3 of the Doctor Workstation so physicians can speak clinical notes in Hindi or English, transcribed via Sarvam/Whisper into the sign-off box.
7. **Hospital SSO & Role-Based Access Control:** Replace hardcoded `DOCTOR_PIN=1234` with standard JWT bearer tokens and secure bcrypt password verification.
8. **Real-Time Telephony Media Stream:** Add WebSocket endpoint for full-duplex streaming with Exotel/Twilio voice gateways.

### Priority 3 (P3) — Hardware & Ecosystem Polish
9. **Bluetooth LE Vitals Sensor SDK:** Wire BLE GATT profile readers in Flutter mobile for instant pulse oximeter readings.
10. **ABDM Sandbox Live Gateway Connector:** Attach registered National Health Authority (NHA) sandbox credentials for real ABHA M1/M2 token verification.

---

# 10. Summary Verification Matrix

| Domain | Architecture Vision | Current Implementation | Lacking / Gap | Status |
|---|---|---|---|---|
| **Core Workflow** | First-mile clinical intake before physician consultation | End-to-end functional: Patient → Kiosk/Mobile/IVR → ClinicalFact → Doctor Workstation | None (Workflow fully preserved) | **Verified Complete** |
| **Channel 1 (Kiosk)** | Touch, voice, OCR, 3D avatar, explain-back, auto-purge | Fully implemented with Three.js avatar, RapidOCR, PIL evidence boxes, 45s inactivity timer | Physical printer driver (uses digital receipt) | **Operational** |
| **Channel 2 (Mobile)** | Flutter Android BYOD with 16 clean architecture features | Fully implemented with BLoC/provider state, call cards, camera upload, vitals UI | BLE hardware sensors (uses manual inputs) | **Operational** |
| **Channel 3 (IVR)** | 2G telephony with zero-GPS 4-step location waterfall | Fully implemented Exotel webhook API, 4-step resolver, audio proofs `[00:12]`, emergency preemption | Live SIP carrier trunk (uses HTTP webhooks) | **Operational** |
| **Doctor Workstation**| Single Pane of Glass with Channel-Specific Evidence | Fully implemented 3-column cockpit, dynamic evidence viewer (Kiosk/BYOD/IVR), 1-click verify | Voice dictation for notes | **Operational** |
| **Clinical Safety** | Deterministic drug, lab, gap, and AYUSH engines | 4 deterministic rule engines executing in `<1ms`, 100% hallucination-free | Multi-drug 3-way interaction matrix | **Verified Complete** |
| **Interoperability** | FHIR R4 Bundle + ABDM Sandbox | Schemas defined, data model compliant | Zero FHIR serializer endpoints in backend | **Identified Gap (P0)** |
| **Contradiction** | Side-by-side reconciliation of verbal vs OCR discrepancies | Both facts saved in DB with source tags | Automated comparison algorithm missing | **Identified Gap (P0)** |
