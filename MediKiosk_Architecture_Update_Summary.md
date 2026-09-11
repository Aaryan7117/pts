# 🚀 MediKiosk — Architecture & Model Stack Update (September 2026)

> **Summary for Team Members:** Comprehensive overview of recent architectural upgrades, model selections, and clinical intelligence enhancements across Cloud and Edge tiers.

---

## 📌 Executive Summary of What Changed

| Component | Previous Baseline | Upgraded Production Architecture | Impact & Rationale |
|---|---|---|---|
| **Primary Cloud Vision & OCR** | RapidOCR / Tesseract pipe | **Google Gemini Flash (Multimodal VLM)** | Direct photo-to-JSON in 1 shot! Reads cursive doctor handwriting and outputs 2D bounding boxes (`box_2d`). |
| **Doctor UI Visual Grounding** | Text line citations only | **Interactive Bounding Box Highlighting** | Clicking a medication on the Doctor Dashboard dynamically highlights that exact handwritten word on the physical prescription slip. |
| **Primary Cloud Speech** | Groq Whisper + Piper | **Sarvam AI (Saaras V4 ASR + Bulbul V3 TTS)** | Near-human Indian regional accents across all 5 priority languages (Hindi, Tamil, Telugu, Marathi, English). |
| **Offline Speech Synthesis (TTS)**| Piper TTS (basic robotic voice) | **AI4Bharat IndicF5 (Near-Human Diffusion TTS)** | Massive quality leap (MOS 4.0+ across 11 Indian languages). Piper retained as ultra-lightweight CPU fallback. |
| **Offline Speech Recognition (ASR)**| OpenAI Whisper base | **AI4Bharat IndicConformer / IndicWhisper** | Purpose-built by IIT Madras on 12,000h Vistaar dataset for Indian regional phonetics and code-mixing. |
| **Offline Clinical LLM** | 3B/7B generic | **Qwen 2.5 7B Instruct (Q4_K_M)** | Top-tier 7B model in the world for clinical entity extraction, AYUSH reasoning, and strict JSON compliance. |
| **System Deployment Topology** | Monolithic standalone | **Distributed Hospital Edge Architecture (Thin Client + Edge Node)** | 64% cheaper hardware cost, 78% power reduction, 100% offline local clinic LAN/Wi-Fi operation. |
| **Total Cloud Software Cost** | Variable | **₹0.00 (100% Free Tiers / Credits)** | Google AI Studio free tier + Sarvam ₹100 signup credits covers full hackathon and pilots. |

---

## 1. 👁️ The Vision Upgrade: Multimodal Prescription OCR + Bounding Boxes

### The Problem Solved:
Previously, prescription ingestion required a two-step pipe: noisy OCR text $\to$ LLM guessing medication names. Handwritten doctor notes often produced garbage text that misled the LLM.

### The Upgraded Solution:
1. **Google Gemini Flash Multimodal Engine (Cloud Mode):**
   - The photo of the handwritten prescription is sent directly to Gemini Flash's vision encoder.
   - It deciphers doctor handwriting, identifies Indian brand names (*Pantocid-DSR*, *Glycomet-GP*, *Augmentin 625*), extracts dosages/frequencies, and outputs validated Pydantic JSON in **under 1 second**.
2. **Interactive 2D Bounding Box (`box_2d`) Grounding:**
   - Gemini Flash natively returns normalized coordinates: `box_2d: [ymin, xmin, ymax, xmax]` on a `0-1000` grid.
   - **Doctor Experience**: On the Doctor Dashboard, clicking or hovering over any extracted medicine card projects an interactive glowing highlight box directly over that exact handwritten line on the scanned prescription image!
   - Doctors verify the original doctor's handwriting in 1 second—**zero blind AI trust**.
3. **Offline Floor**:
   - When offline, **RapidOCR (PP-OCRv5)** runs on CPU threads to extract word-level quad polygons, paired with local **Qwen 7B** extraction.

---

## 2. 🎙️ The Speech Upgrade: Near-Human Regional Voices

### Priority Languages Supported (5 Core):
1. **Hindi (`hi`)** — Central & North India OPDs (AIIA New Delhi)
2. **Tamil (`ta`)** — Siddha medicine core language (Southern AYUSH centres)
3. **Telugu (`te`)** — High-volume South-Central OPDs
4. **Marathi (`mr`)** — Western India Ayurvedic colleges hub
5. **English (`en`)** — Clinical lingua franca, doctor notes, FHIR bundles

