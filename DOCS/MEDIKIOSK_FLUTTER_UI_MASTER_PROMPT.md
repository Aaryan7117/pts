# MEDIKIOSK — FLUTTER UI MASTER PROMPT
## Complete Android + iOS patient UI specification and coding prompt

> **Use this file as the UI source of truth.**
> Build the real Flutter UI—not Figma files, screenshots, or static mockups.
> Read the complete document before writing UI code.
> Do not remove required features and do not invent additional product features.

---

# 1. UI IMPLEMENTATION RULES

- Flutter only for the mobile application.
- One codebase for Android + iOS.
- Material 3 foundation with a custom MediKiosk healthcare theme.
- Responsive layout for phone/tablet/large kiosk-style displays.
- Large touch targets.
- High contrast.
- Minimal cognitive load.
- Voice-first interaction.
- No complex clinical terminology editing by patients.
- All screens must work in mock mode.
- All actions must have visible feedback.
- Loading, error, retry and offline states must be designed.
- Use semantic labels for screen readers.
- Respect SafeArea.
- Never hard-code device-specific dimensions without responsive logic.

---

# 2. DESIGN SYSTEM

# 3. VISUAL DESIGN SYSTEM

## 3.1 Design language

Style:

- modern healthcare
- trustworthy
- calm
- professional
- high contrast
- accessible
- minimal clutter
- large touch targets
- subtle motion
- no unnecessary glassmorphism
- no excessive gradients
- no tiny text
- no decorative UI that competes with the task

Use rounded cards with restrained shadows.

## 3.2 Base canvas

Primary target:

```text
1280 × 800 logical design reference
Landscape-friendly kiosk/tablet layout
```

The application must also adapt to:

- Android phones
- Android tablets
- iPhones
- iPads

Use responsive layouts rather than fixed pixel positioning.

## 3.3 Color tokens

```text
mdCanvas        #F8FAFC
mdSurface       #FFFFFF
mdBrandDark     #0F172A
mdBrandPrimary  #1E3A8A
mdBrandTint     #EFF6FF
mdAyushGreen    #065F46
mdTriageRed     #991B1B
mdTextMuted     #475569
mdBorder        #E2E8F0
mdSuccess       #166534
mdWarning       #92400E
```

Use semantic colors consistently:

- Blue = primary action / information
- Green = success / safe completion
- Red = emergency / critical warning
- Grey = secondary/non-primary
- White = surface

Do not use color as the only way to communicate state. Always include:

- icon
- label
- visual state

## 3.4 Typography

Recommended:

```text
H1: 36sp, bold
H2: 28sp, semibold
H3: 24sp, semibold
Body Large: 22sp
Body: 18sp
Button: 22–24sp, semibold
Caption: 16sp minimum where possible
```

For accessibility, allow text scaling.

## 3.5 Touch targets

Minimum target:

```text
64 × 64 logical pixels
```

Prefer:

```text
72–88px
```

for primary kiosk actions.

## 3.6 Icons

Use Material Icons or another consistent icon library.

Preferred semantic icons:

```text
Welcome       medical_services
Language      language
Help          help_outline
Consent       verified_user
ABHA          qr_code_scanner
Mobile        phone
Voice         mic
Stop          stop
Text          keyboard
Processing    auto_awesome / psychology
Confirm       check_circle
Correction    replay / edit_note
Emergency     emergency
Documents     description
Camera        photo_camera
OCR           document_scanner
Vitals        monitor_heart
Hospital      local_hospital
Map           map
Location      location_on
Ambulance     emergency
Queue         confirmation_number
Doctor        medical_information
History       history
Call          call
IVR           dialpad
Settings      settings
Back          arrow_back
```

Use icons with labels; do not rely on icon-only controls for important actions.

---

---

# 3. REUSABLE UI COMPONENTS

Create reusable components before duplicating UI:

```text
MediScaffold
MediHeader
LanguageSelector
HelpButton
PrimaryActionButton
SecondaryActionButton
LargeChoiceCard
VoiceButton
ListeningWave
ProgressIndicator
StepIndicator
SummaryCard
ClinicalFactCard
ConsentCard
DocumentGuideOverlay
CameraCaptureFrame
OCRFieldCard
EvidenceChip
VitalCard
EmergencyBanner
QueueTicketCard
HospitalServiceCard
MapActionCard
LoadingState
OfflineBanner
ErrorState
RetryButton
ConfirmationDialog
PrivacyResetOverlay
```

