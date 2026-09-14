# MediKiosk — Web UI/UX Master Flow & Antigravity Design Specification

## 0. Purpose

This document is the **web UI source of truth** for redesigning the already-working MediKiosk backend into a polished, professional healthcare web application.

The goal is **not** to rebuild the backend, Flutter mobile app, AI pipeline, OCR pipeline, IVR, or database.

The goal is to build a **high-quality responsive website** that connects to the existing working APIs and presents the complete MediKiosk patient + doctor workflow with a visual quality comparable to the RetinopathyScan portal style, but using a **light medical theme**.

The repository already exposes FastAPI routes for encounters, conversational voice intake, documents/OCR, queue, doctor dashboard, authentication, patient portal, AYUSH, and IVR. The backend entry point describes the system as serving Kiosk Web UI, Mobile BYOD App, and Doctor Dashboard. [GitHub: app/main.py]

---

# 1. VERIFIED CURRENT BACKEND SURFACE

Repository reviewed:

`Aaryan7117/pts`

Primary backend:

```text
app/main.py
app/api/
    auth.py
    ayush.py
    call_sessions.py
    doctor.py
    documents.py
    encounters.py
    ivr.py
    patient.py
    queue.py
```

The FastAPI application currently registers routers for:

- encounters
- call sessions / voice intake
- documents
- queue
- doctor
- authentication
- patient
- AYUSH
- IVR

The backend also mounts uploaded documents/evidence under `/static`.

The doctor API currently exposes:

```text
POST /api/doctor/auth
GET  /api/doctor/queue
GET  /api/doctor/patient/{encounter_id}
POST /api/doctor/patient/{encounter_id}/call-next
GET  /api/doctor/patient/by-abha/{abha_id}
```

The patient API currently exposes:

```text
GET  /api/patient/dashboard/{identifier}
POST /api/patient/document/upload
```

The backend is therefore already structured around a **patient portal + doctor portal + clinical intake + documents + queue** model.

---

# 2. IMPORTANT IMPLEMENTATION RULE

DO NOT replace working backend behavior.

The web frontend must be an **API-driven presentation layer**.

Use:

```text
Existing FastAPI Backend
        ↓
Typed API Client
        ↓
Web Application State
        ↓
Responsive UI
```

Do not duplicate backend clinical logic in frontend JavaScript.

Do not invent a second database.

Do not create fake patient records when the API can provide real data.

When backend data is unavailable, show an honest empty/loading/error state.

---

# 3. PRODUCT POSITIONING

## Product

**MediKiosk AI**

### Subtitle

**Intelligent Clinical Intake & Patient Care**

### Supporting statement

> Capture patient history through voice and touch, organize medical documents, and prepare a clinician-reviewable summary before consultation.

Tone:

- premium healthcare
- trustworthy
- modern
- calm
- accessible
- clinical
- technology-forward without looking futuristic for no reason

---

# 4. DESIGN DIRECTION

The visual inspiration should come from the existing RetinopathyScan style:

- strong product identity
- large hero headings
- dashboard cards
- compact status pills
- clean navigation
- strong section hierarchy
- professional data presentation
- polished authentication screens
- detailed doctor portal
- patient timeline
- clinical review workflow

However, MediKiosk should NOT copy the dark RetinopathyScan visual system.

Use a **light healthcare interface**.

---

# 5. LIGHT MEDICAL DESIGN SYSTEM

## 5.1 Base colors

```text
Canvas       #F6F9FC
Surface      #FFFFFF
Surface Soft #F8FBFF

Primary      #1667D9
Primary Dark #0D3B7A
Primary Tint #EAF3FF

Teal         #0B8F87
Teal Tint    #E7F8F6

Success      #17824C
Success Tint #EAF8F0

Warning      #B66A00
Warning Tint #FFF6E5

Danger       #C83A3A
Danger Tint  #FFF0F0

Text         #10233E
Muted        #6B7A90
Border       #DCE5F0
```

Use color semantically.

Never rely on color alone:

```text
Status = color + icon + label
```

---

# 5.2 Typography

Use a modern web font.

Recommended hierarchy:

```text
Display      44–56px
H1           36–44px
H2           28–34px
H3           22–26px
Body         16–18px
Small        14px
Label        12–13px uppercase/semibold
```

