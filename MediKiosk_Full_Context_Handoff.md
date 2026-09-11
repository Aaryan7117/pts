# MediKiosk — Complete Build Handoff (SIH26047 — v3)

**Team handoff document. Contains: problem context, research, architecture, innovation stack, build plan, demo script, pitch narrative.**  
**Last updated: September 2026 (v3 Finalized)**  

---

## 0. Problem Statement & Operational Reality

- **PS ID:** SIH26047
- **Title:** Patient Case-Taking Software
- **Organization:** Ministry of AYUSH
- **Department:** All India Institute of Ayurveda (AIIA)
- **Category:** Software
- **Theme:** Smart Automation

### The Core Problem in Numbers:
India's public hospital outpatient departments (OPDs) see **4,000–10,000 patients every single day**. Consultations average **2 to 5 minutes per patient** (BMJ Open 2017, 67-country global study — India ~2 min average). 

Clinical history-taking, which classically accounts for **70% to 80% of diagnostic accuracy**, gets drastically compromised under this time pressure.

### The AYUSH Dimension:
In the Ministry of AYUSH and AIIA, clinical history is significantly more granular than allopathic history alone. Classical Ayurvedic examination requires **Dashavidha Pariksha** (Assessment of *Prakriti*, *Vikriti*, *Agni*, *Koshtha*, *Sara*, *Samhanana*, *Pramana*, *Satmya*, *Satva*, *Ahara Shakti*, *Vaya*, and *Ahara-Vihara* lifestyle causative factors). Manually recording this in a 2-minute encounter is clinically impossible.

### The First-Mile Bottleneck:
Patient records in India are scattered across crumpled paper prescriptions, handwritten clinic notes, and lab slips. While the national digital backbone (ABDM, ABHA IDs, FHIR exchange) exists, the **"first-mile" bridge**—capturing structured history, digitizing messy documents, and screening red flags *before* the patient steps into the doctor's cabin—remains completely broken.

### The Solution:
MediKiosk is an **edge-first, patient-facing conversational history intake kiosk and pre-consultation intelligence engine**. It captures voice and touch history across **5 Indian languages**, digitizes prescriptions into verifiable evidence receipts, screens for drug interactions and abnormal lab values, and delivers a changes-first, 30-word triage summary to the physician's workstation.

---

## 1. Why Every Competitor Falls Short (The Landscape)

> **IMPORTANT: SIH judges will evaluate 10+ teams who chose this exact problem statement. Know this comparison cold.**

| Solution Category | Examples | What They Do | Fatal Flaws Caught by Judges |
|---|---|---|---|
| **Generic Chatbots (Rival SIH Teams)** | Navira, Medicure, standard OpenAI wrappers | Basic React form asking ChatGPT for symptoms | **100% Cloud-dependent.** If Wi-Fi drops in a rural PHC, crashes with `Failed to fetch`. Unbounded LLM hallucinates dosages. Zero AYUSH depth. |
| **Symptom Checkers** | Ada Health, Infermedica, Ubie | Adaptive branching interviews for consumer triage | Cloud-only, English/Western focus, zero document ingestion, zero AYUSH/Dashavidha Pariksha depth. |
| **Ambient AI Scribes** | Nuance DAX, Abridge, Nabla | Ambient mic transcribing doctor-patient visit in real-time | Doctor-facing, runs *during* consult, does not solve the first-mile pre-intake wait. |
| **National AYUSH Infra** | A-HMIS, NAMASTE Portal, CCRAS Prakriti | ABDM/FHIR backend terminology and hospital records | Back-office hospital software; has no patient-facing first-mile intake interface. |

### The Gap MediKiosk Exploits:
1. **Patient-Facing & Pre-Consultation:** Reclaims the 45-minute unproductive waiting room time.
2. **100% Self-Sufficient Offline Floor on 1 Laptop:** Runs without internet on a single 8GB machine via AI4Bharat IndicWhisper, RapidOCR, and Qwen 2.5 7B.
3. **No Receipt, No Fact:** Every extracted medication is traceable to an exact pulsing bounding polygon on the original paper prescription scan.
4. **NegEx + Multilingual Vector Embeddings:** Instant 15ms concept mapping across 5 languages that never misinterprets negated symptoms (*"bukhar nahi hai"* $\ne$ fever).
5. **Deterministic Safety Engines:** Hardcoded pairwise drug-drug interaction matrix and physiological abnormal lab ranges.
6. **Proactive Silence Detection:** Flags what the patient *wasn't* asked based on condition-specific rules.
7. **Native Ministry of AYUSH Modeling:** Machine-readable Pydantic schemas for *Agni*, *Prakriti*, and *Ahara-Vihara* mapped to NAMASTE portal terminology.

