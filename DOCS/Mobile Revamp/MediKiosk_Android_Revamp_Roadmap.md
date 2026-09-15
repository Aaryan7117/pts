# MediKiosk — Android (Flutter BYOD) Revamp Roadmap

**Problem Statement:** SIH26047 — AI-Powered Patient Case-Taking Software
**Beneficiary:** All India Institute of Ayurveda, Ministry of AYUSH
**Channel:** Channel 2 — Mobile BYOD
**Supersedes:** `MediKiosk_Android_Two_Developer_Execution_Plan.md` (v3) — contract sections are stale, see §1
**Governing documents:** `MediKiosk_Master_Context.md`, `MEDIKIOSK_WEB_DESIGN_SPEC.md`, `MediKiosk_Master_Implementation_Context_and_Gap_Analysis.md`

---

## 0. The Three Rules This Roadmap Enforces

Everything below follows from three non-negotiables taken from the master context.

**Rule A — Android is an access channel, not a second backend.**
> *"Do not build separate backends for kiosk, Android and IVR."* (Master Context §44.14)
> *"All channels must converge on the same ClinicalFact model."* (§44.13)

The app renders and collects. It never computes clinical meaning. No client-side severity scoring, no client-side negation handling, no client-side drug interaction logic, no client-side translation of clinical text.

**Rule B — No mock data anywhere in the shipped path.**
If the backend is unreachable, the app shows an honest error or a queued-draft state. It never falls back to sample content. §7 makes this mechanically enforceable.

**Rule C — Mobile BYOD is not the offline-AI channel.**
> *"Basic phone != offline AI."* (Master Context §15)

A patient's phone has no Qwen 7B and no IndicConformer. For Android, "offline" means: cache the draft locally, sync when connectivity returns. The kiosk is the offline-AI story. Conflating the two in the pitch is a credibility risk — a judge will ask what model runs on the handset.

---

## 1. Contract Reconciliation — The Most Important Section

The v3 two-developer plan and the shipped FastAPI backend disagree on nearly every field. Building against v3 guarantees a failed integration.

### 1.1 Field-level drift

| Endpoint | v3 plan says | Verified backend | Impact |
|---|---|---|---|
| `POST /api/encounters/bootstrap` | req `{qr_token, device_channel}` | req `{patient_id, language, channel}` | App has no `patient_id` at QR scan time — needs identity resolved first, or a backend change (B4) |
| `POST /api/encounters/bootstrap` | resp includes `supported_languages[]` | resp `{encounter_id, token_number}` only | App would hardcode the 5-language list. Needs B4. |
| `POST /api/call/session/start` | `opening_text`, `opening_audio_base64` | `welcome_text`, `audio_url` | Audio is a **URL, not base64**. Different player implementation, and better — stream instead of holding in memory. |
| `POST /api/call/audio-turn` | `patient_transcript`, `extracted_facts`, `next_question_text`, `next_question_audio_base64`, `turn_index`, `is_completed` | `transcript`, `assistant_reply`, `facts_extracted`, `next_question`, `is_complete` | Every DTO field name differs. **No audio for the next question** — see B3. |
| `POST /api/call/session/end` | documented | **does not exist** | Use `POST /api/encounters/{id}/complete` |
| `POST /api/documents/upload` | form field `document` | form fields `file`, `encounter_id`, `document_type` | Wrong multipart field name = 422 |
| `POST /api/documents/upload` | resp `extracted_medications`, `flagged_interactions`, `highlighted_image_url` | resp `{document_id, ocr_results:[{text, confidence, line_number, bounding_box}]}` | The rich clinical extraction exists on the **doctor** endpoint, not the upload response. See B2. |
| `GET /api/queue/status/{token}` | `patients_ahead`, `doctor_room` | `position`, `doctor_name`, `cabin` | Renames only, but silent nulls if unfixed |
| `POST /api/ivr/voice-webhook` | assigned to Android team | real: `/api/ivr/exotel/incoming-call`, `/exotel/speech-turn`, `/exotel/end-call` | **IVR is server-to-server. It is not Android work.** Remove from mobile scope entirely. |