Keep body text highly readable.

Avoid excessive uppercase body copy.

---

# 5.3 Shape language

Cards:

```text
border-radius: 18–22px
```

Buttons:

```text
border-radius: 12–14px
```

Input fields:

```text
border-radius: 12px
```

Use subtle borders and shallow shadows.

Avoid excessive glassmorphism.

---

# 5.4 Navigation

Desktop:

```text
┌──────────────────────────────────────────────────────────────────┐
│ MediKiosk     Patient / Doctor portal        Search  Help  User │
├───────────────┬──────────────────────────────────────────────────┤
│ Dashboard     │                                                  │
│ Clinical      │                 MAIN CONTENT                     │
│ History       │                                                  │
│ Documents     │                                                  │
│ Medical       │                                                  │
│ Records       │                                                  │
│ Doctors       │                                                  │
│ Queue         │                                                  │
│ Profile       │                                                  │
│ Settings      │                                                  │
└───────────────┴──────────────────────────────────────────────────┘
```

Patient and doctor navigation must be different.

Never expose doctor functionality to patient accounts.

---

# 6. ROUTE MAP

Use a clear route structure.

## Common routes

```text
/
 /welcome
 /account-type
 /help
```

## Patient routes

```text
/patient/login
/patient/register
/patient/language
/patient/consent
/patient/dashboard
/patient/history/new
/patient/history/session
/patient/history/summary
/patient/documents
/patient/documents/:id
/patient/timeline
/patient/queue
/patient/doctors
/patient/doctors/:id
/patient/hospitals
/patient/profile
/patient/settings
/patient/notifications
```

## Doctor routes

```text
/doctor/login
/doctor/register
/doctor/dashboard
/doctor/queue
/doctor/patients
/doctor/patients/:encounterId
/doctor/patients/:encounterId/history
/doctor/patients/:encounterId/documents
/doctor/patients/:encounterId/evidence
/doctor/patients/:encounterId/review
/doctor/patients/:encounterId/consultation
/doctor/patients/:encounterId/prescription
/doctor/referrals
/doctor/analytics
/doctor/profile
/doctor/settings
```

## IVR/browser simulator

```text
/ivr
/ivr/session/:id
```

Only create these pages if the existing backend exposes the necessary data.

---

# 7. GLOBAL APP SHELL

## Header

Left:

```text
MediKiosk logo
MediKiosk AI
```

Center/desktop:

Current section breadcrumb.

Right:

```text
Notifications
Language
Help
Profile avatar
```

Profile menu:

```text
My Profile
Settings
Privacy
Sign Out
```

---

# 8. COMMON UI STATES

Every API-driven page must support:

### Loading

Skeletons matching final layout.

### Empty

Example:

> No patient cases are waiting.

### Error

Example:

> We couldn't load your clinical records.

Buttons:

`Retry`

### Offline

Top banner:

> Connection unavailable. Some features may be limited.

### Success

Use concise confirmation toast/banner.

### Session timeout

Clear sensitive state and return to authentication.

---

# 9. PUBLIC ENTRY FLOW

## PAGE 01 — WELCOME

### Purpose

High-quality MediKiosk landing screen.

### Layout

Two-column desktop.

Left 55%:

```text
MEDIKIOSK AI

Intelligent Clinical
Intake & Patient Care

Capture your symptoms and medical history,
digitize previous medical documents, and
prepare a clinician-ready case before consultation.

✓ Voice + Touch
✓ Multilingual
✓ Medical Document Intelligence
✓ Clinician Review
```

Right 45%:

Centered healthcare illustration or clean abstract clinical graphic.

Primary:

`GET STARTED`

Secondary:

`HOW MEDIKIOSK WORKS`

Footer:

`For patients • clinics • hospitals`

### Interaction

GET STARTED → Account Type.

---

# 10. PAGE 02 — ACCOUNT TYPE

Exactly the role-selection pattern from the RetinopathyScan project.

Title:

## Choose your portal

Subtitle:

> Select how you will use MediKiosk.

Two large cards.

### Patient

```text
PATIENT / INDIVIDUAL

Record symptoms, medical history,
documents and consultation updates.

CONTINUE AS PATIENT
```

