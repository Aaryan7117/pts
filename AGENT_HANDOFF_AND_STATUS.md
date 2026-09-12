# 🏥 MediKiosk: Agent Handoff, Current Status & Execution Roadmap

> **Target Readership:** Incoming AI Coding Agents / Developers  
> **Repository:** `Aaryan7117/pts`  
> **Architecture Paradigm:** Distributed Rural PHC Edge Architecture (Thin-Client Kiosk + On-Premise GPU Edge Server)  
> **Last Updated:** September 11, 2026

---

## 🧭 1. Executive Summary & Core Architecture

MediKiosk is an offline-first, multilingual, multimodal AI patient intake & clinical decision support kiosk designed for rural Indian Primary Health Centres (PHCs).

### Architectural Invariant (Non-Negotiable):
- **Deployment Topology:** **Distributed Rural PHC Edge Architecture**
  - **Station A — Thin-Client Kiosk Terminal:** Runs the touchscreen UI, camera, microphone, and speakers. Low-power, low-cost client sitting in the clinic waiting hall.
  - **Station B — On-Premise Central GPU Edge Server:** Dedicated 8GB VRAM GPU machine (NVIDIA RTX) sitting on the local clinic LAN (`192.168.137.x`), running offline AI workloads (Ollama with Qwen 2.5 7B, IndicF5 TTS, IndicConformer/faster-whisper ASR, RapidOCR).
  - **Offline Resilience:** Zero internet dependency. Client communicates with the Edge Server over offline local Wi-Fi / Ethernet subnet. If broadband is present, the system opportunistically accelerates via cloud APIs (Sarvam AI, Gemini Flash, Groq).
- **Languages Supported (Strict 5):** Hindi (`hi`), Tamil (`ta`), Telugu (`te`), Marathi (`mr`), English (`en`).

---

## ✅ 2. What Has Been Completed So Far

### A. FastAPI Core Backend (`app/`)
1. **Application & Lifecycle (`app/main.py`)**:
   - Asynchronous SQLite WAL database (`medikiosk.db`) initialized via `aiosqlite`.
   - Complete REST endpoints:
     - `GET /health`: Diagnostic probe returning LLM, OCR, TTS, ASR, and deployment mode status.
     - `POST /api/encounters/bootstrap`: Initializes kiosk encounter, issues anonymous token.
     - `POST /api/encounters/queue`: Doctor queue retrieval with triage prioritization.
     - `POST /api/call-sessions/start`: Multi-turn voice session bootstrap with opening question audio.
     - `POST /api/documents/upload`: Multimodal document intake pipeline (OCR + clinical extraction).
     - `POST /api/doctor/auth`: PIN authentication guard for clinical dashboard.
2. **Configuration & Topology (`app/config.py`, `.env.example`, `.env`)**:
   - Dynamic network probing (50ms socket check to `1.1.1.1`) to decide Cloud vs. Edge.
   - Microservice forwarding support via `SPEECH_SERVICE_URL` and `DEPLOYMENT_MODE` (`STANDALONE`, `CLUSTER`, `CLOUD`).

### B. Clinical Safety Engines (`app/core/clinical/`)
1. **Deterministic Drug Safety Engine (`drug_safety.py`)**:
   - Zero hallucination. Hardcoded interaction rules from `drug_interactions.json`.
   - **Allopathic interactions**: Metformin + Contrast, ACE Inhibitors + Spironolactone, Warfarin + NSAIDs, etc.
   - **AYUSH Herb-Drug interactions**: Ashwagandha + Sedatives/Anxiolytics, Guggulu + Statins, Garlic + Anticoagulants.
2. **Lab Reference Checker (`lab_checker.py`)**:
   - Quantitative evaluation of 16 common biomarkers (HbA1c, Fasting Blood Sugar, Serum Creatinine, Platelets, Hemoglobin, Potassium, etc.).
   - Returns `NORMAL`, `OUT_OF_RANGE`, or `CRITICAL_ALERT` with standard reference intervals.
3. **Clinical Gap Detector (`app/core/triage/gap_detector.py`)**:
   - Identifies care deficits based on clinical history (e.g., diabetic patient missing HbA1c > 6 months).