### 1.2 The rule that prevents this recurring

> **DTOs are generated from `http://<edge-ip>:8000/openapi.json`. They are never hand-typed from a markdown document — including this one.**

Use `openapi-generator` or `swagger_parser` into `lib/data/generated/`. Regenerate whenever the backend changes. Any hand-written model class in `lib/data/models/` that duplicates a generated one gets deleted.

This single discipline is what "no mock data" means at the contract layer: the app's idea of the backend is derived from the backend, not from a doc that drifted.

---

## 2. Backend Modifications Required

Seven changes. Six are small. None is a redesign. Ordered by whether Android is blocked without them.

| ID | Change | Why | Blocking? | Size |
|---|---|---|---|---|
| **B1** | Encounter-scoped bearer token issued at `bootstrap`, required on all encounter-scoped reads | Right now any device can read any `encounter_id`. On hospital LAN that's tolerable; on the open internet it is a DPDP problem and a judge-visible flaw. Minimal version: short-lived opaque token bound to `encounter_id`, 30 min TTL. **Not** full OAuth. | **Yes** | S |
| **B2** | Return clinical extraction on document upload — `extracted_medications[]`, `flagged_interactions[]`, `evidence_image_url` | The data already exists (doctor cockpit renders it). Without it the patient sees raw OCR lines and can't verify. PS §Module B requires patient-visible extraction. | **Yes** | S — expose existing |
| **B3** | Add `next_question_audio_url` to `/api/call/audio-turn` response | Otherwise every conversational turn needs a second round trip to synthesize audio. On 4G that's ~600ms added per turn and the call UI stutters. | **Yes** | S |
| **B4** | `bootstrap` accepts `channel: "mobile_byod"`, accepts `qr_token` as an alternative to `patient_id`, and returns `supported_languages[]` | Stops the app hardcoding the language list; lets QR-first onboarding work without pre-resolved identity. | **Yes** | M |
| **B5** | Accept `Idempotency-Key` header on `bootstrap`, `audio-turn`, `documents/upload` | WorkManager retries on flaky cellular **will** create duplicate encounters and duplicate documents without this. Store key → response for 24h. | **Yes** (for offline) | S |
| **B6** | `GET /api/encounters/{id}` returning full current state | App gets killed by Android memory pressure mid-intake. Without rehydration the patient starts over — unacceptable for an elderly user 8 turns in. | Yes | S |
| **B7** | Persist a consent record: `POST /api/encounters/{id}/consent` with `{granted_at, language, consent_version, channel}` | DPDP evidence. Currently consent is a UI screen with no server-side artifact. This is a compliance claim the team is already making. | No — but cheap and defensible | S |

**Explicitly not requested:** JWT/OAuth2 SSO, SQLCipher, ABDM live gateway, FHIR export. All are P0–P2 in the gap analysis but none blocks the Android revamp. Keep them out of this workstream.

---

## 3. Disposition of the Existing `mobile/` App

Sixteen feature packages exist. Four should be deleted. This is the de-scope that makes the rest achievable.

| Package | Verdict | Reasoning |
|---|---|---|
| `welcome` | **Rewrite (a11y)** | Keep the screen, rebuild for TalkBack + text scaling |
| `language` | **Rewrite** | Must be driven by server `supported_languages` (B4) and wired to real Flutter i18n, not a hardcoded list |
| `consent` | **Rewrite** | Must produce a server-side consent artifact (B7), audio-explained, not a checkbox |
| `identity` | **Rewrite** | Mobile OTP / ABHA / guest against real endpoints; no local-only identity |
| `care_stream` | **Keep, thin** | Routes to Kayachikitsa / Panchakarma / General / Emergency. Low risk. |
| `intake` | **Merge into `call_intake`** | PS requires dual-mode (speak **or** tap). One feature, two input modes — not two features. |
| `call_intake` | **Rewrite — this is the core** | Rebuild against real contract. Everything else is secondary. |
| `documents` | **Rewrite** | Real multipart fields, render real bounding boxes over the real image |
| `vitals` | **Demote to optional** | Keep manual entry only if the backend persists it. If it doesn't, cut the screen — a form that writes nowhere is mock data with extra steps. |
| `ayush` | **Keep + strengthen** | Dashavidha Pariksha is the AIIA-facing differentiator. Must POST real structured fields. |
| `triage` | **Display only** | Server owns severity. App renders the badge it is given. Delete any client-side scoring. |
| `emergency` | **Rewrite** | Red-flag detection is a server call, not a local keyword list. Local matching will disagree with the doctor queue. |
| `queue` | **Rewrite** | Real field names (`position`, `cabin`, `doctor_name`) |
| `services` | **DELETE** | Scope bloat. Not in the PS. |
| `map` | **DELETE** | Indoor wayfinding is a demo trap — it will look fake because it is. Replace with a large text card: *"Room 102 · Kayachikitsa · Ground Floor"*. |
| `completion` | **Keep** | Terminal state + token handoff |
| *(BLE sensors)* | **Stays cut** | Gap analysis already marks this P3/MOCKED. Do not revive it. |

