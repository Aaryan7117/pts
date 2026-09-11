# MediKiosk — Architecture Review & Decision Record (v3)

> **Document Status:** CANONICAL DECISION RECORD (v3)  
> **Date:** September 2026 · **Status:** Decisions Agreed, Ready for Hackathon Build  
> **Supersedes:** All v1 and v2 prior records.  

---

## 1. Summary of Architectural Evolution (v1 $\rightarrow$ v2 $\rightarrow$ v3)

The MediKiosk architecture underwent two rigorous red-team audit passes to eliminate all engineering failure points, judge traps, and clinical omissions:
* **Pass 1 (v1 $\rightarrow$ v2):** Eliminated immediate hardware/crash blockers (two-laptop dependency removed, offline ASR floor introduced, PaddleOCR 2.x API breakage fixed with RapidOCR, uncalibrated confidence replaced with arithmetic, line-indexed citation guardrails added).
* **Pass 2 (v2 $\rightarrow$ v3):** Rectified all 43 red-team vulnerabilities from `flaws_found.md`:
  - Eliminated brittle string dictionaries in favor of **NegEx + Multilingual ONNX Embeddings** (15ms).
  - Adopted **AI4Bharat IndicWhisper (ONNX CPU)** for native 5-language speech recognition with zero GPU VRAM impact.
  - Standardized on a **Single 8GB VRAM + 16GB RAM Laptop Core** running Qwen 2.5 7B Q4 on GPU and all other services on CPU.
  - Added full **Ministry of AYUSH Dashavidha Pariksha schemas** (*Agni*, *Prakriti*, *Ahara-Vihara*) mapped to NAMASTE codes.
  - Added deterministic **Drug-Drug Interaction** and **Abnormal Lab Range** engines.
  - Modernized to **`google-genai`** SDK and active **Groq Llama 3.1 70B**.
  - Replaced high-risk physical arcade button soldering with **accessible 80px on-screen touch targets**.
  - Formalized the **Tri-Channel Ingestion Strategy** (Kiosk + BYOD Mobile + 2G Basic Phone IVR).

---

## 2. Complete Decision Record Table