### C. Speech & AI Adapters (`app/core/adapters/`)
1. **Multi-Provider Resilient LLM (`llm.py`)**:
   - Tier 1: Google Gemini Flash (Cloud Quality, multimodal vision & clinical reasoning).
   - Tier 2: Groq Llama 3.1 70B (Cloud Speed fallback, ~500ms).
   - Tier 3: Ollama with **Qwen 2.5 7B** (Offline Edge Server Brain, `OLLAMA_MODEL=qwen2.5:7b`).
2. **Text-to-Speech Adapter (`tts.py`)**:
   - **Tier 1 (Cloud)**: Sarvam AI Bulbul V3 (<250ms, near-human Indian accent across all 5 languages).
   - **Tier 2 (Offline)**: **IndicF5 (AI4Bharat)** running on the GPU Edge Server, forwarded over local LAN via `SPEECH_SERVICE_URL`.
   - **Dev Fallback**: Deterministic silence WAV (prevents crashes during offline unit testing).
   - *Eliminated:* Robotic `pyttsx3` and incomplete `Piper` have been completely eradicated from the project.
3. **Prescription OCR Engine (`ocr.py`)**:
   - Local: `rapidocr_onnxruntime` (PP-OCRv5) on CPU providing word and line-level bounding quad boxes for UI highlighting.
   - Cloud: Gemini Flash Vision for direct handwritten prescription JSON extraction with coordinate bounding boxes.
4. **Speech Recognition Adapter (`asr.py`)**:
   - **Tier 1 (Cloud)**: Sarvam AI Saaras V4, with Groq Whisper-Large-v3-Turbo as cloud secondary.
   - **Tier 2 (Offline)**: **IndicConformer 600M / faster-whisper** on the On-Premise GPU Edge Server, forwarded over local clinic LAN via `SPEECH_SERVICE_URL`.
   - **Dev Fallback**: Deterministic mock transcript (prevents crashes during offline unit testing).
   - *Eliminated:* All stale `IndicWhisper` references and the dead `NotImplementedError` ONNX stub are gone. `INDICWHISPER_MODEL_PATH` is now `INDICCONFORMER_MODEL_PATH`.

### D. Multilingual Concept Normalizer (`app/core/clinical/normalizer.py`)
- Embedding model is now **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** (XLM-RoBERTa based, ~470 MB, native hi/mr/ta/te/en).
- Configurable via `EMBEDDING_MODEL_NAME` in `app/config.py` / `.env` — swappable with zero code edits.
- Concept embeddings are pre-computed at app startup (`EMBEDDING_WARMUP_ON_STARTUP=true`, run off the event loop via `asyncio.to_thread`).
- **Per-variant indexing:** every concept variant (canonical name + each native-script keyword) is embedded as its own vector, and match resolves the best variant back to its owning concept. Concatenating all scripts into one string diluted each language's signal, so a Tamil query scored poorly against a mostly-Latin blob.
- Degrades gracefully to keyword substring matching if `sentence-transformers` is missing or the model can't be fetched.

### E. Automated Test Suite (`tests/`)
- `tests/test_clinical_engines.py`: 5/5 unit tests passing (Critical drug interactions, AYUSH interactions, Lab bounds, Gap detection, NegEx rule filtering).
- `tests/test_api_endpoints.py`: 5/5 integration tests passing (Health check, Encounter bootstrap, Call session, Doctor auth, Document upload).
- **Total: 10/10 tests passing.**

---

## ⚠️ 3. What Needs to Be Done Next (Immediate Action Items)

### 🔴 Priority 1: Connect End-to-End Voice Intake Turn (`/api/encounters/{id}/turn`)
- Build the interactive voice intake route:
  1. Accepts base64 chunked audio / text transcript from Kiosk.
  2. Runs NegEx + Concept Normalizer to extract symptoms.
  3. Runs LLM for clinical fact extraction and next question generation.
  4. Synthesizes explain-back audio via TTS (Sarvam Bulbul or IndicF5).
  5. Returns updated encounter state + audio base64 to Kiosk.