---

## 2. Omnichannel Ingestion Architecture: Meeting Patients Where They Are

While our core hackathon deliverable is the **In-Clinic Web Kiosk**, MediKiosk is architected as an **omnichannel clinical intake platform** that feeds into a single `ClinicalFact` backend:

```
                  ┌─────────────────────────────────────────────────────────┐
                  │                 MEDIKIOSK TRI-CHANNEL INTAKE            │
                  └─────────────────────────────────────────────────────────┘
                                               │
             ┌─────────────────────────────────┼────────────────────────────────┐
             ▼                                 ▼                                ▼
    CHANNEL 1: IN-CLINIC KIOSK        CHANNEL 2: BYOD MOBILE / WEB     CHANNEL 3: 2G BASIC PHONE IVR
  • Primary Core (Our Build)         • Ecosystem Extension             • Rural Elderly Backup (75+ yrs)
  • Single 8GB Laptop at Hospital    • QR scan from waiting queue      • Toll-free telephone call
  • Offline + Online Web Kiosk       • Patient's own smartphone        • Keypad DTMF + Voice prompts
  • "Speak-to-Fill" card UI          • Pre-fills from home             • Zero smartphone/internet needed
  • Document camera scan station     • Uploads gallery photos of Rx    • Natural language telephony
             │                                 │                                │
             └─────────────────────────────────┼────────────────────────────────┘
                                               ▼
                         ┌───────────────────────────────────────────┐
                         │       UNIFIED CLINICAL FACT ENGINE        │
                         │  • NegEx + Multilingual Embeddings        │
                         │  • Dashavidha Pariksha (AYUSH Schema)     │
                         │  • Forensic Medication Drift Timeline     │
                         │  • Drug-Drug Interaction Matrix           │
                         │  • Abnormal Lab Range Checker             │
                         │  • Proactive Clinical Gap Rules           │
                         └─────────────────────┬─────────────────────┘
                                               │
                                               ▼
                         ┌───────────────────────────────────────────┐
                         │             DOCTOR DASHBOARD              │
                         │  • One-Tap Queue Intelligence Triage      │
                         │  • Changes-First Patient Summary          │
                         │  • Bounding-Box Evidence Drilldown        │
                         │  • DPDP Act Compliance & Audit Trail      │
                         └───────────────────────────────────────────┘
```

1. **Channel 1 (In-Clinic Kiosk — Primary Core):** Touch + Voice kiosk in the OPD waiting area. Runs on the hospital's local 8GB edge machine with camera scan station and high-contrast touch controls.
2. **Channel 2 (Patient BYOD Mobile/Web — Ecosystem Vision):** A patient waiting in a 200-person queue scans a QR code on their token and completes the "Speak-to-Fill" cards on their own mobile browser.
3. **Channel 3 (2G Basic-Phone IVR — Rural Accessibility):** For 75-year-old rural patients without smartphones, a toll-free telephone number provides an automated voice/keypad intake loop (like Indane gas booking or CoWIN 1075) that pipes into the exact same database.

---

## 3. Our Innovation Stack — The 6 Differentiators

### Innovation 1: Forensic Medication Adherence Timeline
* **What it is:** Traditional systems only record "current medications". MediKiosk tracks the **temporal drift** between what was historically prescribed and what the patient actually did.
* **The Clinical Story:**
  ```
  Metformin 500mg ──[Rx: March 2026]──→ [Patient: Stopped June 2026] ──→ [New Rx: Aug 2026, 1000mg]
  ```
* **Why Judges Care:** Invisible non-adherence causes major clinical complications. The doctor sees a visual timeline with the 60-day gap highlighted in amber before prescribing a higher dose.