### Speech Synthesis (TTS):
- **Cloud Primary**: **Sarvam Bulbul V3** (<250ms latency, native Indian accents, sounds like an authentic human healthcare assistant).
- **Offline Primary**: **AI4Bharat IndicF5** (State-of-the-art diffusion speech model by IIT Madras supporting all 5 priority languages with high naturalness).
- **Offline Fallback**: **Piper TTS** (ONNX CPU, ultra-lightweight emergency fallback).

### Speech Recognition (ASR):
- **Cloud Primary**: **Sarvam Saaras V4** (Sub-second transcription, unmatched code-mixing like Hinglish/Tanglish).
- **Offline Floor**: **AI4Bharat IndicConformer 600M / IndicWhisper** (Runs on CPU threads via ONNX Runtime, 0 MB GPU VRAM utilized).

---

## 3. 🌐 Distributed Hospital Edge Architecture (Thin-Client + Edge Server)

### Why This is an Enterprise Standard for Public Hospitals & Rural PHCs:
In real Primary Health Centres (PHCs) and government hospitals:
- You **never** place an expensive ₹1.2 Lakh GPU workstation inside a public waiting hall kiosk. It risks theft, physical damage, and overheating.
- **Enterprise Design**:
  1. **Thin-Client Kiosk Terminals**: Inexpensive touchscreen tablets, mini-PCs, or kiosks in the waiting halls running only the React UI, microphone, and webcam.
  2. **On-Premise Edge AI Server Node**: A single dedicated GPU computing unit located safely in the clinic's administrative or IT closet.
  3. **Local Hospital Intranet**: Communication happens over the **local offline clinic Wi-Fi or LAN subnet**. **Zero internet required!**

### Hard Financial ROI:
- **Monolithic Kiosks (GPU in each kiosk)**: 3 kiosks × ₹1,20,000 = **₹3,60,000** CapEx | 900W power draw.
- **Distributed Edge Node**: 1 Edge Server (₹85,000) + 3 Thin Clients (₹45,000) = **₹1,30,000** CapEx | 195W power draw.
- **Savings**: **~64% CapEx reduction**, **78% power savings** (operates 8+ hours on standard rural PHC solar/UPS backup).

---

## 4. 🛡️ Deterministic Clinical Safety Core (Zero Hallucination)

1. **Negation Guard (NegEx)**:
   - Multilingual syntax filter in 5 languages ensures statements like *"bukhar nahi hai"* or *"thalaivali illai"* are never recorded as positive symptoms.
2. **Pairwise Drug-Drug & Herb-Drug Interaction Matrix**:
   - 100% deterministic matrix screening allopathic and AYUSH combinations (e.g., Ashwagandha + Sedatives, Metformin + Radiopaque contrast, Warfarin + Aspirin).
3. **Abnormal Lab Range Checker**:
   - Reference interval evaluator flagging normal, high, low, and panic values (e.g., HbA1c, Fasting Blood Glucose, Serum Creatinine).
4. **Ministry of AYUSH Dashavidha Pariksha Modeling**:
   - Structured Pydantic schemas for *Agni*, *Prakriti*, and *Ahara-Vihara* lifestyle factors mapped to official NAMASTE portal terminology.

---

## 5. 🎪 Live Demo Strategy for Hackathon Presentation

### Act 1: "The Wow" (Cloud Mode — Broadband Connected)
- Patient speaks vernacular Hindi/Tamil $\to$ Sarvam Saaras transcribes with code-mixing.
- Handwritten prescription scanned $\to$ Gemini Flash vision extracts medicines and `box_2d` bounding boxes in <1s.
- Natural regional voice reads back summary via Sarvam Bulbul V3.
- **Judge reaction**: *"It reads messy doctor handwriting and sounds like a real healthcare worker!"*

### Act 2: "The Resilience & Edge Offline Proof" (Zero Internet)
- Unplug internet / toggle mobile data OFF on the local Wi-Fi router.
- Show network status: **Cellular data OFF, Local Subnet IPv4 only (`192.168.137.x`)**.
- Same flow executes offline: IndicConformer ASR $\to$ Qwen 7B extraction $\to$ RapidOCR $\to$ IndicF5 TTS.
- **Judge reaction**: *"It's a genuine distributed hospital edge system that works completely offline!"*

### Act 3: "The Clinical Safety & Visual Evidence" (Doctor Cabin)
- Doctor opens dashboard: clicks extracted medicine $\to$ bounding box glows over the original paper prescription scan.
- Caught drug-drug interaction alert and triage score shown.
- **Judge reaction**: *"This is clinically sound, safe, and ready for primary healthcare deployment."*