**Net effect:** 16 packages → 11. Two fewer screens to localize into 5 languages, two fewer to make screen-reader accessible.

---

## 4. Target Architecture

```
lib/
├── core/
│   ├── config/          app_config.dart — API_BASE_URL via --dart-define, NO default
│   ├── network/         dio client, IdempotencyInterceptor, AuthInterceptor (B1), error mapper
│   ├── audio/           recorder (16kHz mono PCM), url player, playback queue
│   ├── a11y/            semantics helpers, focus utilities, live-region announcer
│   └── design/          tokens ported from MEDIKIOSK_WEB_DESIGN_SPEC (3-layer)
├── l10n/
│   ├── app_en.arb  app_hi.arb  app_ta.arb  app_te.arb  app_mr.arb
│   └── (generated)
├── data/
│   ├── generated/       ← from openapi.json. Do not edit by hand.
│   ├── local/           drift: encounter drafts, pending sync queue
│   └── repositories/    the ONLY place generated DTOs are touched
└── features/            11 packages, each: presentation/ + state/
```

**State management:** keep whatever is already there (BLoC or provider — gap analysis says both appear). Do not migrate state libraries as part of this revamp. That is the definition of over-engineering here.

**One repository rule:** generated DTOs never escape `lib/data/`. Features consume domain models. This is what lets B1–B7 land without touching 11 feature packages.

---

## 5. Phase Plan

Each phase ends at a **CHECKPOINT**. Do not start the next phase until the checkpoint is demonstrated on a real device against the real backend. One ticket in flight at a time.

---

### PHASE 0 — Contract Truth (no app code)

| Ticket | Work | Done when |
|---|---|---|
| **A-000** | Start backend, pull `openapi.json`, diff every endpoint against §1.1 of this doc. Produce `ANDROID_CONTRACT_VERIFIED.md` with actual request/response shapes. | The file exists and every row in §1.1 is marked confirmed or corrected |
| **A-001** | Backend team lands **B1, B3, B4** | `curl` against a running server returns the new shapes |

> **CHECKPOINT 0** — A single `curl` sequence completes bootstrap → session start → one audio turn → complete, with a real WAV file, returning real facts. **If this does not work from curl, it will not work from Flutter.** Stop here until it does.

---

### PHASE 1 — Foundation

| Ticket | Work | Done when |
|---|---|---|
| **A-010** | Delete `services/`, `map/`. Remove BLE code paths. Delete every `mock_*.dart`, fixture list, and hardcoded sample. | `grep -rniE "mock\|dummy\|sample\|lorem\|placeholder" lib/` returns nothing in shipped code |
| **A-011** | Generate DTOs from `openapi.json` into `lib/data/generated/`. Delete superseded hand-written models. | Generated client compiles |
| **A-012** | `AppConfig` reads `API_BASE_URL` from `--dart-define`. **No default value** — app shows a config error screen if absent. | Release build with no define shows the error screen, not a localhost fallback |
| **A-013** | Dio client + `AuthInterceptor` (B1 token) + `IdempotencyInterceptor` (B5 UUID per mutating call) + error mapper for 401/403/404/409/422/5xx/timeout | Each status maps to a distinct user-facing state per Web Spec §10.2 |
| **A-014** | i18n scaffold: `flutter gen-l10n`, 5 ARB files, all English strings extracted. Add `avoid_hardcoded_strings` lint. | `flutter analyze` fails on a literal string added to a widget |