Component requirements:
- typed parameters
- no business logic
- theme-driven styling
- accessibility semantics
- disabled/loading states
- consistent spacing

---

# 4. GLOBAL HEADER

For patient screens that need it:

```text
LEFT:
MediKiosk logo/medical cross
MediKiosk title

RIGHT:
language selector
help button
```

Do not overload the header.

On emergency screens, the emergency state must visually dominate.

---

# 5. SCREEN-BY-SCREEN UI PROMPTS

## SCREEN 01 — WELCOME

**AI instruction:** Build a calm, premium healthcare welcome screen.

Layout:
- full background canvas
- centered medical cross/brand mark
- large `Welcome to MediKiosk`
- subtitle explaining pre-consultation
- large primary `START` button
- help action
- audio assistance action
- language shortcut

Visual:
- generous whitespace
- rounded card/button geometry
- subtle elevation
- no distracting gradients
- large readable typography

Interactions:
- Start → Language
- Help → help modal
- Audio → localized TTS
- language shortcut → language selector

Accessibility:
- all actions ≥64dp target
- semantic labels
- readable contrast

---

## SCREEN 02 — LANGUAGE SELECTION

Title:
`Choose your language`

Display a large choice grid.

Initial supported choices:
- English
- हिन्दी
- தமிழ்
- తెలుగు
- मराठी
- configured additional languages

Each language:
- large icon/label
- selected border
- selected checkmark

Footer:
`CONTINUE`

Rules:
- Continue disabled until selection.
- Language selection immediately changes future UI/TTS configuration.
- Do not translate clinical meaning locally in a way that bypasses backend policy.

---

## SCREEN 03 — CONSENT

Title:
`Before we begin`

Show three simple privacy statements:
- why symptoms are collected
- why documents may be captured
- who may access the information

Actions:
- `I Agree and Continue`
- `I Do Not Agree`

Advanced privacy policy:
- collapsible
- readable
- scrollable

Do not use dense legal text as the primary visual.

If declined:
- explain what cannot proceed
- offer safe exit/reset

---

## SCREEN 04 — IDENTIFICATION

Title:
`Let's find your hospital record`

Three large cards:

### Card 1
`SCAN ABHA QR CODE`

Camera opens with a clear scanner frame.

### Card 2
`ENTER LINKED MOBILE NUMBER`

Open large numeric keypad.

### Card 3
`NEW REGISTRATION / SKIP ID`

Continue without identity match.

Show progress/loading while identification is processed.

Errors:
- QR unreadable
- network unavailable
- identity service unavailable

Never expose backend errors directly.

---

## SCREEN 05 — CARE STREAM / REASON FOR VISIT

Purpose:
quickly establish why the patient is here.

Use large choice cards with plain language.

Example categories:
- General health problem
- Follow-up
- AYUSH consultation
- Existing prescription/history
- Other

Do not make the patient fill a long form.

Continue only after a selection or explicit skip.

---

## SCREEN 06 — VOICE INTAKE

Title:
`What problem are you experiencing?`

Subtitle:
`Tell us in your own words.`

Center:
- oversized microphone button
- microphone icon
- clear instruction
- optional text input

Below:
- `Tap to talk`
- audio guidance

Secondary:
`I prefer to type`

Behavior:
- microphone permission
- start recording
- transition to active capture
- graceful failure if microphone unavailable

---

## SCREEN 07 — ACTIVE VOICE CAPTURE

Title:
`I'm listening...`

Center:
- animated voice waveform
- microphone/stop control
- elapsed recording indicator

Transcription:
- large readable live transcript
- do not show technical AI terms

Actions:
- `DONE SPEAKING`
- `CANCEL`

If no speech:
- gentle prompt
- retry

If recording interrupted:
- preserve safe state and offer retry.

---

## SCREEN 08 — CONVERSATIONAL FOLLOW-UP

This is a conversational card-based screen.