### Innovation 2: NegEx + Multilingual Semantic Concept Mapping
* **What it is:** Patients describe symptoms colloquially across 5 languages (*"pet mein jalan"*, *"நெஞ்சு எரிச்சல்"*, *"छातीत जळजळ"*). 
* **The Architecture:**  
  1. Deterministic NegEx pre-filter checks for negation terms (`nahi`, `illai`, `ledu`, `not`).
  2. Multilingual sentence transformer (`paraphrase-multilingual-MiniLM-L12-v2` ONNX) embeds the statement in 15ms on CPU.
  3. Mathematical cosine similarity maps the phrase to standard `SNOMED-CT` and `NAMASTE` codes without slow or hallucinatory LLM round-trips.

### Innovation 3: Proactive Silence Detection ("What Wasn't Asked")
* **What it is:** Diagnostic errors in busy OPDs usually stem from the question that was **never asked**. After the intake interview, our rule engine checks captured facts against expected clinical standards and generates a **Clinical Gap List**.
* **What the Doctor Sees:**
  ```
  ⚠ CLINICAL GAPS DETECTED (2):
    ✗ Patient is 55+, diabetic, on Metformin — NOT asked about: peripheral neuropathy (foot numbness)
    ✗ Patient reports joint pain >3 weeks — NOT asked about: morning stiffness duration
  ```

### Innovation 4: Closed-Loop Explain-Back (Audio Readback for Zero-Literacy)
* **What it is:** Showing a wall of text fails for non-literate patients. The kiosk uses **Piper TTS** to synthesize a plain-language summary in the patient's language:
  > *"Aapne bataya ki aapko 3 hafte se ghutno mein dard hai aur Methotrexate 2 hafte pehle band kar di thi. Kya yeh sahi hai?"*
* **Verification:** Screen displays massive, high-contrast on-screen buttons: **Green [हाँ / YES]** and **Red [नहीं / NO]**. Tapping NO immediately opens a correction loop.

### Innovation 5: Doctor Queue Intelligence (One-Tap Triage)
* **What it is:** Doctors usually call patients blindly by token number. MediKiosk generates a **30-word structured case summary** and severity badge for every waiting patient.
* **Doctor Action:** The doctor reviews the waiting queue from their desk and triages with one tap:
  * `🔴 Token #42 — Ramesh, 62M — Acute chest pain 2 hrs, diabetic [CALL NEXT - URGENT]`
  * `🟡 Token #43 — Meena, 68F — Knee pain 3 wks, stopped Methotrexate [SEE NORMALLY]`

### Innovation 6: Line-Indexed Evidence Boxing ("No Receipt, No Fact")
* **What it is:** When RapidOCR scans a prescription, detected lines are indexed (`[L1]`, `[L2]`). The LLM is schema-constrained to cite line indices (`source_lines: [2, 3]`). 
* **The Visual Clincher:** Clicking any extracted medication on the Doctor Dashboard displays the original prescription image with the exact line region pulsing in a crisp yellow highlight box. The AI cannot fabricate coordinates.

---

## 4. The Core Data Model: `ClinicalFact`

Every intake channel writes into this immutable, audited table:

```json
{
  "id": "fact-9821-uuid",
  "encounter_id": "enc-4819-uuid",
  "category": "chief_complaint | medication | allergy | vital | lab_result | ayush_agni | ayush_prakriti | ayush_ahara",
  "field": "current_medication",
  "value": "Methotrexate",
  "dose": "10 mg",
  "frequency": "weekly",
  "patient_words": "peeli goli, hafte mein ek baar",
  "normalized_concept": "Methotrexate 10mg tablet",
  "concept_code": "SNOMED:372658004",
  "provenance_tier": "TOUCH | LOOKUP | EMBEDDING | LLM | OCR",
  "source_type": "patient_voice | document_ocr | explain_back_verified",
  "source_reference": {
    "type": "document_ocr",
    "document_id": "doc-01-uuid",
    "line_indices": [2, 3],
    "bbox": [412, 188, 690, 244],
    "ocr_confidence": 0.94,
    "raw_text": "Tab. Methotrexate 10mg 1 tab weekly"
  },
  "confidence": 0.89,
  "confidence_breakdown": {
    "tier_score": 0.95,
    "input_quality": 0.94,
    "completeness": 1.0
  },
  "temporal_state": "prescribed | taking | stopped | dose_changed",
  "valid_from": "2026-02-10",
  "valid_until": "2026-08-25",
  "status": "patient_confirmed",
  "created_at": "2026-09-11T10:14:22Z"
}
```