### 🔴 Priority 2: Mobile / Frontend UI Integration
- **Status:** The `mobile/` directory contains Flutter boilerplate from commit `c3c3998`, but `mobile/lib/` was not committed by the remote team.
- **Action Needed:**
  - Check with the team or repository branches for the actual UI code.
  - Or construct the lightweight Kiosk client UI (React/Vite touchscreen interface or Flutter app) pointing to `VITE_API_BASE_URL` or `API_BASE_URL`.

### 🔴 Priority 3: GPU Edge Server Turnkey Runner (Laptop 2)
- Create a script (e.g. `scripts/start_edge_server.bat` or `scripts/edge_service.py`) for the 8GB RTX GPU machine:
  1. Starts Ollama with LAN binding: `$env:OLLAMA_HOST="0.0.0.0:11434"; ollama serve`.
  2. Runs the speech microservice (IndicF5 + IndicConformer) on port `8001`.
  3. Provides firewall and LAN IP (`ipconfig`) instructions.
- **Contract the backend already expects** (both adapters forward to `SPEECH_SERVICE_URL`):
  - `POST /api/speech/synthesize` — JSON `{text, language}` ➔ `{audio_base64, duration_ms}`
  - `POST /api/speech/transcribe` — multipart `file` + form `language` ➔ `{text, language, confidence}`

---

## 📂 4. Exact Files to Feed to a New Agent for Full Context

When bringing in a new agent or developer, **pass the following files** in this exact order to give them complete, unambiguous context:

### Essential Context Files (Read-Only Specs):
1. **`AGENT_HANDOFF_AND_STATUS.md`** *(This file)*: High-level overview, status, and roadmap.
2. **`MediKiosk_Tech_Stack_Finalized.md`**: The master technical architecture specification (VRAM budget, model benchmarks, clinical guardrails).
3. **`speech_stack_research.md`**: Full benchmark and reasoning for speech/TTS/ASR model selection (why IndicF5 & Sarvam were chosen; why Piper/pyttsx3/XTTS were eliminated).
4. **`MediKiosk_Full_Context_Handoff.md`**: Operational guidelines and hackathon demo flow.

### Active Codebase Files (To Inspect & Modify):
1. **`app/config.py`**: Global environment variables and feature toggles.
2. **`requirements.txt`**: Active Python packages.
3. **`app/core/clinical/normalizer.py`**: Semantic Concept Normalizer (multilingual MiniLM, aligned).
4. **`app/core/adapters/asr.py`**: Speech recognition adapter (two-tier, aligned).
5. **`app/core/adapters/tts.py`**: Text-to-speech adapter (already cleaned & aligned).
6. **`app/core/adapters/llm.py`**: Multi-provider LLM adapter.
7. **`app/main.py`**: FastAPI route controller.
8. **`tests/test_api_endpoints.py` & `tests/test_clinical_engines.py`**: Regression verification tests.

---

## 🔒 5. Rules & Ground Truths for Incoming Agents

1. **Model Hierarchy is Locked:**
   - LLM: Gemini Flash (Cloud) ➔ Groq Llama 3.1 70B (Cloud backup) ➔ **Qwen 2.5 7B** via Ollama (Offline Edge Node). **Never downgrade Qwen to 3B in code**; 3B is strictly an emergency `.env` fallback.
   - TTS: Sarvam Bulbul V3 (Cloud) ➔ **IndicF5** (Offline GPU Edge Server). No pyttsx3, no Piper.
   - ASR: Sarvam Saaras V4 (Cloud) ➔ **IndicConformer / faster-whisper** (Offline Edge Server).
   - OCR: Gemini Flash Vision (Cloud) ➔ **RapidOCR PP-OCRv5** (Offline CPU).
   - Embeddings: **`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`** (Offline CPU). Never use `all-MiniLM-L6-v2`.
2. **Public Terminology:**
   - In all code comments, markdown docs, and commit messages, refer to the physical setup as:
     `"Distributed Rural PHC Edge Architecture (Thin-Client Kiosk + On-Premise GPU Edge Server)"`.
3. **Zero Hallucination in Clinical Safeguards:**
   - Drug-drug and herb-drug interactions, lab thresholds, and NegEx must remain strictly deterministic (Python rules + JSON banks). Never rely solely on an LLM for safety gates.
4. **Always Run Tests:**
   - Always verify that `pytest tests/ -v` passes after modifying any engine or adapter.