Show:
- current question
- optional supporting explanation
- voice response button
- type alternative
- progress indicator

Examples of question types:
- duration
- severity
- location
- associated symptoms
- relevant history

Rules:
- one question at a time
- no long questionnaire
- adapt based on backend response
- never display internal model terminology

---

## SCREEN 09 — AI PROCESSING

Title:
`Understanding your response...`

Show:
- calm animated progress indicator
- short human-readable status

Example:
`Organizing your symptom details...`

Do NOT show:
- LLM
- tokens
- embeddings
- inference
- model names
- confidence scores intended for developers

If processing fails:
- retry
- continue manually where safe
- never pretend processing succeeded

---

## SCREEN 10 — SIMPLE SUMMARY CONFIRMATION

Title:
`Is this information correct?`

Show only patient-friendly facts.

Example:
```text
Main problem
Headache

How long
3 days

Pain
6 out of 10
```

Actions:
- `YES, THIS IS CORRECT`
- `NO, SAY IT AGAIN`

Important:
**Do not create a clinical editor.**
The patient should not manually edit complex structured terminology.

If correction:
- return to voice interaction
- allow patient to speak the correction

---

## SCREEN 11 — RED FLAG / TRIAGE

This screen must be visually distinct.

Use:
- strong warning hierarchy
- emergency icon
- clear red warning area
- very large text
- simple instructions

Message example:
`Your symptoms need immediate attention.`

Explain:
- clinical desk has been alerted
- where to go
- what to do next

Action:
`GET IMMEDIATE HELP`

If the configured flow requires ticket printing, show it as a secondary action.

Do not show technical risk scores.

Do not allow normal queue continuation when the backend marks the case as an emergency stop.

---

## SCREEN 12 — DOCUMENT INTRO

Title:
`Scan your medical documents`

Explain:
- place prescription/test paper in the scan area
- keep it flat
- good lighting

Actions:
- `START SCANNING`
- `SKIP`

Use a simple document illustration/icon.

---

## SCREEN 13 — DOCUMENT CAMERA

Camera screen requirements:
- 4:3 document preview area
- clear rectangular guide
- corner markers
- document detection state
- capture button
- retake
- skip

Status examples:
`ALIGN DOCUMENT`
`HOLD STEADY`
`DOCUMENT CAPTURED`

Do not show raw OCR/debug information.

Camera permission failure:
- explain why camera is needed
- provide retry
- provide skip where policy allows

---

## SCREEN 14 — OCR PROCESSING

Title:
`Reading your document...`

Show:
- document thumbnail
- progress indicator
- processing status

Example:
`Extracting medicines and test results...`

If upload fails:
- retry
- recapture
- skip

Do not display fake extracted information.

---

## SCREEN 15 — OCR RESULT / EVIDENCE

Title:
`Medical history found`

Show extracted information as readable cards:

```text
Medicine
Metformin 500 mg

Date
August 2026

Lab result
HbA1c 8.4%
```

Every extracted item should have:
- evidence indicator
- source reference action where available
- confidence only where clinically appropriate and clearly labelled

Patient should not be forced to manually correct the medical values.

Action:
`CONTINUE`

Doctor dashboard receives the structured data and evidence.

---

## SCREEN 16 — SOURCE DOCUMENT VIEW

Display:
- captured document
- zoom/pan
- highlighted evidence region where backend provides coordinates
- extracted fact reference

Controls:
- zoom in
- zoom out
- reset
- close

Keep the viewer simple and accessible.

---

## SCREEN 17 — VITALS

Title:
`Let's record your basic measurements`

Use large cards:

- blood pressure
- pulse
- temperature
- SpO₂
- weight/height when configured

Each card shows:
- measurement
- unit
- source/status

If hardware is unavailable:
- clearly indicate unavailable
- allow configured manual/skip flow

Do not make the patient interpret medical thresholds.

---

## SCREEN 18 — AYUSH PROFILE

Only show when the selected care stream requires it.

Title:
`Your daily habits`

Use simple cards/segmented choices for configured variables such as:
- diet style (Ahara)
- digestion (Agni)
- bowel pattern (Koshtha)

Keep terminology paired with plain-language explanation.