> **CHECKPOINT 1** — App launches, reaches a screen, shows a real error when the backend is off. Nothing is faked.

---

### PHASE 2 — The Vertical Slice

This is the phase that matters. Master Context §31: build the complete thin path before any breadth.

```
QR scan → language → consent → identity → bootstrap
   → call session start → ONE voice turn → real facts on screen
```

| Ticket | Work | Done when |
|---|---|---|
| **A-020** | Welcome + QR scan (and manual token entry fallback) | Scanning a real poster QR yields a real token |
| **A-021** | Language select, driven by `supported_languages` from B4. Selection sets Flutter locale **and** the `language` sent to every subsequent call. | Switching to Tamil changes app chrome *and* the language of `welcome_text` from the server |
| **A-022** | Consent screen: plain-language text, TTS audio explanation, explicit accept. POSTs consent record (B7). | Consent row appears in the backend audit table |
| **A-023** | Identity: ABHA / mobile / guest → real patient resolution → `bootstrap` | Real `encounter_id` + `token_number` returned |
| **A-024** | Audio recorder: 16kHz mono, permission flow with a rationale screen, level metering | Recorded WAV plays back correctly and is accepted by `/audio-turn` |
| **A-025** | Call screen v1 — deliberately ugly. Record → POST → render `transcript`, `facts_extracted`, `next_question`. Play `next_question_audio_url`. | Speaking Hindi into the phone returns a real Hindi transcript and real extracted facts |

> **CHECKPOINT 2 — THE ONE THAT COUNTS**
> Speak a symptom in Hindi into a physical Android phone. Real facts appear on screen. **The patient appears in the doctor queue on the laptop.**
> Per Master Context §31, nothing else starts until this works end to end.

---

### PHASE 3 — Complete the Intake Loop

| Ticket | Work | Done when |
|---|---|---|
| **A-030** | Multi-turn loop until `is_complete`, with turn history and rolling captions | A 6-turn interview completes without state loss |
| **A-031** | **Touch input mode** — every question answerable by tapping instead of speaking (PS §2.3 dual-mode requirement, and the ASR-failure fallback from Master Context §46) | Airplane-mode-the-mic: interview still completes by touch |
| **A-032** | Explain-back verification: TTS summary + 72dp YES/NO. Facts move to `PATIENT_CONFIRMED`. | Verification status visible on the doctor cockpit |
| **A-033** | `POST /api/encounters/{id}/complete` → token card | Token matches the doctor queue |
| **A-034** | Emergency path — server-flagged red flag preempts the queue and shows a full-screen alert | Saying a red-flag phrase jumps the patient to position #1 |
| **A-035** | Session rehydration (B6) after app kill | Force-stop at turn 4, relaunch, resume at turn 4 |

> **CHECKPOINT 3** — Full voice intake and full touch intake both produce identical ClinicalFact structures on the doctor side.

---

### PHASE 4 — Documents

| Ticket | Work | Done when |
|---|---|---|
| **A-040** | Camera capture with guided viewfinder, retake, crop | Image uploads with correct `file` + `document_type` fields |
| **A-041** | Render real `ocr_results` bounding boxes over the captured image | Boxes align with actual text on a real prescription |
| **A-042** | Render `extracted_medications` + `flagged_interactions` (B2) with confidence | A real prescription photo yields real medication names |
| **A-043** | Low-confidence path: show the source image and ask the patient to confirm (Master Context §46 OCR failure) | Sub-threshold extraction triggers verification, never silent acceptance |

> **CHECKPOINT 4** — A genuine paper prescription, photographed on a phone, appears line-cited in the doctor cockpit.

---

### PHASE 5 — AYUSH + Queue