### Doctor

```text
MEDICAL PROFESSIONAL

Review patient cases, clinical history,
documents and consultation information.

CONTINUE AS DOCTOR
```

Card hover:

- subtle elevation
- border highlight
- arrow animation

---

# 11. PATIENT AUTHENTICATION

## PAGE 03 — PATIENT LOGIN

Layout:

Left information panel:

```text
MediKiosk AI

Your health history,
organized before consultation.

Voice
Documents
Timeline
Doctor Review
```

Right card:

```text
PATIENT PORTAL

Sign in to your health workspace.

Mobile number / Patient ID
Password / PIN

[ ACCESS PATIENT PORTAL ]

Forgot PIN?

New to MediKiosk?
Create patient account
```

Keep form simple.

---

# 12. PAGE 04 — PATIENT REGISTRATION

Title:

## Create your patient profile

Use a clean two-column form.

Required fields should be only those supported by the actual backend workflow.

Suggested visible sections:

### Personal

- Full name
- Date of birth / age
- Sex
- Mobile

### Identity

- ABHA ID if available
- Hospital/MRN if available
- Optional identification field according to configured workflow

### Contact

- City
- District
- State

### Preferences

- Preferred language

### Other

- Insurance/payer information if supported

Primary:

`CREATE PATIENT PROFILE`

After success:

Show profile card:

```text
PATIENT ID
MK-XXXX

ABHA STATUS
Linked / Pending

PROFILE CREATED
✓
```

---

# 13. PAGE 05 — PATIENT LANGUAGE

Centered premium selection.

Title:

## Choose your language

Cards:

```text
English
தமிழ்
हिन्दी
తెలుగు
मराठी
```

Optional additional configured languages.

Right side preview:

> This language will be used for your patient experience and voice guidance.

CTA:

`CONTINUE`

---

# 14. PAGE 06 — CONSENT

Three cards:

### What we collect

Symptoms, medical history, documents.

### Why we collect it

To prepare information for your consultation.

### Who can see it

Authorized clinical staff according to workflow.

Actions:

`AGREE & CONTINUE`

`DECLINE`

Secondary:

`Read full privacy policy`

Use a reassuring privacy visual.

---

# 15. PATIENT DASHBOARD

## PAGE 07 — PATIENT DASHBOARD

This should have the same polished dashboard hierarchy as RetinopathyScan.

Header:

```text
Good morning, Ramesh
Your health workspace
```

Hero:

```text
Prepare for your next consultation

Complete your clinical history and
keep your medical documents organized.

[ START NEW HISTORY ]
```

Stats:

```text
ACTIVE CASES
1

MEDICAL DOCUMENTS
8

PAST CONSULTATIONS
4

VERIFIED RECORDS
6
```

Main area:

### Current Visit

Show:

```text
General Medicine
Token: A-261
Status: Waiting
Doctor: Dr. S. Verma
```

CTA:

`VIEW VISIT`

### Quick Actions

```text
Start New History
Upload Document
View Medical Records
Find Doctor
```

### Recent Activity

```text
12 Sep
Clinical history submitted

10 Sep
Prescription added

03 Sep
Doctor review completed
```

---

# 16. PATIENT LEFT NAVIGATION

```text
Dashboard

Clinical History
Documents
Medical Timeline
Current Queue
Doctors & Hospitals

Notifications

My Profile
Settings

Sign Out
```

Optional separate:

`Emergency`

---

# 17. NEW HISTORY FLOW

## PAGE 08 — NEW HISTORY INTRO

Title:

## Let's understand what brings you here

Supporting text:

> You can speak naturally or answer using the screen.

Show:

```text
VOICE
Speak naturally

TOUCH
Tap answers
```

CTA:

`START`

---

# 18. PAGE 09 — VOICE INTERVIEW

Large clinical conversational panel.

```text
MediKiosk AI

What problem are you experiencing?

[ 🎙 START SPEAKING ]
```

Secondary:

`Prefer typing?`

Right panel:

```text
Progress
1 of 12
```

Bottom:

`Pause` `Exit`

---

# 19. PAGE 10 — ACTIVE VOICE

