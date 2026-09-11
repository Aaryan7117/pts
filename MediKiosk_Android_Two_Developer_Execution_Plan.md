# MediKiosk — Android & Telephony Two-Developer Execution Plan
## Mobile BYOD & Conversational Call Intake Execution Plan (v3 Canonical)

**Target:** Android / Mobile Patient Application (BYOD) + Twilio / Call Intake Integration  
**Team:** THOUFIKUR + MUBASHIR  
**Backend Foundation:** Provided by Core Backend Team (Lead Engineer + Antigravity)  

---

## 0. Executive Split of Responsibilities

To ensure maximum speed and eliminate hackathon integration friction, the project responsibilities are divided cleanly:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE MEDIKIOSK WORK DIVISION                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 👑 CORE BACKEND & AI FOUNDATION (Lead Engineer + Antigravity):              │
│ • Unified FastAPI Backend running on the 8GB Laptop                         │
│ • Multi-Model Hybrid AI (Ollama Qwen 7B, Groq Llama 3.1 70B, Gemini Flash) │
│ • Speech Engines: AI4Bharat IndicWhisper (ONNX CPU) + Sarvam/Groq Whisper   │
│ • Concept Normalizer: NegEx + Multilingual Sentence Embeddings (MiniLM)     │
│ • Vision OCR: RapidOCR ONNX + Line-indexed prescription citation            │
│ • All Pydantic Schemas (ClinicalFact, AYUSH Dashavidha Pariksha)            │
│ • Deterministic Safety Engines (Drug Interactions, Lab Ranges, Gaps)        │
│ • Clean REST & Call-Session APIs with interactive Swagger docs at `/docs`   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📱 MOBILE APP & TELEPHONY TEAM (THOUFIKUR + MUBASHIR):                      │
│ • Flutter / Android Mobile Client (BYOD Intake Channel)                     │
│ • 📞 Conversational Voice Call Screen ("Call AI Intake" UI)                │
│ • Twilio / Calling Integration (Telephony stream & webhooks)                │
│ • Camera Document Scan & Gallery Upload UI                                  │
│ • Live Queue Token Tracker Screen                                           │
│ • Routing and connecting all Android UI screens to the Core Backend APIs    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. What the Android & Telephony Team Builds

Thoufikur and Mubashir do **not** need to configure local CUDA drivers, quantized models, or complex clinical rules. The Core Backend provides those out-of-the-box.

### Your Direct Mission:
1. **Build the Mobile App (Flutter / Android):**  
   An accessible, elderly-friendly mobile interface for patients waiting in the OPD queue or at home.
2. **Build the Conversational Call Intake (Twilio / Phone Call UI):**  
   Implement the phone-call experience where patients speak naturally over a call interface, audio streams to our backend, and symptoms auto-fill in real-time.
3. **Connect the App to the Core Backend APIs:**  
   Route your mobile screens to the clean REST endpoints provided by the Core Backend.

---

## 2. The Conversational Call Intake Feature (The Heart of the Mobile Experience)

Elderly (70+ yrs) and rural patients struggle with multi-step forms. The mobile app solves this with a **1-Tap Call Intake**:

### A. The User Journey
```text
Patient opens App / Scans Token QR
                ↓
Taps massive Green Card: [ 📞 अस्पताल से बात करें / CALL AI INTAKE ]
                ↓
Opens Active Call UI (Screen A-06B)
(Looks and feels like a real phone call with avatar, timer, and audio waveform)
                ↓
AI speaks over earpiece/speaker: "नमस्ते, आपको क्या परेशानी है?"
                ↓
Patient speaks naturally: "मुझे 3 दिन से सीने में जलन और बुखार है..."
                ↓
Audio stream sends to POST /api/call/audio-turn
                ↓
Screen auto-fills cards in real-time as patient speaks
                ↓
AI asks adaptive follow-up over the call
                ↓
Patient confirms via audio / large YES button
                ↓
Token generated (e.g. A-042) → App switches to Live Queue Tracker
```

### B. Twilio / Telephony Calling Flow (For Basic Keypad Phones)
* For rural patients with basic 2G keypad phones:
  * Patient dials the hospital toll-free number.
  * Twilio / Telephony webhook hits our backend: `POST /api/ivr/voice-webhook`.
  * Twilio plays TTS audio questions, records voice replies, and pipes audio into our clinical engine.
  * Case appears in the Doctor Dashboard under the exact same queue.

---

## 3. The Core Backend API Schemas (Contract Between App & Backend)

> **Mubashir and Thoufikur:** Use these exact JSON Request and Response structures to build your Flutter Dart models (`fromJson` / `toJson`) and mock service layer immediately.

