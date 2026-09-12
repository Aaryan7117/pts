# MediKiosk — Implementation & Architecture Audit
**Document Status:** CANONICAL AUDIT (Prompt 0 Deliverable)  
**Execution Context:** Single-Developer Full Implementation (SIH26047 — Ministry of AYUSH / AIIA)  
**Evaluator:** Antigravity AI Senior Engineer  
**Date:** September 2026  

---

## 1. Executive Summary

This audit establishes the baseline technical state of the MediKiosk repository before implementing the mobile and tablet client application. In accordance with the **Source-of-Truth Hierarchy** and **Karpathy Guidelines**, this document reconciles the existing working FastAPI backend with the canonical client specifications:
- `MEDIKIOSK_ANDROID_DESIGN_SPEC.md`
- `DOCS/MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md`
- `MEDIKIOSK_SINGLE_DEVELOPER_FULL_ANTIGRAVITY_MASTER - Copy.md`
- `MEDIKIOSK_DEVELOPMENT_FLOW_MASTER.md`

No functionality has been invented. All contracts documented below reflect the active repository codebase.

---

## 2. Workspace & Environment Inspection

| Subsystem | Discovered State | Verification Result |
|---|---|---|
| **Repository Root** | `/home/conste/repos/pts` | Clean Git workspace |
| **Backend Framework** | FastAPI 3.0.0 with Uvicorn (`app/main.py`) | Operational via `python run.py` |
| **Database** | SQLite with WAL mode via `aiosqlite` (`app/database.py`) | Tables initialized on startup |
| **Client Codebase** | Flutter Project (`/home/conste/repos/pts/mobile`) | Valid project, FVM pinned |
| **Flutter SDK** | Flutter 3.47.3 • channel stable (Dart 3.13.3) | `fvm flutter test` passed |
| **Target Hardware** | Physical Android Phone via USB Debugging | **`moto g54 5G` (Android 15, API 35)** detected via ADB |
| **Secondary Target** | Android Tablet / Kiosk | 1280 × 800 Landscape Responsive Grid |

---

## 3. Backend Subsystem Architecture

### 3.1 Database Schema (`app/database.py`)
The active database engine is SQLite in Write-Ahead Logging (`WAL`) mode with foreign key enforcement:
1. `encounters`:
   - `id` (TEXT PK, e.g. `enc-a1b2c3d4`)
   - `patient_id` (TEXT, e.g. `pat-e5f6g7h8`)
   - `token_number` (TEXT UNIQUE, e.g. `A-104`, `TK-4819`)
   - `language` (TEXT DEFAULT `'hi'`: `'en'`, `'hi'`, `'ta'`, `'te'`, `'mr'`)
   - `channel` (TEXT DEFAULT `'kiosk'`: `'kiosk'`, `'android_byod'`, `'ivr_phone'`)
   - `status` (TEXT: `'BOOTSTRAPPED'`, `'IN_PROGRESS'`, `'COMPLETED'`, `'DOCTOR_REVIEWED'`)
   - `department` (TEXT DEFAULT `'General Medicine'`)
   - `severity_badge` (TEXT: `'GREEN'`, `'YELLOW'`, `'RED'`)
   - `created_at`, `updated_at` (DATETIME)
2. `clinical_facts`:
   - Immutable, audited fact table storing chief complaint, medications, allergies, vitals, lab results, and AYUSH constitutional markers (Agni, Prakriti, Ahara).
   - Provenance tracking: `provenance_tier` (`TOUCH`, `LOOKUP`, `EMBEDDING`, `LLM`, `OCR`), `source_type` (`patient_voice`, `document_ocr`, `explain_back_verified`, `touch_input`), `confidence` (float 0.0–1.0).
   - Temporal state: `temporal_state` (`prescribed`, `taking`, `stopped`, `dose_changed`), `valid_from`, `valid_until`.