Full-width focus page.

Center:

- circular microphone control
- waveform
- transcript

```text
Listening...

"I'm having chest pain for the last three days..."
```

Actions:

`DONE`

`RECORD AGAIN`

Do not show technical model information.

---

# 20. PAGE 11 — ADAPTIVE FOLLOW-UP

Question card:

```text
When did your chest pain start?
```

Choice cards:

```text
Today
Yesterday
2–3 days ago
More than a week ago
Not sure
```

Voice button:

`Answer by speaking`

Keep one clinical question per view.

---

# 21. PAGE 12 — PATIENT-FACING CONFIRMATION

Title:

## Did we understand you correctly?

Show simple cards:

```text
Main problem
Chest pain

Duration
3 days

Severity
6 / 10

Breathing difficulty
No
```

Actions:

`YES, CONTINUE`

`SAY IT AGAIN`

This is not a medical editing screen.

---

# 22. PAGE 13 — RED-FLAG STATE

When backend reports RED severity, switch to an emergency-focused page.

Title:

# Immediate attention required

Show:

```text
Your responses indicate symptoms
that need prompt clinical attention.

Clinical staff have been alerted.
```

Large CTA:

`GET HELP NOW`

Secondary:

`VIEW TRIAGE LOCATION`

No normal-flow completion button.

---

# 23. PAGE 14 — DOCUMENT CENTER

Title:

## Add medical documents

Cards:

```text
Prescription
Lab Report
Discharge Summary
Imaging
Other
```

Primary:

`UPLOAD DOCUMENT`

Secondary:

`CAPTURE WITH CAMERA`

Show accepted types and size limits only if backend/configuration supplies them.

---

# 24. PAGE 15 — DOCUMENT UPLOAD

Drag/drop desktop panel:

```text
Drop your medical document here

or

[ CHOOSE FILE ]

JPG • PNG • PDF
```

Mobile/browser camera option if supported.

After selection:

File preview.

CTA:

`PROCESS DOCUMENT`

---

# 25. PAGE 16 — OCR PROCESSING

Large progress card:

```text
Reading document

✓ Document received
✓ OCR processing
● Extracting clinical information
○ Organizing timeline
```

Do not invent progress that backend doesn't actually expose; use indeterminate progress when necessary.

---

# 26. PAGE 17 — OCR / DOCUMENT RESULT

Title:

## Medical information detected

Two-column layout.

Left:

Original document preview.

Right:

Extracted data.

Sections:

```text
Medication
Metformin 500 mg

Diagnosis
Type 2 Diabetes

Investigation
HbA1c 8.2%

Date
12 Aug 2026
```

Each fact:

`Evidence`

Click → source document / highlight.

Use labels:

```text
Extracted
Verified
Needs review
```

---

# 27. PAGE 18 — MEDICAL TIMELINE

Timeline design:

```text
2022
Diagnosis

2023
Prescription

2024
Hospital visit

2025
Lab report

2026
Current encounter
```

Use distinct icons.

Filters:

```text
All
Prescriptions
Lab Reports
Hospital Visits
Symptoms
```

---

# 28. PAGE 19 — STRUCTURED SUMMARY REVIEW

Title:

## Review your clinical information

Show:

```text
Chief Complaint
History of Present Illness
Past Medical History
Past Surgical History
Medications
Allergies
Family History
Personal History
Review of Systems
Previous Investigations
```

Patient should see plain-language presentation.

CTA:

`SUBMIT TO CLINICAL TEAM`

---

# 29. PAGE 20 — SUBMISSION SUCCESS

Hero:

✓

## Your clinical intake is complete

Show:

```text
Case ID
MK-2026-00124

Department
General Medicine

Priority
Normal

Status
Submitted for clinical review
```

Primary:

`VIEW CASE`

---

# 30. PATIENT QUEUE PAGE

## PAGE 21 — CURRENT VISIT

Show:

```text
YOUR TOKEN
A-261

General Medicine

Position
2

Status
WAITING

Room
102
```

Only display position/wait data if backend supplies it.

Refresh button:

`REFRESH STATUS`

---

# 31. DOCTOR LOGIN

## PAGE 22 — DOCTOR LOGIN

Professional split screen.