| # | Topic | Prior Flaw / Dilemma | Final v3 Decision | Engineering Rationale |
|---|---|---|---|---|
| **1** | **Offline ASR Floor** | Cloud Bhashini was only ASR; Wi-Fi disconnect demo would crash voice | **AI4Bharat IndicWhisper (ONNX CPU)** | 12,000h Vistaar dataset, 5 languages, runs in 1.4s on CPU, consumes **0 MB VRAM**, aligns with MeitY/Bhashini. |
| **2** | **Online Voice Speed** | Slow cloud transcription or lack of Hinglish support | **Groq Whisper-Large-v3-Turbo / Sarvam AI** | Sub-250ms latency, free tier on Groq, Sarvam handles colloquial Hinglish code-switching. |
| **3** | **Symptom Concept Normalization** | Brittle 200-word exact string dictionary or slow LLM chat | **NegEx + Multilingual Sentence Embeddings** | Deterministic negation guard (`nahi`, `not`) + `paraphrase-multilingual-MiniLM` ONNX (15ms) cosine matching against SNOMED/NAMASTE. |
| **4** | **Hardware Topology** | Confusing multi-laptop split (Laptop 1 vs 2 vs 3) | **Single 8GB VRAM Laptop Core** | Qwen 2.5 7B Q4 (~4.7GB VRAM) on GPU; IndicWhisper, RapidOCR, Embeddings, TTS, FastAPI on 8-core CPU threads. 100% self-sufficient. |
| **5** | **Memory Headroom & Bailout** | 7B model might spill to RAM if 4K external projector connected | **Pre-pulled Qwen 2.5 3B Fallback** | Instant `.env` switch drops LLM VRAM to 1.9GB, giving 4.5GB emergency buffer if venue displays choke VRAM. |
| **6** | **Document OCR Engine** | PaddleOCR 2.x API errors on Windows and consumes excessive resources | **RapidOCR (`rapidocr_onnxruntime`)** | C++ ONNX engine, clean pip install, ~800MB RAM on CPU, outputs line polygons for bounding box union. |
| **7** | **Evidence Linking ("No Receipt, No Fact")** | LLMs hallucinate coordinates if asked for bounding boxes | **Line-Indexed Citation Guardrails** | OCR lines are indexed `[L1, L2]`; LLM schema requires `source_lines: list[int]`; backend deterministically renders SVG highlight box over original Rx. |
| **8** | **Ministry of AYUSH Depth** | Vague buzzwords ("Layer 3", "Dashavidha Pariksha"), zero schemas | **Machine-Readable Pydantic AYUSH Models** | Explicit models for *Agni* (Sama, Vishama, Tikshna, Manda), *Prakriti*, *Ahara-Vihara*, and pending doctor exam checklists (Nadi, Jihva). |
| **9** | **Drug Safety Engine** | SIH26047 mandates drug interaction detection; previously missing | **Deterministic Pairwise Matrix** | Covers allopathic-allopathic (Metformin + Contrast, Warfarin + Aspirin) and herb-drug interactions (Ashwagandha + Sedatives, Yashtimadhu + Antihypertensives). |
| **10** | **Abnormal Lab Range Checker** | SIH26047 mandates flagging abnormal labs; previously missing | **Physiological Reference Intervals Engine** | Tests FBS, PPBS, HbA1c, Creatinine, Hemoglobin with `NORMAL`, `HIGH`, `LOW`, and `CRITICAL_PANIC` flags. |
| **11** | **Multilingual Scope** | Only Hindi/English; ignored AYUSH national diversity | **5 Priority Languages (EN, HI, TA, TE, MR)** | Tamil covers **Siddha**; Telugu & Marathi cover major Ayurvedic hubs; shared vector space handles all 5 languages. |
| **12** | **Deprecated Models & SDKs** | Groq Llama 3.3 70B deprecated Aug 16, 2026; legacy `google.generativeai` SDK | **Llama 3.1 70B + Modern `google-genai` SDK** | Active Groq model; Gemini provider uses official typed `response_schema` constraints. |
| **13** | **Offline Failover Lag** | When offline, cloud requests hang on TCP connection timeouts | **Active Socket Connectivity Probe (150ms)** | Bypasses cloud instantly when offline; zero UI stalls during the live Wi-Fi unplug test. |
| **14** | **Physical Hardware Buttons** | Team lacked time/hardware to solder USB arcade buttons | **Accessible 80px On-Screen Touch Targets** | High-contrast Green [हाँ / YES] and Red [नहीं / NO] buttons in UI. Zero hardware failure risk. |
| **15** | **Zero-Literacy Patient Verification** | Illiterate patients cannot verify text on screen | **Piper TTS Closed-Loop Audio Explain-Back** | Synthesizes plain Hindi/regional audio summary; patient confirms with Green/Red touch buttons. |
| **16** | **Privacy & DPDP Act 2023** | Passwords unusable by rural elderly; unencrypted storage | **Token Intake + Audio Purge + SQLCipher** | Temporary Kiosk Token (e.g. `TK-4819`), ephemeral audio wiped post-session, AES-256 DB encryption, Doctor PIN gate. |
| **17** | **Contradiction Resolution Policy** | Undefined conflict hierarchy when patient contradicts prescription | **Non-Destructive Dual-Fact Preservation** | Retains both prescription fact and patient statement; renders adherence drift timeline; flags conflict for doctor review. |
| **18** | **Omnichannel Ingestion Vision** | Touchscreen kiosk alone leaves out rural elderly non-smartphone owners | **Tri-Channel Strategy (Kiosk + BYOD + IVR)** | Core hackathon build is Web Kiosk; ecosystem extends to BYOD Mobile and Toll-Free 2G Basic Phone IVR. |

---

## 3. Hardware Resource Map (16GB RAM + 8GB VRAM)

```
┌────────────────────────────────────────────────────────────────────────┐
│             SINGLE 8GB VRAM LAPTOP (ALL SERVICES SELF-SUFFICIENT)      │
├────────────────────────────────────────────────────────────────────────┤
│ GPU VRAM (8.0 GB Physical Limit):                                      │
│  • Ollama Qwen 2.5 7B Q4_K_M:                            ~4.70 GB      │
│  • Attention KV Cache (2048 context):                    ~0.60 GB      │
│  • CUDA Runtime & Buffers:                               ~0.40 GB      │
│  • Windows DWM + 1080p Display:                          ~1.00 GB      │
│  TOTAL VRAM: ~6.70 GB / 8.0 GB (1.30 GB Safe Headroom) ✅              │
├────────────────────────────────────────────────────────────────────────┤
│ SYSTEM RAM (16.0 GB Physical Limit):                                   │
│  • Windows 11 Base OS:                                   ~3.50 GB      │
│  • Chromium UI (Kiosk + Doctor Tabs):                    ~1.00 GB      │
│  • AI4Bharat IndicWhisper ONNX (CPU):                    ~0.90 GB      │
│  • RapidOCR ONNX (CPU):                                  ~0.80 GB      │
│  • Multilingual MiniLM Embeddings (CPU):                 ~0.15 GB      │
│  • Piper TTS ONNX (CPU):                                 ~0.05 GB      │
│  • FastAPI Backend + SQLite WAL:                         ~0.30 GB      │
│  TOTAL RAM: ~6.70 GB / 16.0 GB (~9.30 GB Free System RAM) ✅           │
└────────────────────────────────────────────────────────────────────────┘
```

---

*MediKiosk SIH26047 Architecture Review & Decision Record (v3 Finalized).*