Example:
`Digestion (Agni)`
`Weak`
`Fast`
`Variable`

No dense questionnaire.

---

## SCREEN 19 — DEPARTMENT ROUTING / QUEUE

Title:
`Your visit is ready`

Show:
- recommended department
- token/queue number
- estimated wait only if backend provides it
- current queue status

Example:
```text
General Medicine
Token A-402
```

Actions:
- view queue
- view hospital services
- continue

Do not invent live queue information.

---

## SCREEN 20 — HOSPITAL SERVICES

Create a service grid:

- OPD departments
- pharmacy
- laboratory
- billing/counters where configured
- help desk
- toilets
- emergency
- other configured hospital services

Each card:
- recognizable icon
- large title
- short description
- optional location/directions action

---

## SCREEN 21 — HOSPITAL MAP

Map UI should contain:
- current location when permission/provider supports it
- hospital location
- selected service
- route/directions action
- zoom controls
- accessible list alternative

If map service is unavailable:
- show text-based directions or service list if available
- never display a broken blank map without explanation

---

## SCREEN 22 — EMERGENCY

This is also accessible independently from configured app entry points.

Show:
- large emergency/SOS action
- clear warning before dispatch where required
- hospital/ambulance options according to backend policy

Flow:
```text
SOS
 ↓
confirmation
 ↓
location permission
 ↓
emergency request
 ↓
status
```

Never fake dispatch success.

---

## SCREEN 23 — AMBULANCE STATUS

Show:
- request state
- assigned provider/status when available
- destination hospital
- ETA only when returned by real provider/backend
- emergency contact/help action

Possible states:
- requesting
- confirmed
- assigned
- en route
- arrived
- failed/cancelled

Mock mode must visibly indicate simulated status.

---

## SCREEN 24 — COMPLETION / RESET

Title:
`Intake completed successfully`

Show:
- token
- department
- queue information
- confirmation that information was sent to authorized clinical staff

Privacy:
`This screen will reset automatically.`

Countdown:
- visible
- cancellable only if safe
- reset clears sensitive session state

After reset:
- return to Welcome

No patient information should remain visible after reset.

---

# 6. GLOBAL ERROR STATES

Every relevant screen must have:

### Loading
- skeleton/progress
- no frozen UI

### Network error
- simple explanation
- retry
- offline alternative where supported

### Permission denied
- explain the permission
- retry/open settings where appropriate
- skip if safe

### Server error
- human-readable message
- retry
- preserve local draft

### Session timeout
- clear sensitive data
- explain session ended
- return to welcome

---

# 7. ANIMATION RULES

Use subtle animation only.

Allowed:
- fade
- scale
- slide
- microphone pulse
- waveform
- progress
- card selection
- map transitions

Avoid:
- excessive bouncing
- decorative particle effects
- long animations
- animations that delay critical actions

Respect reduced-motion/accessibility settings where supported.

---

# 8. ICON POLICY

Use one consistent icon family.

Preferred:
- Material Icons / Material Symbols
- custom MediKiosk logo where needed

Core icons:
```text
mic
stop
volume_up
language
help
check
close
arrow_forward
arrow_back
camera_alt
document_scanner
description
visibility
zoom_in
zoom_out
favorite/health
warning
emergency
location_on
map
directions
local_hospital
medication
monitor_heart
thermostat
water_drop
queue
person
lock
privacy_tip
refresh
wifi_off
```

Do not mix random icon packs.

Icons must have semantic labels when they are interactive.

---

# 9. RESPONSIVE RULES

The same UI must adapt to:
- Android phone
- Android tablet
- iPhone
- iPad
- large kiosk-style landscape display

Use:
- LayoutBuilder
- MediaQuery
- responsive constraints
- max content width
- flexible grids

Do not simply scale every element proportionally.

For large displays:
- increase whitespace
- maintain readable content width
- preserve large touch targets

For phones:
- use vertical layouts
- avoid horizontal overflow
- maintain one primary action per step

---

# 10. FLUTTER IMPLEMENTATION STRUCTURE

Recommended:

```text
lib/
  app/
    app.dart
    router.dart
    theme/
    localization/

  core/
    errors/
    network/
    permissions/
    storage/
    widgets/
    utils/

  features/
    onboarding/
    consent/
    identity/
    intake/
    voice/
    triage/
    documents/
    vitals/
    ayush/
    queue/
    services/
    map/
    emergency/
    completion/

  data/
    models/
    repositories/
    datasources/

  services/
    audio/
    camera/
    location/
    notifications/
    secure_storage/
```

Use feature-based organization rather than one giant screen folder.

---

# 11. STATE MANAGEMENT

Use the project's agreed state-management solution consistently.

If starting fresh, use Riverpod.

UI must react to states such as:

```text
initial
loading
ready
recording
processing
success
error
offline
permissionDenied
completed
```

Do not store critical business state only inside individual widgets.

---

# 12. NAVIGATION

Use a centralized router such as `go_router`.

The route graph must reflect the exact product flow:

```text
/welcome
/language
/consent
/identity
/care-stream
/intake
/intake/listening
/intake/follow-up
/intake/processing
/intake/summary
/triage
/documents
/documents/camera
/documents/processing
/documents/results
/documents/evidence
/vitals
/ayush
/queue
/services
/map
/emergency
/emergency/ambulance
/completed
```

Routes may be guarded by session state.

Back navigation must never accidentally skip required consent, triage, or safety states.

---

# 13. MOCK MODE

The UI must be fully demonstrable without backend access.

Mock mode must simulate:
- speech transcript
- follow-up questions
- extracted facts
- triage normal/red-flag cases
- OCR results
- evidence references
- vitals
- department routing
- queue token
- hospital services
- emergency status

Clearly label simulated live data where the user could otherwise mistake it for real information.

---

# 14. API BOUNDARY

Flutter calls repositories such as:

```dart
SessionRepository
IdentityRepository
IntakeRepository
SpeechRepository
ClinicalRepository
TriageRepository
DocumentRepository
VitalsRepository
QueueRepository
HospitalRepository
EmergencyRepository
```

Widgets call controllers/providers, not raw HTTP.

Example:

```text
Screen
 ↓
Controller / Provider
 ↓
Repository interface
 ↓
Mock OR API datasource
```

This lets the UI be completed before backend integration.

---

# 15. SECURITY UI REQUIREMENTS

- Never display API keys.
- Never display internal logs.
- Avoid exposing sensitive patient information on public screens.
- Auto-reset the session.
- Mask sensitive identifiers where appropriate.
- Do not retain captured documents longer than the configured policy.
- Clear temporary UI state on reset.
- Do not put patient data into analytics/debug logs.

---

# 16. ACCESSIBILITY

Required:
- large text
- high contrast
- large buttons
- semantic labels
- clear focus order
- voice/audio assistance
- no color-only status communication
- simple language
- readable error messages
- enough spacing between actions

Target:
- elderly users
- low-literacy users
- users unfamiliar with smartphones

---

# 17. QUALITY BAR

The UI is NOT complete if:
- it looks like default Flutter
- buttons do nothing
- navigation is hard-coded chaotically
- screens have inconsistent spacing
- there are placeholder boxes
- there are fake medical results
- there is no error state
- there is no offline state
- patient must edit complex clinical terminology
- Android works but iOS layout breaks
- text overflows
- touch targets are too small

---

# 18. EXECUTION PROMPT — GIVE THIS TO THE FLUTTER CODING AI