| Ticket | Work | Done when |
|---|---|---|
| **A-050** | Dashavidha Pariksha module posting real structured fields (Prakriti, Vikriti, Agni, Koshtha, Ahara-Vihara) | AYUSH block renders in the doctor cockpit |
| **A-051** | Queue tracker with real `position` / `estimated_wait_minutes` / `cabin`, polling with backoff | Number decrements as the doctor calls patients |
| **A-052** | Completion screen: token, department, room as large text | — |

> **CHECKPOINT 5** — Feature-complete against the PS. Freeze scope here.

---

### PHASE 6 — Accessibility & Localization Hardening

Not a polish pass. The PS names accessibility as a hard requirement and the app is for elderly, low-literacy, first-visit patients. Budget real time. Details in §6 and §7.

| Ticket | Work |
|---|---|
| **A-060** | TalkBack pass over all 11 features — every interactive element labelled in the active locale |
| **A-061** | Text scaling to 2.0× with zero clipping or overflow on a 5" screen |
| **A-062** | Contrast audit against the tokens; fix every failure below 4.5:1 |
| **A-063** | Audio-first mode: complete an intake with the screen off / eyes closed |
| **A-064** | Indic typography: Noto fonts, line-height 1.5–1.65, diacritic clipping test per script |
| **A-065** | Native-speaker review of all 5 ARB files — machine translation of clinical UI is a liability |
| **A-066** | Reduced-motion + disable the waveform animation when the OS requests it |

> **CHECKPOINT 6** — A blindfolded team member completes an intake using only TalkBack and audio prompts.

---

### PHASE 7 — Resilience

| Ticket | Work |
|---|---|
| **A-070** | Drift local draft store, encounter-scoped |
| **A-071** | WorkManager sync queue with exponential backoff, using B5 idempotency keys |
| **A-072** | Honest connectivity banner: *"Saved on your phone. Will sync when you're back online."* — never a silent failure, never fake success |
| **A-073** | Graceful degradation matrix per Master Context §46: ASR fail → touch; TTS fail → text; OCR fail → source image; backend fail → queued draft |

> **CHECKPOINT 7** — Toggle airplane mode mid-interview. Nothing is lost, nothing is duplicated, nothing is invented.

---

## 6. Accessibility Specification

Concrete and testable. Vague a11y goals produce no a11y.

**Touch targets**
- Absolute minimum 48dp (Material)
- Primary intake CTAs 72dp — matches the 68px kiosk standard in the web spec
- Minimum 8dp between adjacent targets

**Screen reader (TalkBack)**
- Every `IconButton`, card and control wrapped in `Semantics` with a `label` **in the active locale**, never English-only
- Decorative elements (waveform, avatar) wrapped in `ExcludeSemantics`
- Incoming transcript captions announced via `SemanticsService.announce` so a blind user knows a turn changed
- Logical focus order; verify with TalkBack's swipe-next

**Text scaling**
- Use `MediaQuery.textScalerOf(context)` — never `textScaleFactor`, and never lock it to 1.0
- Every screen must survive 2.0× on a 5-inch device. Use `Flexible` / `FittedBox` / scrollable columns, not fixed heights.

**Contrast**
- Body text ≥ 4.5:1; large text ≥ 3:1. Target 7:1 where the web spec claims AAA — do not claim AAA in the pitch unless the tokens actually measure it.

**Never color-only**
- `RED` / `YELLOW` / `GREEN` severity badges must carry an icon **and** localized text. Roughly 8% of Indian men are red-green colour deficient; a red-only emergency badge is invisible to them.

**Audio-first path (PS explicitly requires visually-impaired support)**
- Every screen completable with TTS prompt + one large button
- A persistent "🔊 Repeat" control on every screen
- Auto-play the question audio on turn arrival unless the user has muted

**Motion**
- Honour `MediaQuery.disableAnimationsOf(context)`; kill the waveform and avatar animation when set

**Indic typography**
- Noto Sans Devanagari / Tamil / Telugu
- `line-height` 1.5–1.65 — Devanagari matras and Tamil/Telugu vowel signs clip at 1.2
- Regression-test the strings: `स्त्री`, `ஸ்ரீ`, `క్రి`, `ऋ`, `ై`

---

## 7. Localization Specification