### Endpoint 1: QR Token Validation & Encounter Bootstrap
* **URL:** `POST /api/encounters/bootstrap`
* **Request Body:**
  ```json
  {
    "qr_token": "TK-4819",
    "device_channel": "android_byod"
  }
  ```
* **Response Body (`200 OK`):**
  ```json
  {
    "encounter_id": "enc-7f8a-uuid",
    "patient_id": "pat-1029-uuid",
    "token_number": "TK-4819",
    "status": "BOOTSTRAPPED",
    "supported_languages": [
      {"code": "en", "label": "English"},
      {"code": "hi", "label": "हिन्दी"},
      {"code": "ta", "label": "தமிழ்"},
      {"code": "te", "label": "తెలుగు"},
      {"code": "mr", "label": "मराठी"}
    ]
  }
  ```

---

### Endpoint 2: Start Conversational Voice Call Session
* **URL:** `POST /api/call/session/start`
* **Request Body:**
  ```json
  {
    "encounter_id": "enc-7f8a-uuid",
    "language": "hi"
  }
  ```
* **Response Body (`200 OK`):**
  ```json
  {
    "session_id": "call-sess-9912-uuid",
    "status": "CALL_ACTIVE",
    "opening_text": "नमस्ते, मैं ऑल इंडिया इंस्टीट्यूट ऑफ आयुर्वेदा का डिजिटल सहायक हूँ। आपको क्या परेशानी है?",
    "opening_audio_base64": "UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ..."
  }
  ```

---

### Endpoint 3: Stream Voice Audio Turn (The Core Calling Loop)
* **URL:** `POST /api/call/audio-turn`
* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  * `session_id` (string): `"call-sess-9912-uuid"`
  * `audio_file` (file): Audio recording chunk from device microphone (`.wav`, `.m4a`, or `.webm`)
* **Response Body (`200 OK`):**
  ```json
  {
    "session_id": "call-sess-9912-uuid",
    "turn_index": 1,
    "patient_transcript": "मुझे तीन दिन से पेट में जलन और सीने में दर्द है",
    "extracted_facts": [
      {
        "category": "symptom",
        "field": "chief_complaint",
        "concept": "Epigastric burning sensation",
        "concept_code": "SNOMED:30789004",
        "duration": "3 days",
        "confidence": 0.92,
        "provenance": "EMBEDDING_MATCH"
      },
      {
        "category": "symptom",
        "field": "chest_pain",
        "concept": "Retrosternal chest discomfort",
        "concept_code": "SNOMED:29857009",
        "duration": "3 days",
        "confidence": 0.88,
        "provenance": "EMBEDDING_MATCH"
      }
    ],
    "next_question_text": "क्या आपको इसके साथ उल्टी या चक्कर भी आ रहे हैं?",
    "next_question_audio_base64": "UklGRi4AAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQ...",
    "is_completed": false
  }
  ```

---

### Endpoint 4: End Voice Call Session & Lock Intake
* **URL:** `POST /api/call/session/end`
* **Request Body:**
  ```json
  {
    "session_id": "call-sess-9912-uuid"
  }
  ```
* **Response Body (`200 OK`):**
  ```json
  {
    "encounter_id": "enc-7f8a-uuid",
    "status": "COMPLETED",
    "assigned_token": "A-042",
    "department": "General Medicine",
    "total_facts_captured": 4,
    "red_flags_detected": false
  }
  ```

---

### Endpoint 5: Upload Prescription / Medical Document Photo
* **URL:** `POST /api/documents/upload`
* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  * `encounter_id` (string): `"enc-7f8a-uuid"`
  * `document` (file): Photo of paper prescription captured by phone camera
* **Response Body (`200 OK`):**
  ```json
  {
    "document_id": "doc-5521-uuid",
    "ocr_status": "SUCCESS",
    "extracted_medications": [
      {
        "name": "Methotrexate",
        "dose": "10 mg",
        "frequency": "weekly",
        "source_lines": [2, 3],
        "confidence": 0.94
      }
    ],
    "flagged_interactions": [
      {
        "drug_a": "Methotrexate",
        "drug_b": "NSAIDs",
        "severity": "HIGH",
        "warning": "NSAIDs reduce renal clearance of Methotrexate. Flagged for clinician review."
      }
    ],
    "highlighted_image_url": "http://192.168.1.15:8000/static/evidence/doc-5521-boxed.jpg"
  }
  ```

---

### Endpoint 6: Live OPD Queue Status Tracker
* **URL:** `GET /api/queue/status/{token}`
* **Path Parameter:** `token` (e.g. `A-042`)
* **Response Body (`200 OK`):**
  ```json
  {
    "token": "A-042",
    "department": "General Medicine",
    "status": "WAITING",
    "patients_ahead": 3,
    "estimated_wait_minutes": 10,
    "doctor_room": "Room 104 (Dr. Sharma)"
  }
  ```

