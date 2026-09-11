# MediKiosk — AI-Powered Patient Tracking & Clinical Intake System

A multi-channel, edge-first clinical intake and patient tracking platform designed for Indian healthcare settings. MediKiosk bridges patient registration, vernacular voice intake (ASR/TTS), multilingual clinical interviews, prescription scanning (OCR), AYUSH/Allopathy drug safety checking, and real-time doctor queue triage.

---

## 🌟 Architecture & Highlights

- **Edge-First + Cloud Fallback**: Zero-cloud dependency for core triage; cloud LLM/ASR adapters (Groq, Gemini, Sarvam) available for high accuracy.
- **Multilingual Clinical Voice Intake**: Supports Hindi, Tamil, Telugu, Marathi, and English.
- **AYUSH & Allopathic Drug Interaction Engine**: Safety cross-checking between 18+ high-risk herbal-allopathic pairs (e.g., Ashwagandha + Sedatives, Garlic/Ginkgo + Anticoagulants).
- **Clinical Rule & Gap Detection**: Red-flag symptom detection (chest pain, stroke signs), diabetic history gaps, and lab value anomaly alerts.
- **Unified Doctor Queue**: Real-time triage with severity scoring (Emergency, Priority, Normal) and live audio/document review.
- **FastAPI Backend**: Fully async, SQLite with WAL mode, Pydantic v2 schemas.

---

## 📁 Repository Structure

```
├── app/
│   ├── api/                   # REST API routes
│   │   ├── call_sessions.py   # Voice intake & conversational turns
│   │   ├── doctor.py          # Doctor dashboard & encounter finalization
│   │   ├── documents.py       # Prescription & report upload / OCR
│   │   ├── encounters.py      # QR code token bootstrap & status
│   │   └── queue.py           # Doctor triage queue management
│   ├── core/
│   │   ├── adapters/          # Pluggable AI model adapters (ASR, TTS, LLM, OCR)
│   │   └── clinical/          # Clinical logic (Drug safety, gap detector, normalizer)
│   ├── schemas/               # Pydantic v2 data models
│   ├── config.py              # Environment configuration
│   ├── database.py            # SQLite async database setup & tables
│   └── main.py                # FastAPI app initialization & routing
├── static/                    # Evidence, prescriptions, and upload storage
├── .env.example               # Template environment configuration
├── requirements.txt           # Python dependencies
├── run.py                     # App launcher
└── MediKiosk_*.md             # Architecture, handoff & execution plans
```

---

## 🚀 Quick Start

### 1. Clone & Setup Environment

```bash
git clone https://github.com/Aaryan7117/pts.git
cd pts

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```
Edit `.env` to configure your API keys (Groq, Gemini, Sarvam) and model paths if running offline models.

### 3. Launch the Server

```bash
python run.py
```
The server will start at `http://localhost:8000`.

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/health`

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/api/encounters/bootstrap` | POST | Initialize encounter from QR token & language |
| `/api/call/start` | POST | Begin conversational voice session |
| `/api/call/turn` | POST | Process patient audio turn / response |
| `/api/documents/upload` | POST | Upload and process prescription/document |
| `/api/queue` | GET | List patient queue sorted by priority |
| `/api/doctor/encounter/{id}` | GET | Fetch clinical card, facts & safety flags |
| `/api/doctor/finalize` | POST | Doctor final sign-off & prescription issue |

---

## 👥 Authors & Contributors
- **Aaryan Madhan** (@Aaryan7117) - *Backend Lead Developer*
- **R Mubashir Sheriff** (@mubashir-73) - *Android & Telephony Developer*