Left:

```text
MediKiosk AI

Clinical Command Center

Patient history
Evidence
Triage
Consultation
```

Right:

```text
MEDICAL PROFESSIONAL

Doctor ID / Email

Security PIN

[ ACCESS PORTAL ]
```

Small text:

`Authorized clinical use`

---

# 32. DOCTOR REGISTRATION / PROFILE

If implemented in backend:

Title:

## Clinical professional profile

Fields:

```text
Full legal name
Registration ID
Specialization
Hospital / Clinic
Phone
City
District
State
Email
```

Status area:

```text
Verification
Pending / Verified
```

---

# 33. DOCTOR DASHBOARD

This is the equivalent of the polished RetinopathyScan dashboard.

Header:

```text
Good morning, Dr. Verma

Clinical Command Center
```

Hero:

```text
Review complete patient histories
before consultation.

[ OPEN PATIENT QUEUE ]
```

Stats:

```text
PATIENTS TODAY        42
PENDING REVIEW         8
PRIORITY CASES         2
COMPLETED             32
```

Main section:

## Patient Queue

Rows/cards:

```text
Patient
Age
Chief Complaint
Priority
Documents
Status
```

Priority:

```text
HIGH
MEDIUM
NORMAL
```

---

# 34. DOCTOR QUEUE PAGE

## PAGE 23 — PATIENT QUEUE

Table:

```text
PATIENT     AGE   COMPLAINT       PRIORITY   CHANNEL   ACTION

Lakshmi     58    Chest pain      HIGH       KIOSK     Review
Arun        42    Fever           NORMAL     IVR       Review
Meena       33    Back pain       NORMAL     KIOSK     Review
```

Filters:

```text
All
Priority
Waiting
In Progress
Reviewed
```

Search:

`Search patient / encounter`

---

# 35. DOCTOR PATIENT DETAIL

## PAGE 24 — CASE OVERVIEW

Top:

```text
PATIENT
Ramesh Kumar

Age 56
Male

ABHA
XXXX XXXX XXXX

Encounter
MK-2026-00124

Priority
HIGH
```

Tabs:

```text
Overview
Clinical History
Documents
Timeline
Evidence
Consultation
```

---

# 36. CLINICAL SUMMARY PAGE

## PAGE 25 — STRUCTURED HISTORY

Main content:

```text
Chief Complaint
...

History of Present Illness
...

Past Medical History
...

Past Surgical History
...

Medications
...

Allergies
...

Family History
...

Personal History
...

Review of Systems
...
```

Right rail:

```text
AI STRUCTURED

Source-backed
Doctor review required
```

Actions:

`EDIT`

`CONFIRM`

`REJECT`

---

# 37. EVIDENCE PAGE

## PAGE 26 — EVIDENCE TRACEABILITY

Split view.

Left:

Clinical fact.

Right:

Original source.

Example:

```text
HbA1c 8.2%

Source:
Document DOC-004
Page 1
Line 12
```

Button:

`VIEW SOURCE`

If backend exposes bounding boxes/highlight paths, render them on the document preview.

The repository architecture explicitly uses source references / line-indexed citation guardrails, so the UI should surface this as a trustworthy evidence workflow rather than hiding it.

---

# 38. DOCUMENT TIMELINE

## PAGE 27

Top:

```text
DOCUMENTS
4
```

Cards:

```text
Prescription
12 Aug 2026
OCR complete

Lab Report
04 Aug 2026
OCR complete

Discharge Summary
13 Jun 2025
OCR complete
```

Click → document viewer.

---

# 39. DOCTOR DOCUMENT VIEWER

Two-column:

```text
ORIGINAL DOCUMENT
       │
       │
       ▼
EXTRACTED CLINICAL DATA
```

Controls:

Zoom
Rotate
Download if permitted

Fact links:

`View Evidence`

---

# 40. TRIAGE PANEL

## PAGE 28 — PRIORITY REVIEW

If priority:

```text
PRIORITY CASE

Red Flag Detected

Chest pain
Breathlessness

Source:
Patient conversation

Action:
Immediate clinical attention
```

Doctor actions:

`ACKNOWLEDGE`

`ESCALATE`

`MARK REVIEWED`