---

## 4. Division of Work: THOUFIKUR vs. MUBASHIR

### 🎨 THOUFIKUR: Mobile UI & Interaction Lead
* **A-01:** Welcome & QR Scanner screen (joins OPD queue via camera).
* **A-02:** 5-Language Selection screen (English, हिन्दी, தமிழ், తెలుగు, मराठी).
* **A-03:** Consent & Patient ID screen (minimal, elderly-accessible).
* **A-04:** **Active Call Intake Screen (Screen A-06B):**
  * Calling avatar, call timer, pulsing audio waveform.
  * Speakerphone toggle, mute button, red End Call button.
  * Live rolling captions and auto-filling symptom cards.
* **A-05:** Prescription & Report Camera Capture screen (photo crop, retake, upload).
* **A-06:** Explain-Back verification modal (Large 80px Green [YES] / Red [NO] buttons).
* **A-07:** Live Queue Token Tracker screen (token number, department, estimated wait time).

### ⚙️ MUBASHIR: Networking, Audio Streaming & Twilio Lead
* **M-01:** Flutter HTTP API Client (`ApiClient`) connecting to all Core Backend endpoints using the Section 3 schemas.
* **M-02:** Mobile Audio Recording & Streaming:
  * Capture 16kHz mono audio from device mic.
  * Send audio chunks to `/api/call/audio-turn`.
  * Decode and play back incoming base64 TTS audio smoothly over speaker/earpiece.
* **M-03:** Twilio / Telephony Webhook Integration:
  * Configure Twilio Voice TwiML webhook to hit `/api/ivr/voice-webhook`.
  * Handle incoming keypad phone calls and connect DTMF / voice streams.
* **M-04:** Offline Drafts & Sync:
  * If phone network drops, cache draft answers locally in SQLite/Hive.
  * Background retry queue using Android `WorkManager` when connectivity returns.

---

## 5. Mobile App Screen Flow (Step-by-Step)

```text
┌─────────────────────────────────────────────────────────────┐
│ Screen 1: Welcome & QR Scan                                 │
│ [ Scan Token QR ]  or  [ Enter Token Manually ]             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Screen 2: Language Selector (5 Cards)                       │
│ [ English ]  [ हिन्दी ]  [ தமிழ் ]  [ తెలుగు ]  [ मराठी ]      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Screen 3: 1-Tap Intake Mode                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📞 CALL AI INTAKE (Speak naturally over a phone call)   │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✍️ TOUCH INTAKE (Step-by-step card questionnaire)       │ │
│ └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Screen 4: Active Call Intake (Phone UI)                     │
│ • Live Avatar + Call Timer (01:14)                          │
│ • AI speaks question -> Patient answers                     │
│ • Rolling Cards Auto-Fill on screen                         │
│ • Large [ End Call & Review ] button                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Screen 5: Camera Prescription Upload                        │
│ [ 📷 Take Photo of Paper Prescription / Lab Slip ]          │
│ [ Upload & Verify ]                                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Screen 6: Live Queue Tracker                                │
│ TOKEN: A-042 | Department: General Medicine                 │
│ Status: 3 patients ahead of you (Estimated wait: ~10 mins)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Integration Checkpoints for the Mobile Team

1. **Hour 0–4 (Contract Freeze & Hello World):**
   * Thoufikur sets up Flutter project and creates the 6 screens with placeholder buttons.
   * Mubashir creates Dart DTO model classes from the Section 3 JSON schemas and tests calling `http://<laptop-ip>:8000/docs` from the mobile browser over local Wi-Fi.
2. **Hour 4–12 (Call Screen & Voice Turns):**
   * Thoufikur completes the Active Call UI.
   * Mubashir connects the mic audio recorder to `/api/call/audio-turn` and verifies that speaking Hindi audio returns transcribed text and next-question audio.
3. **Hour 12–20 (Camera Scan & Queue Tracker):**
   * Connect camera capture to `/api/documents/upload` and render extracted medicines.
   * Connect `/api/queue/status` to show the live token card.
4. **Hour 20–28 (Twilio Webhook & Offline Resilience):**
   * Mubashir sets up the Twilio phone number webhook for basic keypad phones.
   * Test local draft caching when mobile data is toggled off.
5. **Hour 28–36 (Full End-to-End Rehearsal with Doctor Dashboard):**
   * Run a full intake call on the Android phone $\rightarrow$ verify that the patient immediately pops up on the Doctor Dashboard waiting queue on the laptop!

---

*MediKiosk Android & Telephony Execution Plan (v3 Finalized).*