### Deterministic Confidence Arithmetic:
$$\text{Confidence} = \text{Tier Score} \times \text{Input Quality} \times \text{Completeness}$$
- `tier_score`: Touch = 1.0, Vector Embedding = Cosine Score ($0.82–0.98$), LLM Extraction = capped at 0.70.
- `input_quality`: OCR or ASR engine quality metric ($0.0–1.0$).
- `completeness`: `filled_fields / required_fields`.
- **Tiers:** $\ge 0.85$ (High, locked) · $0.55–0.85$ (Medium, requires explain-back confirmation) · $< 0.55$ (Refuse, flag for human doctor review).

---

## 5. System Architecture & Hardware Budget

### Single 8GB Laptop Core (100% Self-Sufficient):
- **Machine Specs:** 8GB VRAM (NVIDIA RTX 3060/3070/4060), 8-Core/16-Thread CPU, 16GB System RAM.
- **VRAM Allocation (8GB Limit):**
  - Ollama Qwen 2.5 7B Q4: **~4.70 GB**
  - KV Cache & CUDA context: **~1.00 GB**
  - Windows DWM + 1080p display buffer: **~1.00 GB**
  - **Headroom: ~1.30 GB free (Zero CUDA OOM risk)**
- **System RAM Allocation (16GB Limit):**
  - Windows 11 base: ~3.50 GB
  - Chromium UI (Kiosk + Doctor tabs): ~1.00 GB
  - AI4Bharat IndicWhisper (ONNX CPU): ~0.90 GB (**0 MB VRAM**)
  - RapidOCR (`rapidocr_onnxruntime` CPU): ~0.80 GB (**0 MB VRAM**)
  - Multilingual MiniLM Embeddings (ONNX CPU): ~0.15 GB (**0 MB VRAM**)
  - Piper TTS (ONNX CPU): ~0.05 GB (**0 MB VRAM**)
  - FastAPI backend + SQLite WAL: ~0.30 GB
  - **Free RAM: ~9.30 GB (Zero thrashing)**

---

## 6. Full 5-Language Multilingual Scope

1. **English (`en`)** — Doctor dashboard, clinical notes, FHIR R4 JSON bundles.
2. **Hindi (`hi`)** — Central/North India OPD intake (AIIA New Delhi).
3. **Tamil (`ta`)** — Foundational language of **Siddha medicine** (AYUSH southern institutes).
4. **Telugu (`te`)** — High-volume South Central India OPDs.
5. **Marathi (`mr`)** — Western India AYUSH hub (highest concentration of Ayurvedic colleges).

---

## 7. The Scripted 7-Beat Judge Demonstration (~7 min)

### Persona:
**"Meena,"** 68F, Hindi-speaking, limited literacy, knee joint pain for 3 weeks, stopped taking Methotrexate 10mg two weeks ago, carrying an old paper prescription.

---

### Beat 1: First-Mile Intake & Multilingual Consent (1 min)
* Patient approaches kiosk, taps **[हिन्दी]** from the 5 language cards.
* Audio + text consent screen: *"आपका डेटा सुरक्षित है..."* $\rightarrow$ Taps **[सहमत / Agree]**.
* Patient speaks into the mic: *"Mujhe teen hafte se ghutno mein dard hai."*
* Kiosk displays live transcript. The **NegEx + Multilingual Embedding Normalizer** maps it to `Knee joint pain (SNOMED:202446002)` in 15ms. The "Speak-to-Fill" card on screen lights up green.

### Beat 2: The Internet Disconnect Proof (30 sec) — THE CLINCHER
* **Action:** Physically unplug the Ethernet cable / turn off Wi-Fi on the laptop in front of the judges.
* Header flips from `CLOUD: ONLINE` $\rightarrow$ `EDGE: OFFLINE`.
* Kiosk transitions to the next question with **zero lag or TCP connection stall** (handled by the 150ms socket probe).
* Speech and extraction continue running locally on **AI4Bharat IndicWhisper + local Qwen 7B**.