Do not present the rule engine as an autonomous diagnosis.

---

# 41. DOCTOR VERIFICATION

## PAGE 29 — VERIFY CASE

Verification checklist:

```text
✓ Chief complaint
✓ HPI
✓ Past history
✓ Medication
✓ Allergy
✓ Family history
✓ Documents
✓ Timeline
```

Each item:

```text
Verified
Needs edit
Missing
```

Bottom sticky action:

`CONFIRM CLINICAL HISTORY`

---

# 42. CONSULTATION PAGE

## PAGE 30

Three-column professional workspace.

Left:

Patient snapshot.

Center:

Structured clinical history.

Right:

Doctor workspace.

Right sections:

```text
Clinical Assessment
Notes
Plan
Prescription
Follow-up
Referral
```

Bottom:

`SAVE CONSULTATION`

---

# 43. PRESCRIPTION PAGE

## PAGE 31

```text
PRESCRIPTION

Medication
Dose
Frequency
Duration
Instructions
```

Generate/save using the existing backend functionality.

No autonomous prescription generation by frontend.

---

# 44. REFERRAL PAGE

## PAGE 32

Fields:

```text
Referral specialty
Reason
Priority
Notes
```

Button:

`SEND REFERRAL`

---

# 45. FINAL ENCOUNTER PAGE

## PAGE 33

Status:

```text
✓ CONSULTATION COMPLETED
```

Summary:

```text
History verified
Documents reviewed
Clinical notes saved
Prescription saved
```

Then:

`RETURN TO PATIENT QUEUE`

---

# 46. PATIENT POST-REVIEW PAGE

Patient should see:

```text
Your case has been reviewed

Dr. S. Verma
General Medicine
Hospital / Clinic

✓ Clinical history reviewed
✓ Consultation completed
```

Actions:

`VIEW REPORT`

`VIEW PRESCRIPTION`

`VIEW DOCTOR`

The current patient API already returns doctor verification information associated with encounters.

---

# 47. PATIENT MEDICAL RECORDS

## PAGE 34

Dashboard-style record library.

Tabs:

```text
All
Visits
Prescriptions
Documents
Investigations
Referrals
```

Timeline cards.

---

# 48. FIND DOCTORS

## PAGE 35

Professional discovery page.

Header:

```text
Find Clinical Experts
```

Search:

`Search doctor, specialty or hospital`

Filters:

```text
Specialty
Location
Hospital
Availability
```

Doctor cards:

```text
Dr. S. Verma
General Medicine

Hospital
Location

Verified

[ VIEW PROFILE ]
```

Map/list split only when actual location/map data is available.

---

# 49. DOCTOR PROFILE

## PAGE 36

```text
Dr. S. Verma
General Medicine

Verified Professional

Hospital
Location
Consultation information

[ VIEW HOSPITAL ]
```

---

# 50. PROFILE & SETTINGS

Patient:

```text
Profile
Personal information
Language
Privacy
Notifications
Security
Sign Out
```

Doctor:

```text
Professional Profile
Hospital
Specialization
Verification
Security
Notifications
Sign Out
```

---

# 51. NOTIFICATIONS

Patient examples:

```text
Your case was reviewed
Your document was processed
Doctor consultation completed
Queue updated
```

Doctor examples:

```text
Priority case received
New patient history
New document uploaded
Review pending
```

---

# 52. ANALYTICS / OPERATIONS

Doctor/authorized staff dashboard.

Cards:

```text
Total cases
Pending
Reviewed
Priority
Documents processed
```

Charts:

- daily encounters
- priority distribution
- channel usage
- department distribution

Use actual API values only.

---

# 53. IVR BROWSER SIMULATOR PAGE

For web demo only if needed.

Title:

## MediKiosk Voice Call

Show fake phone-style interface:

```text
CALL CONNECTED

Language
English

Listening...

User:
"My father has chest pain."

AI:
"When did it start?"
```

Controls:

```text
1
2
3
4
5
6
7
8
9
*
0
#
```

Display transcript and structured status.

The IVR should ultimately create/update the same backend encounter model as kiosk/web intake.

---

# 54. RESPONSIVE BEHAVIOR

## Desktop

Sidebar + large content.