```text
You are the senior Flutter engineer responsible for implementing MediKiosk.

Read BOTH:
1. MEDIKIOSK_DEVELOPMENT_FLOW_MASTER.md
2. MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md

Read them completely before modifying the repository.

First inspect the existing Flutter project and report:
- Flutter/Dart version if detectable
- current folder structure
- existing dependencies
- existing routes/screens
- existing code that can be reused
- conflicts with this specification

Then implement the application in phases.

PHASE 1:
Create/verify architecture, theme, localization, routing, reusable components, state management, repository interfaces and mock mode.

PHASE 2:
Implement every patient screen from Screen 01 through Screen 24 exactly according to this UI specification.

PHASE 3:
Connect every button and transition using the state machine. No dead buttons.

PHASE 4:
Add loading, error, offline and permission states.

PHASE 5:
Verify the entire mock patient journey.

PHASE 6:
Prepare repository/API boundaries for backend integration without putting secrets in Flutter.

Rules:
- Do not remove required MediKiosk features.
- Do not invent unrelated features.
- Do not change the clinical/product logic.
- Do not create a clinical editor for patients.
- Keep complex reconciliation on the doctor side.
- Do not put AI API keys in the mobile application.
- Do not fake real backend success.
- Mock services must be isolated and clearly identifiable.
- Use reusable components.
- Keep business logic outside widgets.
- Make Android and iOS layouts responsive.
- Fix analyzer/compiler errors before proceeding.
- Run tests after each meaningful phase.
- Do not stop after creating the first few screens.
- Continue until the complete specified UI flow is implemented.

At the end, provide:
1. files created/changed
2. dependencies added
3. routes implemented
4. screens completed
5. mock flows tested
6. analyzer/test results
7. remaining backend integrations
8. exact command to run the app

Start by inspecting the repository. Do not generate code blindly.
```

---

# 19. FINAL UI ACCEPTANCE CHECKLIST

```text
[ ] Screen 01 Welcome
[ ] Screen 02 Language
[ ] Screen 03 Consent
[ ] Screen 04 Identification
[ ] Screen 05 Care Stream
[ ] Screen 06 Voice Intake
[ ] Screen 07 Active Listening
[ ] Screen 08 Follow-up
[ ] Screen 09 AI Processing
[ ] Screen 10 Summary
[ ] Screen 11 Triage
[ ] Screen 12 Document Intro
[ ] Screen 13 Camera
[ ] Screen 14 OCR Processing
[ ] Screen 15 OCR Results
[ ] Screen 16 Evidence Viewer
[ ] Screen 17 Vitals
[ ] Screen 18 AYUSH
[ ] Screen 19 Queue
[ ] Screen 20 Services
[ ] Screen 21 Map
[ ] Screen 22 Emergency
[ ] Screen 23 Ambulance
[ ] Screen 24 Completion/Reset

[ ] Android responsive
[ ] iOS responsive
[ ] Accessibility
[ ] Localization
[ ] Mock mode
[ ] Offline state
[ ] Error states
[ ] Permission states
[ ] Session reset
[ ] No dead buttons
[ ] No clinical data editing burden on patient
[ ] No secrets in Flutter
```

---

# 20. REFERENCE SCREEN DEFINITIONS

The following detailed source definitions are retained below so that the coding AI can cross-check each screen instead of inventing its own interpretation.

# SCREEN 01 — WELCOME

## Purpose

Create immediate understanding.

## Layout

Top:

```text
MediKiosk
Hospital / Clinic name
Help icon
Language shortcut
```

Center:

```text
Medical cross / healthcare illustration
Welcome to MediKiosk

Let's gather your health details before you see your doctor.
```

Primary:

```text
START
```

Secondary:

```text
Need Help?
```

Audio:

```text
🔊 Listen to instructions
```

## Behavior

START → language screen.

Help → accessible help modal.

Audio → TTS localized welcome message.

## Design

- large central visual
- one dominant CTA
- generous whitespace
- subtle entrance animation
- no dense text

---
# SCREEN 02 — LANGUAGE SELECTION

## Purpose

Select interaction language before speech services are activated.

## Options

Initial supported UI:

```text
English
हिन्दी
தமிழ்
తెలుగు
मराठी
```

Architecture must allow more languages later.

## Layout

Large cards:

```text
English
हिन्दी
தமிழ்

తెలుగు
मराठी
```

Each selected card gets:

- blue border
- light blue background
- check icon

Primary:

```text
CONTINUE →
```

## Behavior

Selecting language updates:

- UI localization
- TTS language
- speech recognition configuration
- backend language metadata

---
# SCREEN 03 — CONSENT

## Purpose

Obtain understandable consent.

Show:

```text
Before we begin

We collect your health information to help the healthcare team
prepare for your consultation.

Your uploaded documents are handled securely.

Only authorized healthcare personnel should access the
clinical information.
```

Buttons:

```text
✓ I Agree and Continue
I Do Not Agree
```

Expandable:

```text
View detailed privacy information
```

## Important