There are **two distinct localization surfaces** and conflating them causes clinical bugs.

**Surface 1 — App chrome (client-side)**
- ARB files, `flutter gen-l10n`, 5 locales: `en`, `hi`, `ta`, `te`, `mr`
- Zero string literals in widgets, enforced by lint
- Dates/numbers through `intl` with the active locale
- Reviewed by a native speaker per language. Clinical UI in machine-translated Tamil is worse than English.

**Surface 2 — Clinical content (server-side)**
- `welcome_text`, `next_question`, `assistant_reply`, extracted concepts, explain-back summaries — **all generated by the backend in the patient's language**
- The app renders them verbatim
- **The app must never translate clinical content client-side.** Running an on-device translator over "sīne mein jalan nahīn hai" risks dropping the negation — exactly the failure the master context calls out in §19 and §45.

**The binding rule**
The `language` code chosen at A-021 is the single source of truth. It sets the Flutter locale *and* is sent on every API call. They must never diverge mid-session — an app showing Tamil chrome while the server generates Hindi questions is worse than monolingual.

**Adding a sixth language** should mean: one ARB file + one backend locale entry. If it means touching feature code, the abstraction is wrong.

---

## 8. No-Mock-Data Enforcement

Policy is not enough; make it mechanical.

**Build gate** — fail CI if these appear in `lib/`:
```bash
grep -rniE "mock|dummy|fake|sample|lorem|hardcoded|TODO: replace" lib/ \
  --include="*.dart" | grep -v "_test.dart" && exit 1
```

**No silent fallbacks**
- `AppConfig.apiBaseUrl` has no default. Missing define → visible config error screen.
- Repositories throw on failure. They never return canned objects.
- Empty states say *"No documents uploaded yet"* — never a pre-populated example.

**Test fixtures live only in `test/`.** Never imported from `lib/`.

**Demo data is server-side.** If the demo needs 17 patients in the queue, they get seeded into SQLite by a backend script — not hardcoded in the app. This also means the demo survives someone tapping an unexpected button.

---

## 9. Definition of Done

Adapted from Master Context §32. The Android channel is done when:

```
PATIENT (phone)
  ↓ QR / manual token
LANGUAGE + CONSENT (recorded server-side)
  ↓
IDENTITY → real encounter
  ↓
VOICE or TOUCH intake  ← both paths, identical output
  ↓
Real ASR → real facts → PATIENT_CONFIRMED
  ↓
DOCUMENTS → real OCR → real extraction → patient-verified
  ↓
AYUSH Dashavidha (real structured fields)
  ↓
SERVER safety + routing
  ↓
TOKEN + QUEUE (live)
  ↓
DOCTOR DASHBOARD — indistinguishable in structure from a kiosk encounter
```

Plus:
- [ ] Zero mock data in `lib/` (grep gate passes)
- [ ] All 5 locales complete and native-reviewed
- [ ] TalkBack intake completed end to end
- [ ] 2.0× text scale, no clipping
- [ ] Airplane-mode interruption loses nothing, duplicates nothing
- [ ] Every DTO generated from `openapi.json`
- [ ] App kill mid-intake resumes correctly

---

## 10. Risks

| Risk | Mitigation |
|---|---|
| Someone builds from the v3 contract | This doc supersedes it. Delete or clearly mark v3 as stale. |
| Backend changes break the app silently | Regenerate DTOs on every backend change; treat generation as part of the backend's done-criteria |
| "Offline AI on the phone" claim in the pitch | State plainly: kiosk = offline AI, mobile = offline drafts. Judges will ask what model runs on the handset. |
| Localization left to the end | Phase 1 scaffolds i18n. Adding it at Phase 6 means touching all 11 features. |
| Accessibility treated as polish | It's a named PS requirement with its own checkpoint. It cannot be cut. |
| Scope creep back into `map`/`services`/BLE | They're deleted, not disabled. Restoring them requires a decision, not a commit. |
| Duplicate encounters from retries | B5 idempotency keys, landed before Phase 7 |

---

*MediKiosk Android Revamp Roadmap — supersedes the contract sections of the v3 two-developer plan.*
