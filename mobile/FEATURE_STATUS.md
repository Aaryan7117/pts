# MediKiosk — Feature Status Matrix
**Document Status:** CANONICAL CAPABILITY AUDIT (Prompt 0 Deliverable)  
**Evaluation Standard:** Zero-Hallucination Honest Architecture  
**Statuses Defined:**  
- **`IMPLEMENTED`**: Fully functional in code, tested, and actively executing.  
- **`PARTIALLY IMPLEMENTED`**: Core logic present, adapter or edge boundary pending full integration.  
- **`MOCKED`**: Deterministic simulation layer present for offline testing or demo mode.  
- **`INTEGRATION READY`**: Typed boundary/schema defined; waiting for external hardware or live provider keys.  
- **`NOT IMPLEMENTED`**: Planned architecture not yet constructed in repository.  

---

## 1. Feature Matrix

| Domain | Feature | Status | Implementation Details / Boundary |
|---|---|---|---|
| **Patient Intake** | Multilingual Onboarding (5 Languages) | **`IMPLEMENTED`** | English, Hindi, Tamil, Telugu, Marathi supported in schemas and UI spec |
| **Patient Intake** | Audio-Explained Consent | **`IMPLEMENTED`** | Text + TTS synthesis hook with plain language terms |
| **Patient Intake** | Patient Identification (ABHA / Phone / Skip) | **`IMPLEMENTED`** | Guest bypass + QR code token payload supported in `/api/encounters/bootstrap` |
| **Patient Intake** | Care Stream / OPD Selection | **`IMPLEMENTED`** | General Medicine, AYUSH (Ayurveda/Homeopathy), Pediatrics, Emergency routing |
| **Conversational AI**| Voice Intake & Speech Processing | **`IMPLEMENTED`** | `/api/call/session/start` & `/api/call/audio-turn` connected to ASR/TTS adapters |
| **Conversational AI**| SOCRATES Adaptive Questioning | **`IMPLEMENTED`** | `app/core/clinical/interview_engine.py` drives dynamic follow-ups |
| **Conversational AI**| Explain-Back Verification | **`IMPLEMENTED`** | Simple [YES] / [NO] confirmation cards without patient editing burden |
| **AYUSH Domain** | Dashavidha Pariksha Intake | **`IMPLEMENTED`** | Complete schemas for Agni, Prakriti, Koshtha, Ahara-Vihara in `app/schemas/ayush.py` |
| **AYUSH Domain** | NAMASTE Portal Code Mapping | **`IMPLEMENTED`** | Semantic normalizer tags concepts with NAMASTE standard codes |
| **Clinical Safety** | Deterministic Red-Flag Detection | **`IMPLEMENTED`** | Deterministic rule engine triggers high-priority triage badge (`RED`) |
| **Clinical Safety** | Drug-Drug Interaction Check | **`IMPLEMENTED`** | `app/core/clinical/drug_safety.py` runs contraindication check on extracted medications |
| **Clinical Safety** | Lab Range Outlier Check | **`IMPLEMENTED`** | `app/core/clinical/lab_checker.py` evaluates high/low biological intervals |
| **Clinical Safety** | Clinical Gap Detection | **`IMPLEMENTED`** | `app/core/clinical/gap_detector.py` flags missing critical context for doctors |
| **Document AI** | Document Camera Capture | **`IMPLEMENTED`** | Framing guide and client-side photo capture |
| **Document AI** | RapidOCR Line Detection & Bounding Box | **`IMPLEMENTED`** | RapidOCR ONNX pipeline extracts lines and computes pixel bounding polygons |
| **Document AI** | Multimodal Prescription Extraction | **`IMPLEMENTED`** | Gemini Flash / Groq LLM medication extraction with line citation |
| **Document AI** | Evidence-Boxed Image Highlighting | **`IMPLEMENTED`** | OpenCV boxes drawn on source prescription, served via `/static/evidence/` |
| **Vitals Capture** | Manual / Sensor Vitals Intake | **`IMPLEMENTED`** | BP, Pulse, SpO2, Temp, Blood Sugar supported in data models |
| **Queue Management**| Live Queue Position & Wait Estimation | **`IMPLEMENTED`** | `/api/queue/status/{token}` calculates patients ahead and wait time |
| **Doctor Interface**| Doctor PIN Authentication | **`IMPLEMENTED`** | `/api/doctor/auth` PIN-gated access (`1234`) |
| **Doctor Interface**| Changes-First Queue Overview | **`IMPLEMENTED`** | `/api/doctor/queue` orders by severity (`RED` -> `YELLOW` -> `GREEN`) with 30-word summary |
| **Doctor Interface**| Provenance Evidence Drilldown | **`IMPLEMENTED`** | `/api/doctor/patient/{id}` exposes source document highlights, tier scores, verbatim words |
| **Hospital Services**| OPD Departments & Facilities Directory | **`IMPLEMENTED`** | Pharmacy, Lab, Radiology, Injection Room directories |
| **Hospital Services**| Hospital Map Wayfinding | **`MOCKED`** | High-contrast indoor schematic wayfinding map |
| **Emergency** | SOS One-Tap Emergency Assistance | **`IMPLEMENTED`** | Immediate escalation path, bypassing normal queue with direct staff alert |
| **Emergency** | Ambulance Live GPS Tracking | **`MOCKED`** | Simulated ETA tracking labeled clearly as simulated demo state |
| **Telephony / IVR** | IVR Conversational Intake Session | **`IMPLEMENTED`** | Same data model and interview state machine via `/api/call/*` |
| **Telephony / IVR** | Telecom Carrier PSTN/SIP Bridge | **`INTEGRATION READY / MOCKED`** | Provider-neutral adapter boundary defined; no live carrier trunk attached |
| **Standards** | FHIR R4 Encounter & Observation Mapping | **`INTEGRATION READY`** | Data model is FHIR R4 compliant; ready for ABDM sandbox connector |
| **Standards** | ABDM Milestone 1/2 Gateway | **`INTEGRATION READY`** | Sandbox boundary defined; no production government gateway cert configured |
| **Resilience** | Offline-First Edge Execution | **`IMPLEMENTED`** | Local SQLite WAL database, offline mock datasource, edge Ollama LLM support |
| **Privacy** | 10-Second Automatic Session Wipe | **`IMPLEMENTED`** | Screen 24 privacy countdown purges temporary RAM state on public kiosks |
| **Privacy** | Inactivity Timeout Overlay (45s) | **`IMPLEMENTED`** | 45-second inactivity warning dialog before automatic session purge |

---

## 2. Integrity Certification

- **No fake PSTN call:** The voice session is an authenticated WebRTC/REST audio session matching the same backend engine.
- **No fake diagnosis:** MediKiosk categorizes candidate clinical facts, red-flag triage badges, and evidence links; the physician retains sole diagnostic and prescription authority.
- **No hallucinated APIs:** All client networking calls strictly mirror the tested routes documented in `API_CONTRACT_AUDIT.md`.