Do not claim a specific legal compliance state merely because a consent screen exists.

Actual DPDP/ABDM compliance requires backend, policy, security, retention, access-control, and institutional implementation.

---
# SCREEN 04 — IDENTIFICATION

## Purpose

Identify the patient where possible.

Cards:

```text
SCAN ABHA QR
ENTER MOBILE NUMBER
NEW REGISTRATION / SKIP
```

QR path:

```text
Permission
↓
Camera
↓
QR detection
↓
Validate
↓
Backend lookup
↓
Success / Retry
```

Mobile path:

```text
Mobile number
↓
Validation
↓
OTP if backend requires it
↓
Verification
```

Skip path:

```text
Anonymous/session-based intake
```

Never expose sensitive patient information on a shared screen unnecessarily.

---
# SCREEN 05 — CARE STREAM / REASON FOR VISIT

Show large choices only if the project workflow requires routing.

Examples:

```text
General Consultation
Ayurveda / AYUSH
Follow-up
Document Review
Emergency Help
```

Do not make this screen medically diagnostic.

It is routing/intention selection.

---
# SCREEN 06 — VOICE INTAKE

## Purpose

Allow natural speech.

Heading:

```text
What problem are you experiencing?
```

Subheading:

```text
Tell us in your own words.
```

Central:

```text
        ◯
      🎙️
   TAP TO TALK
```

Secondary:

```text
⌨ Type instead
```

Audio help:

```text
🔊 Hear the question
```

## Interaction

Tap mic:

```text
permission → recording → waveform
```

Do not continuously record without explicit interaction/appropriate consent.

---
# SCREEN 07 — ACTIVE VOICE CAPTURE

Show:

```text
I'm listening...
```

Waveform animation.

Live transcript can be shown if appropriate.

Buttons:

```text
DONE SPEAKING
CANCEL
```

State indicators:

```text
Listening
Processing audio
No speech detected
Microphone unavailable
```

## Accessibility

If microphone permission is denied:

```text
We cannot access the microphone.
You can type your answer instead.
```

---
# SCREEN 08 — CONVERSATIONAL FOLLOW-UP

Instead of displaying a long questionnaire, show one question at a time.

Example:

```text
Where is the pain?
```

Answer modes:

```text
🎙 Speak
Tap an option
⌨ Type
```

Possible structured questions:

```text
Duration
Location
Severity
Onset
Associated symptoms
Relevant history
Medication
Allergy
```

Questions must be generated/selected by the backend clinical workflow, not hardcoded as an AI diagnosis.

---
# SCREEN 09 — AI PROCESSING

Show only user-understandable language.

```text
Understanding your response...

Organizing your information for the healthcare team.
```

Do NOT show:

```text
LLM
tokens
embeddings
inference
temperature
vector search
```

Use a clean loading animation.

---
# SCREEN 10 — SIMPLE SUMMARY CONFIRMATION

This is intentionally simplified.

Show:

```text
Here is what I understood

Main problem:
Headache

Started:
3 days ago

Pain:
6 / 10
```

Buttons:

```text
✓ YES, THAT'S RIGHT
↻ SAY IT AGAIN
```

Optional:

```text
Hear summary
```

Do not force the patient to manually edit clinical terminology.

---
# SCREEN 11 — RED FLAG / TRIAGE

Only show when the backend triage engine returns a high-risk state.

Use a strong red warning hierarchy.

```text
⚠ PLEASE GET HELP NOW

Your answers may need urgent medical attention.

Please go to the designated clinical desk.

Your information has been sent to the appropriate
hospital workflow, if the backend connection is available.
```

Actions:

```text
GET HELP
CALL EMERGENCY
PRINT / SHOW PRIORITY TOKEN
```

Do not diagnose.

Use language such as:

```text
may require urgent evaluation
```

rather than:

```text
you definitely have X
```

---
# SCREEN 12 — DOCUMENT INTRO

```text
Do you have old medical documents?

You can scan prescriptions, reports, or test records.
```

Buttons:

```text
SCAN DOCUMENTS
SKIP
```

---
# SCREEN 13 — DOCUMENT CAMERA

Camera view:

```text
┌─────────────────────────┐
│                         │
│   DOCUMENT GUIDE BOX    │
│                         │
└─────────────────────────┘
```

Status:

```text
Move document inside the frame
Hold steady
Document captured
```

Actions:

```text
CAPTURE
RETAKE
DONE
```

Do not store images indefinitely on-device.

---
# SCREEN 14 — OCR PROCESSING

```text
Reading your document...

Extracting information from the scanned record.
```

Display:

```text
Scanning
Reading
Structuring
Saving evidence
```

Do not claim 100% OCR accuracy.

---
# SCREEN 15 — OCR RESULT / EVIDENCE

Show extracted information in a readable way:

```text
Previous medical record

Medication
Metformin 500 mg

Lab result
HbA1c — 8.4%

Date
Aug 2026
```

Each extracted fact should have:

```text
Evidence available
```

Tap fact:

```text
Open source image
```

This is critical for clinical trust.

---
# SCREEN 16 — SOURCE DOCUMENT VIEW

Split view where screen size allows:

```text
Original document
        +
Extracted fact
```

Example:

```text
HbA1c: 8.4%

Source:
Page 1
Region: detected document area
```

The doctor dashboard must also have access to the source evidence.

---
# SCREEN 17 — VITALS

Only show this module when the required device/sensor is available.

Possible:

```text
Blood pressure
Heart rate
SpO2
Temperature
Weight
Height
```

Each reading:

```text
value
unit
timestamp
source/device
confidence/status
```

Do not invent measurements.

If hardware is not connected:

```text
Vitals device unavailable
Continue without vitals
```

---
# SCREEN 18 — AYUSH PROFILE

If the AYUSH workflow is selected, present only simple patient-friendly questions.

Examples:

```text
Diet pattern
Digestion
Bowel pattern
Sleep
Daily routine
```

Do not force users to understand technical Sanskrit terminology.

If the backend derives concepts such as:

```text
Ahara
Agni
Koshtha
Prakriti
Vikriti
```

those can be displayed to clinicians, but the patient-facing UI should use understandable language.

---
# SCREEN 19 — QUEUE / DEPARTMENT ROUTING

Show:

```text
Your intake is complete.

Department:
General Medicine OPD

Token:
A-402

Estimated waiting:
~15 min
```

Buttons:

```text
VIEW QUEUE
HOSPITAL SERVICES
DONE
```

Queue estimates must come from backend data when available.

Do not hardcode real-time estimates in production.

---
# SCREEN 20 — HOSPITAL SERVICES

Cards:

```text
OPD
Pharmacy
Laboratory
Billing
Emergency
Help Desk
Washrooms
Departments
```

Each card can open relevant information.

---
# SCREEN 21 — HOSPITAL MAP

Show:

```text
Current location
Department
Route
```

Actions:

```text
START DIRECTIONS
CALL HELP DESK
BACK
```

Location permission must be requested only when required.

If location is unavailable:

```text
Location unavailable
Choose your destination manually.
```

---
# SCREEN 22 — EMERGENCY

Large, extremely clear layout.

```text
🚨 EMERGENCY HELP
```

Actions:

```text
CALL EMERGENCY SERVICE
CALL HOSPITAL
REQUEST AMBULANCE
```

Require confirmation for accidental calls where appropriate.

Do not pretend that ambulance dispatch is integrated unless a real backend/service exists.

---
# SCREEN 23 — AMBULANCE STATUS

If a real dispatch integration exists:

```text
Ambulance requested

Pickup location
Destination hospital

Status:
Dispatched

ETA:
xx min
```

Without integration, show a clearly labeled prototype state rather than fake live tracking.

---
# SCREEN 24 — COMPLETION / RESET

```text
Your intake is complete.

Your information has been prepared for the healthcare team.
```

Token:

```text
A-402
```

Privacy:

```text
This screen will reset automatically.
```

Reset:

```text
10 seconds
```

Clear:

- patient details
- temporary images
- temporary transcripts
- sensitive state

unless explicitly required for a pending backend operation.

---

---

# 21. FINAL COMMAND

**Implement the UI now, but follow the development-flow document for the overall execution order. Build the complete patient application, not a partial demo. Preserve every required feature and interaction described above.**