3. `documents`:
   - Scanned prescription/lab records (`file_path`, `ocr_status`, `ocr_raw_text`, `ocr_lines`, `highlighted_path`).
4. `call_sessions`:
   - Conversational voice intake sessions linked to encounters (`id`, `encounter_id`, `status`, `language`, `current_step`, `turn_count`).
5. `queue_tokens`:
   - OPD waiting queue tokens (`token`, `encounter_id`, `department`, `status`, `position`, `doctor_room`).
6. `audit_log`:
   - DPDP/HIPAA-compliant immutable audit log (`encounter_id`, `actor`, `action`, `details`, `created_at`).

### 3.2 AI, Vision & Clinical Engines
1. **LLM Gateway (`app/core/adapters/llm.py`):**
   - Hybrid Edge/Cloud Router:
     - Local Edge: Ollama (`qwen2.5:7b` primary, `qwen2.5:3b` fallback at `http://localhost:11434/v1`).
     - Cloud Speed: Groq (`llama-3.1-70b-versatile`).
     - Cloud Quality: Google Gemini 1.5/2.0 Flash.
2. **ASR & Speech Gateway (`app/core/adapters/asr.py` & `tts.py`):**
   - Cloud ASR: Sarvam AI (`saaras:v2` / `saarika:v2`).
   - Edge ASR: IndicWhisper / local speech service.
   - Cloud/Edge TTS: Sarvam Bulbul V3 / IndicF5 / gTTS fallback.
3. **OCR Engine (`app/core/adapters/ocr.py`):**
   - Multimodal Gemini Vision (cloud) or RapidOCR ONNX (offline edge).
   - Line-indexed bounding polygons with OpenCV evidence boxing.
4. **Deterministic Clinical Engines (`app/core/clinical/`):**
   - `interview_engine.py`: Adaptive SOCRATES questioning loop.
   - `drug_safety.py`: Deterministic drug-drug interaction matrix.
   - `lab_checker.py`: Reference interval range validation.
   - `gap_detector.py`: Proactive missing information flags.
   - `normalizer.py`: Semantic normalization to SNOMED CT and NAMASTE codes.

---

## 4. Hardware & Client Target Inspection

### 4.1 USB Connected Physical Device
- **Device Model:** Motorola Moto G54 5G (`ZD222DWX6G`)
- **Android Version:** Android 15 (API 35, `android-arm64`)
- **Transport:** USB Debugging active and authorized
- **Application Display Mode:** Android BYOD (Portrait) + Tablet/Kiosk Mode (Landscape 1280×800)

### 4.2 Kiosk Environment
- Primary resolution target: 1280 × 800 logical pixels.
- Interaction paradigm: Voice-first with massive touch controls (72dp primary CTA, minimum 64dp targets).
- Privacy protection: 45-second inactivity warning with 10-second automatic RAM wipe and privacy reset overlay.

---

## 5. Telephony / IVR Clarification (Non-Negotiable)

The backend exposes `/api/call/*` endpoints that implement a **conversational voice-session intake API**.  
- **Inspection Finding:** No direct PSTN/SIP carrier integration (e.g. Twilio Voice, Plivo, Exotel, Asterisk) exists in the repository.
- **Strict Classification:**
  - Kiosk & Mobile Voice Turn Session: **`IMPLEMENTED`**
  - Carrier PSTN Telephone Integration: **`INTEGRATION READY / MOCKED`**
  - The client will simulate the IVR/call surface via `ActiveCallCard` (Screen A-06B) and connect to the live `/api/call/*` session engine without faking live telecom carrier connectivity.

---

## 6. Audit Conclusion & Next Actions

The backend foundation is complete, healthy, and structurally sound. The database, clinical schemas, OCR pipeline, and conversational state machine are ready to serve the mobile client.

Proceed immediately to **`API_CONTRACT_AUDIT.md`** and **`FEATURE_STATUS.md`** to freeze the technical contracts.