### Beat 3: Physical Prescription Scan & Evidence Boxing (1.5 min)
* Place Meena's printed prescription on the scan station $\rightarrow$ Tap **[स्कैन करें / Scan]**.
* RapidOCR ONNX processes text lines in $<1.5\text{s}$ on CPU.
* Qwen 7B extracts medications, outputting `source_lines: [2, 3]`.
* System deterministically renders bounding polygons over the original prescription image.

### Beat 4: Adherence Drift & Contradiction Resolution (1 min)
* Scanned prescription lists `Methotrexate 10mg weekly`.
* Patient previously stated she stopped taking it.
* Kiosk asks via Piper TTS: *"इस पर्चे में Methotrexate 10mg लिखा है। क्या आप अभी ले रहे हैं या बंद कर दिया?"*
* Patient taps on-screen **[बंद कर दिया / Stopped]**.
* System updates `temporal_state: stopped`, `valid_until: ~2 weeks ago`. The medication adherence timeline visually updates showing the 14-day gap.

### Beat 5: Closed-Loop Audio Explain-Back (45 sec)
* System synthesizes a plain Hindi audio sentence: *"आपने बताया कि 3 हफ्ते से घुटनों में दर्द है और Methotrexate 2 हफ्ते पहले बंद कर दी थी। क्या यह सही है?"*
* Screen presents two massive, 80px high-contrast buttons: **Green [हाँ / YES]** and **Red [नहीं / NO]**.
* Patient presses **[हाँ / YES]** $\rightarrow$ Facts locked with status `explain_back_verified`.

### Beat 6: Doctor Intelligence & Evidence Drilldown (2 min)
* Doctor workstation unlocks with 4-digit PIN (`1234`).
* **Queue Intelligence:** Meena appears with severity badge `🟡 MEDICATION_CONFLICT`. Doctor clicks **[CALL NEXT]**.
* **Changes-First Summary:** Stopped medications and recent symptom changes appear at the top of the screen.
* **Proactive Gap Alert:** Shows: `⚠ NOT asked: Morning stiffness duration (expected for joint pain >2 weeks)`.
* **Evidence Drilldown:** Doctor clicks "Methotrexate" $\rightarrow$ modal displays the original prescription image with the exact line pulsing in yellow.

### Beat 7: Failure-Mode Showcase & Restraint (1 min)
* **Illegible Prescription Refusal:** Place an illegible, doctor-scrawled prescription under the scanner. RapidOCR confidence drops to $0.34 (< 0.50)$.
* **Restraint Behavior:** The kiosk does **NOT** invent a medicine. It displays: *"दवा का नाम स्पष्ट नहीं है — डॉक्टर व्यक्तिगत रूप से जांच करेंगे" (Prescription text unverified — flagged for physician review)*. On the Doctor Dashboard, the item appears with an amber warning badge. 
* Turn Wi-Fi back on $\rightarrow$ IndexedDB sync queue flushes records to central server in 2 seconds with zero duplicates.

---

## 8. Claims — What to Say vs. What NEVER to Say

### Safe, Bulletproof Claims ✅
- *"Edge-first offline architecture running on a single 8GB machine"*
- *"Evidence-grounded extraction where every fact links to an audio waveform or pixel polygon"*
- *"NegEx-guarded multilingual concept normalization across 5 languages"*
- *"Machine-readable AYUSH Dashavidha Pariksha modeling for AIIA clinical workflows"*
- *"Deterministic drug-drug interaction matrix and abnormal lab range alerts"*
- *"Forensic medication adherence timeline showing prescription-to-reality drift"*
- *"Closed-loop audio explain-back for zero-literacy patient verification"*
- *"DPDP Act 2023 compliance with ephemeral audio purge and Doctor PIN gate"*

### NEVER Claim ❌
- ❌ *"Our system diagnoses diseases"* (Illegal medical claim)
- ❌ *"100% zero hallucination guaranteed"* (Scientifically indefensible)
- ❌ *"Our AI replaces OPD nurses or doctors"* (Antagonizes clinical judges)
- ❌ *"Fully certified ABDM integration"* (Claim Level 2 FHIR export, not production cert)
- ❌ *"Reads all doctor cursive handwriting with 100% accuracy"* (Highlight refusal mode instead)

---

*MediKiosk SIH26047 Architecture Team — Complete Build Handoff (v3 Finalized).*