## Tablet

Collapsible sidebar.

## Mobile browser

Bottom nav / compact header.

## Kiosk

Large touch controls, minimal navigation, high visibility.

The web build should be fully responsive.

---

# 55. PAGE TRANSITION DESIGN

Use subtle:

```text
fade
slide-up
scale-in
skeleton loading
```

Do not use heavy animation in clinical workflows.

For page navigation:

150–250ms.

For major status changes:

250–350ms.

---

# 56. MICRO-INTERACTION DESIGN

Primary button:

- hover elevation
- pressed state
- disabled state
- loading spinner

Cards:

- hover lift
- keyboard focus ring

Voice:

- pulse only during active listening

Red flag:

- no flashing
- strong static alert + subtle entrance animation

---

# 57. ACCESSIBILITY

Mandatory:

- keyboard navigation
- semantic labels
- focus states
- adequate contrast
- readable font sizes
- screen reader labels
- large touch targets
- no information conveyed only by color

Patient interaction must be usable by elderly and low-literacy users.

---

# 58. SECURITY UX

Never display:

- raw backend exceptions
- API keys
- internal tokens
- database identifiers unless intentionally user-facing
- developer diagnostics

Patient-facing identifiers:

- Patient ID
- Encounter ID
- Queue token

Doctor-facing:

- encounter identifiers
- source references
- clinical status

---

# 59. DATA BINDING

The frontend must map directly to the existing backend concepts.

### Patient dashboard

Bind:

```text
patient
profile
active_token
encounters
documents
doctor_verification
facts
ayush_intake
```

### Doctor queue

Bind:

```text
encounter_id
token_number
severity_badge
summary_30_words
channel
fact_count
has_medication_conflict
has_red_flags
created_at
```

### Doctor patient page

Bind:

```text
encounter
clinical_facts
drug_interaction_alerts
lab_result_alerts
clinical_gap_alerts
ayush_intake
medication_timeline
documents
```

---

# 60. FRONTEND ARCHITECTURE

Recommended web structure:

```text
web/
├── src/
│   ├── app/
│   ├── routes/
│   ├── layouts/
│   │   ├── PublicLayout
│   │   ├── PatientLayout
│   │   └── DoctorLayout
│   ├── pages/
│   │   ├── public/
│   │   ├── patient/
│   │   └── doctor/
│   ├── components/
│   ├── features/
│   │   ├── auth/
│   │   ├── patient/
│   │   ├── intake/
│   │   ├── documents/
│   │   ├── queue/
│   │   ├── doctor/
│   │   └── ivr/
│   ├── services/
│   │   └── api/
│   ├── hooks/
│   ├── store/
│   ├── types/
│   └── styles/
└── package.json
```

Use a typed API client.

---

# 61. STATE MODEL

Global state:

```text
auth
currentUser
role
language
patient
encounter
intakeSession
documents
queue
notifications
ui
```

Patient-specific:

```text
patientProfile
activeEncounter
historyProgress
documents
timeline
currentQueue
doctorVerification
```

Doctor-specific:

```text
doctorProfile
queue
selectedEncounter
clinicalFacts
documents
alerts
reviewState
consultation
```

---

# 62. ROUTE GUARDS

Patient routes:

```text
requireAuthenticatedPatient
```

Doctor routes:

```text
requireAuthenticatedDoctor
```

Prevent:

```text
patient → /doctor/*
doctor → /patient/*
```

Redirect unauthenticated users to the correct login page.

---

# 63. API ERROR MAPPING

Convert backend status codes into friendly UI.

```text
401 → Authentication required
403 → You don't have access to this case
404 → Record not found
409 → Current state changed, refresh
422 → Please check submitted information
429 → Please retry shortly
5xx → Service temporarily unavailable
```

Never expose raw `detail` blindly.

---

# 64. API INTEGRATION PRIORITY

Build in this order:

## Phase 1

```text
auth
patient dashboard
doctor auth
doctor queue
doctor patient detail
```

## Phase 2

```text
document upload
document viewer
OCR result
clinical timeline
```

## Phase 3

```text
voice intake
adaptive questions
submission
queue
```

## Phase 4

```text
doctor review
evidence
consultation
prescription
```

## Phase 5

```text
IVR browser simulator
analytics
advanced routing
```

---

# 65. IMPORTANT: DO NOT REBUILD WORKING AI

The repository architecture already contains:

- speech/voice processing
- OCR
- clinical normalization
- doctor queue intelligence
- drug interaction detection
- lab checks
- AYUSH support
- IVR
- evidence/source references

The web layer must make those systems visible through excellent UX instead of replacing them.

---

# 66. FINAL MASTER USER JOURNEY

## Patient

```text
Landing
  ↓
Account Type
  ↓
Patient Login/Register
  ↓
Patient Profile
  ↓
Language
  ↓
Consent
  ↓
Patient Dashboard
  ↓
Start Clinical History
  ↓
Voice / Touch
  ↓
Adaptive Questions
  ↓
Red-Flag Check
  ├── Normal → Continue
  └── Urgent → Priority Triage
  ↓
Documents
  ↓
OCR
  ↓
Extracted Information
  ↓
Medical Timeline
  ↓
Structured Summary
  ↓
Submit
  ↓
Queue / Visit Status
  ↓
Doctor Review
  ↓
Doctor Verification
  ↓
Consultation
  ↓
Prescription / Report
  ↓
Patient Notification
  ↓
Medical Records
```

## Doctor

```text
Doctor Login
  ↓
Dashboard
  ↓
Patient Queue
  ↓
Open Case
  ↓
Overview
  ↓
Clinical History
  ↓
Documents
  ↓
Evidence
  ↓
Red-Flag Review
  ↓
Verify / Edit
  ↓
Consultation
  ↓
Prescription
  ↓
Referral if needed
  ↓
Complete Encounter
```

## IVR

```text
Phone
  ↓
Language
  ↓
Identity
  ↓
Consent
  ↓
Voice Intake
  ↓
Same Encounter Model
  ↓
Same Queue
  ↓
Same Doctor Portal
```

---

# 67. VISUAL QUALITY BAR

The finished MediKiosk website should feel like:

```text
RetinopathyScan quality
        +
Modern healthcare SaaS
        +
Hospital-grade information hierarchy
        +
Accessible patient UX
```

It must NOT feel like:

```text
college-project form
generic chatbot
generic admin dashboard
template healthcare website
```

---

# 68. FINAL ANTIGRAVITY INSTRUCTION

Build the web UI around the EXISTING MediKiosk backend.

First inspect the current repository and current API behavior.

Do not rebuild backend functionality.

Do not modify Flutter.

Do not alter working clinical logic unless absolutely required for API compatibility.

Create a polished responsive **light-theme MediKiosk Web Portal** with:

```text
PUBLIC EXPERIENCE
PATIENT PORTAL
DOCTOR PORTAL
CLINICAL REVIEW
DOCUMENT INTELLIGENCE
VOICE INTAKE
QUEUE
MEDICAL TIMELINE
EVIDENCE
CONSULTATION
PRESCRIPTION
IVR DEMO
```

Use a consistent healthcare design system.

Prioritize:

1. usability
2. accessibility
3. clinical clarity
4. evidence traceability
5. responsive design
6. polished visual hierarchy
7. real API integration
8. safe error handling

Every page must have:

- loading state
- error state
- empty state where relevant
- success state where relevant
- responsive behavior
- keyboard accessibility
- visible interaction feedback

DO NOT create disconnected static mock pages.

Every primary CTA must navigate to a real application state.

The final website must be a connected, navigable, API-backed product.

---

# 69. SUCCESS CRITERIA

The implementation is complete when a demo can perform:

```text
PATIENT
Login
 ↓
Dashboard
 ↓
Start History
 ↓
Voice/Touch
 ↓
Submit
 ↓
Document Upload
 ↓
Timeline
 ↓
Queue

DOCTOR
Login
 ↓
Dashboard
 ↓
Queue
 ↓
Open Same Patient
 ↓
View History
 ↓
View Documents
 ↓
View Evidence
 ↓
Verify
 ↓
Consultation

PATIENT
 ↓
See completed/reviewed record
 ↓
See doctor/report
```

The visual design must be clean enough for an SIH demonstration and practical enough to continue into real implementation.
