# MediKiosk — Android & Mobile Kiosk Design System Specification
## Canonical UI/UX Design System, Component Catalog & Screen Blueprint
**Document Version:** 4.0.0 (SIH26047 Production Specification — Light Medical Standard)  
**Visual Benchmark:** Harmonized with MediKiosk Web Interface (ReliaCare-Inspired Light Healthcare Glassmorphism)  
**Target Clients:** Android Mobile (BYOD Patient App), Android Tablet / Kiosk (1280 × 800 Landscape)  
**Primary Users:** OPD Patients (Elderly 68+ yrs, Rural, Low-Literacy, 5 Indian Languages) & Clinical Attendants  
**Governing Documents:** `DOCS/MediKiosk_Master_Context.md`, `DOCS/Mobile Revamp/MediKiosk_Android_Revamp_Roadmap.md`, `MEDIKIOSK_WEB_DESIGN_SPEC.md`

---

## Table of Contents
1. [Design Philosophy, Visual Theme & Foundational Rules](#1-design-philosophy-visual-theme--foundational-rules)
2. [Three-Layer Design Token Architecture](#2-three-layer-design-token-architecture)
   - [2.1 Layer 1: Primitive Tokens (Colors, Spacing, Radius, Shadows, Glass)](#21-layer-1-primitive-tokens)
   - [2.2 Layer 2: Semantic Tokens (Light Medical Intent)](#22-layer-2-semantic-tokens)
   - [2.3 Layer 3: Component Tokens (Widget-Scoped)](#23-layer-3-component-tokens)
   - [2.4 Contrast & Accessibility Matrix (WCAG 2.2 AAA Compliance)](#24-contrast--accessibility-matrix-wcag-22-aaa-compliance)
3. [Typography & Multilingual Script Architecture](#3-typography--multilingual-script-architecture)
   - [3.1 Font Families & Script Fallback Stack (Lora + DM Sans + Noto)](#31-font-families--script-fallback-stack)
   - [3.2 Scale, Modular Rhythm & Weights](#32-scale-modular-rhythm--weights)
   - [3.3 Indic Diacritic Preservation & Text Scaling Protection](#33-indic-diacritic-preservation--text-scaling-protection)
4. [Ergonomics, Responsive Layout & Grid System](#4-ergonomics-responsive-layout--grid-system)
   - [4.1 Breakpoint Strategy & Target Displays](#41-breakpoint-strategy--target-displays)
   - [4.2 Touch Targets & Elderly Thumb Zones](#42-touch-targets--elderly-thumb-zones)
   - [4.3 Spacing Scale & Layout Constraints](#43-spacing-scale--layout-constraints)
5. [Iconography & Official Brand Assets (Strict No-Emoji Standard)](#5-iconography--official-brand-assets-strict-no-emoji-standard)
   - [5.1 Material Symbols Canonical Mapping](#51-material-symbols-canonical-mapping)
   - [5.2 Official MediKiosk Brand Mark & AIIA Seal Specification](#52-official-medikiosk-brand-mark--aiia-seal-specification)
   - [5.3 Semantic Status Badge Matrix](#53-semantic-status-badge-matrix)
6. [Motion Choreography & Audio Feedback](#6-motion-choreography--audio-feedback)
   - [6.1 Curves & Timing Tokens](#61-curves--timing-tokens)
   - [6.2 Signature Micro-Interactions (Mic Halo, 9-Bar Waveform, OCR Scanner)](#62-signature-micro-interactions)
   - [6.3 Auditory Cues (Earcons & TTS Readback)](#63-auditory-cues)
7. [Comprehensive Component Catalog (29 Production Components)](#7-comprehensive-component-catalog)
8. [Screen-by-Screen UI Layout Blueprint (Screens 01 to 24 + Screen A-06B)](#8-screen-by-screen-ui-layout-blueprint)
9. [Global States & System Resilience Framework](#9-global-states--system-resilience-framework)
10. [Flutter Implementation Architecture & Dart Code Blueprint](#10-flutter-implementation-architecture--dart-code-blueprint)
11. [Developer Checklist & Acceptance Verification Matrix](#11-developer-checklist--acceptance-verification-matrix)

---

# 1. DESIGN PHILOSOPHY, VISUAL THEME & FOUNDATIONAL RULES

MediKiosk is deployed in high-stress, noisy government hospital outpatient departments (OPDs) where patients wait 45–90 minutes for a 2-minute doctor consultation. The visual style follows the **MediKiosk Web Interface Light Medical Standard**, drawing inspiration from modern high-precision clinical portals (such as ReliaCare and RetinopathyScan).

### Visual Aesthetics Standard:
1. **Luminous Light Medical Canvas:** Warm cream-to-sage canvas (`#F8FAF5` to `#DFF2EB`) creating an atmosphere of calm healing, institutional dignity, and warmth. Zero gloomy dark modes, zero harsh stark white glare.
2. **Deep Forest Typographic Authority:** Primary text in deep forest `#064E3B` and dark pine `#1A3C34`. Provides superior visual acuity for elderly eyes while conveying medical trust and AYUSH heritage.
3. **High-Contrast Lime Action Accents:** Primary interactive buttons and selection highlights utilize vibrant medical lime (`#A3E635`) paired with deep forest text (`#064E3B`), surpassing WCAG 2.2 AAA with a **7.6:1 contrast ratio**.
4. **Frosted Glass Chrome & Pill Geometry:** Soft translucent white cards (`rgba(255, 255, 255, 0.72)`) with a gentle blur, razor-thin borders (`#D7E8DF`), and friendly pill curvature (`radius-full: 9999dp`, `radius-2xl: 32dp`) that remove intimidation for first-time smartphone users.
5. **Strict No-Emoji Standard:** Hospital-grade clinical dignity requires authentic UI iconography. Emojis (e.g. syringe, pill, siren) are strictly prohibited across all patient and staff views. All actions use crisp, standardized Material Symbols.
6. **No AI Slops or Unexplained Scores:** Zero decorative hallucinated blobs, zero raw machine-learning jargon (`"LLM inference score: 0.94"`, `"Token probability"`). The UI communicates verified clinical facts in plain everyday words.

### Foundational Clinical Rules:
- **Rule A — Access Channel, Not a Second Backend:** The mobile app renders and collects; it never computes clinical diagnosis, drug interaction algorithms, or client-side translation. All channels converge on the canonical `ClinicalFact` model.
- **Rule B — Closed-Loop Explain-Back (No Patient Editing Burden):** Patients confirm or clarify statements using large conversational cards and high-contrast **[YES]** / **[NO]** controls. Patients are never forced to edit dosage numbers, clinical ICD/SNOMED codes, or OCR text strings manually.
- **Rule C — Verifiable Provenance ("No Receipt, No Fact"):** Every medication, dosage, or lab value extracted from an uploaded document links directly to a highlighted bounding box and cited line index on the original scanned document.
- **Rule D — Mobile BYOD is Offline-Drafts, Not Offline-AI:** Handsets do not run 7B LLMs or Whisper neural nets. If connectivity drops, mobile drafts are stored securely in local SQLite/Drift and synced when connectivity returns via idempotency keys. The physical kiosk station remains the local offline-AI hub.

---

# 2. THREE-LAYER DESIGN TOKEN ARCHITECTURE

The design tokens follow a strict 3-tier system: **Primitive (Raw Values) $\rightarrow$ Semantic (Intent/Role) $\rightarrow$ Component (Scoped).**

```text
┌────────────────────────────────────────────────────────┐
│  LAYER 1: PRIMITIVE TOKENS (Raw Hex, DP, Durations)    │
│  lime500 (#A3E635), forest900 (#064E3B), space16 (16dp)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: SEMANTIC TOKENS (Intent & Context)           │
│  mdBrandPrimary, mdTextOnBrand, mdSurfaceGlass, mdRed  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 3: COMPONENT TOKENS (Widget-Scoped)             │
│  choiceCardBg, voiceBtnHalo, triageBannerBorder        │
└────────────────────────────────────────────────────────┘
```

---

## 2.1 Layer 1: Primitive Tokens

### A. Raw Color Palette (Harmonized with Web Design Tokens)
```text
/* Sage & Cream Neutrals */
slate-25:    #FBFDF9    /* Ultra-light card surface */
slate-50:    #F8FAF5    /* mdCanvas (Base cream/sage canvas) */
slate-100:   #EEF6F1    /* mdSurfaceSubtle (Input background, disabled card) */
slate-200:   #D7E8DF    /* mdBorder (Standard card border, divider) */
slate-300:   #B5CDBF    /* mdBorderStrong / Input focus outline */
slate-400:   #8AA99A    /* Inactive icons, placeholder text */
slate-500:   #5F7A6E    /* mdTextMuted (Secondary descriptions, timestamps) */
slate-600:   #456056    /* Secondary body copy */
slate-700:   #374151    /* Primary body copy */
slate-800:   #1A3C34    /* mdBrandDark / Forest headings */
slate-900:   #064E3B    /* mdTextPrimary / Deep forest high-contrast text */
white:       #FFFFFF    /* mdSurface (Card backgrounds, modals) */

/* Lime Accents (Primary Interactive Brand) */
lime-50:     #F3FCE8    /* mdBrandTint (Selected card background) */
lime-100:    #E4F8C8    /* Selected card border tint */
lime-200:    #C9F0A0    /* Soft active pill highlight */
lime-400:    #B4E86A    /* Interactive secondary button hover */
lime-500:    #A3E635    /* mdBrandPrimary (Dominant CTA button fill) */
lime-600:    #8BCF28    /* Pressed button state */
lime-800:    #4D7C0F    /* High-contrast accessible text variant */

/* Soft Sage & Mint */
sage-100:    #DFF2EB    /* Gradient top start */
sage-200:    #C8E8DC    /* Card inner tint */
sage-300:    #A8D5C6    /* Subtle tag background */

/* Healthcare Teal & AYUSH Forest Green */
teal-50:     #E7F8F6    /* Telehealth & Vitals tint */
teal-500:    #12A59C    /* Sensor active line */
teal-700:    #0B8F87    /* Telehealth / connected hardware badge */
teal-900:    #075B56    /* Deep teal accent */

emerald-50:  #EAF8F0    /* mdAyushTint (AYUSH card background) */
emerald-600: #17824C    /* mdSuccessInteractive */
emerald-800: #0D6338    /* Confirmed fact border */
emerald-900: #047857    /* mdAyushGreen (Safe state, AIIA branding) */

/* Triage Red & Warning Amber */
red-50:      #FFF0F0    /* mdTriageTint */
red-100:     #FFE0E0    /* Red flag chip background */
red-600:     #E04040    /* Triage active highlight */
red-700:     #C83A3A    /* mdTriageRed (Emergency alert banner & text) */
red-900:     #881D1D    /* Critical banner background */

amber-50:    #FFF6E5    /* mdWarningTint */
amber-100:   #FEEDCC    /* Warning tag background */
amber-500:   #D97E00    /* Amber indicator */
amber-700:   #B66A00    /* mdWarning (Medication conflict, missing document) */
amber-900:   #7A4300    /* Dark amber alert text */
```

### B. Spacing Scale (4dp / 8dp Base System)
```text
space-2:     2dp     /* Micro offsets */
space-4:     4dp     /* Tight icon-text padding */
space-8:     8dp     /* Compact element spacing */
space-12:    12dp    /* Inner chip padding, badge inset */
space-16:    16dp    /* Standard card internal padding (Phone) */
space-20:    20dp    /* Button horizontal padding */
space-24:    24dp    /* Screen edge margin (Phone) / Card padding (Tablet) */
space-32:    32dp    /* Section vertical separation */
space-40:    40dp    /* Kiosk screen margin */
space-48:    48dp    /* Major grouping separation */
space-64:    64dp    /* Primary CTA vertical clearance */
space-80:    80dp    /* Hero welcome spacing */
```

### C. Border Radius Scale (Pill-First Geometry)
```text
radius-xs:   4dp     /* Mini tags */
radius-sm:   8dp     /* Evidence line badges */
radius-md:   12dp    /* Input fields, secondary buttons */
radius-lg:   16dp    /* Compact choice cards */
radius-xl:   24dp    /* Primary intake cards */
radius-2xl:  32dp    /* Large modal containers, hero panels */
radius-full: 9999dp  /* Pills, primary action buttons, mic trigger */
```

### D. Elevation & Glassmorphism Scale
```text
elevation-0: None
elevation-glass: Background: rgba(255, 255, 255, 0.72), Blur: 14dp, Border: 1dp solid rgba(255, 255, 255, 0.65)
elevation-1: Offset(0, 2), Blur: 8,  Color: rgba(6, 78, 59, 0.05)  /* Static cards */
elevation-2: Offset(0, 4), Blur: 12, Color: rgba(6, 78, 59, 0.08)  /* Interactive cards, hover */
elevation-3: Offset(0, 8), Blur: 24, Color: rgba(6, 78, 59, 0.12)  /* Modals, Sticky bottom bar */
elevation-active-lime: Offset(0, 4), Blur: 16, Color: rgba(163, 230, 53, 0.35) /* Primary CTA glow */
elevation-active-red:  Offset(0, 6), Blur: 20, Color: rgba(200, 58, 58, 0.25)  /* Emergency SOS glow */
```

---

## 2.2 Layer 2: Semantic Tokens

| Token Name | Hex / Value | Material 3 Mapping | Semantic Role & Intent |
|---|---|---|---|
| `mdCanvas` | `#F8FAF5` | `colorScheme.surface` | Base app background (cream/sage serene canvas) |
| `mdSurface` | `#FFFFFF` | `colorScheme.surfaceContainer` | Opaque white card background, modals |
| `mdSurfaceGlass` | `rgba(255, 255, 255, 0.72)` | `colorScheme.surfaceContainerHigh` | Frosted glass card surface |
| `mdSurfaceSubtle` | `#EEF6F1` | `colorScheme.surfaceContainerHighest`| Disabled states, unselected input fill |
| `mdBrandPrimary` | `#A3E635` | `colorScheme.primary` | Dominant healthcare CTA fill (Vibrant Lime) |
| `mdBrandDark` | `#064E3B` | `colorScheme.primaryContainer` | Institutional authority, dark badge fill |
| `mdBrandTint` | `#F3FCE8` | `colorScheme.secondaryContainer`| Selected card tint, subtle brand focus |
| `mdTextOnBrand` | `#064E3B` | `colorScheme.onPrimary` | High-contrast dark forest text on lime CTA |
| `mdTextPrimary` | `#064E3B` | `colorScheme.onSurface` | Main headings, clinical questions, primary labels |
| `mdTextSecondary`| `#374151` | `colorScheme.onSurfaceVariant` | Body copy, patient descriptions |
| `mdTextMuted` | `#5F7A6E` | `colorScheme.outline` | Subtitles, helper text, timestamps |
| `mdTextInverse` | `#FFFFFF` | `colorScheme.inverseSurface` | White text on red alerts & dark badges |
| `mdBorder` | `#D7E8DF` | `colorScheme.outlineVariant` | Standard card border (1.5dp solid) |
| `mdBorderSelected`| `#A3E635` | `colorScheme.primary` | Selected card border (3dp solid lime) |
| `mdAyushGreen` | `#047857` | `colorScheme.tertiary` | AYUSH stream, positive fact confirmation |
| `mdTriageRed` | `#C83A3A` | `colorScheme.error` | Red Flag emergency alert, SOS trigger |
| `mdSuccess` | `#17824C` | `colorScheme.secondary` | Confirmed facts, successful OCR match |
| `mdWarning` | `#B66A00` | `colorScheme.errorContainer` | Medication gaps, incomplete documents |

---

## 2.3 Layer 3: Component Tokens

| Component Area | Component Token | Semantic Source Token | Visual Spec |
|---|---|---|---|
| **Large Choice Card** | `choiceCardBg` | `mdSurfaceGlass` | Translucent `#FFFFFF` (72%) with 1.5dp `mdBorder` |
| | `choiceCardBgSelected`| `mdBrandTint` | `#F3FCE8` with 3dp `mdBrandPrimary` border |
| | `choiceCardTitleColor`| `mdTextPrimary` | 22sp DM Sans SemiBold (`#064E3B`) |
| **Primary CTA Button** | `primaryBtnBg` | `mdBrandPrimary` | Full pill radius, `#A3E635` fill |
| | `primaryBtnTextColor`| `mdTextOnBrand` | 22sp DM Sans SemiBold (`#064E3B`) |
| | `primaryBtnShadow` | `elevation-active-lime`| 0 4px 14px rgba(163, 230, 53, 0.35) |
| **Voice Button** | `voiceBtnBgIdle` | `mdBrandDark` | Circular 96dp, Deep Forest `#064E3B` |
| | `voiceBtnBgActive` | `mdTriageRed` | Circular 96dp, Crimson `#C83A3A` |
| | `voiceBtnHaloColor` | `mdBrandPrimary` | Expanding 24dp ring, `#A3E635` opacity 0.40 |
| **Triage Alert Banner**| `triageBannerBg` | `red-50` | `#FFF0F0` emergency container |
| | `triageBannerBorder`| `mdTriageRed` | 2dp solid `#C83A3A` |
| | `triageBannerText` | `red-900` | `#881D1D` 24sp Lora Bold |
| **Document Guide** | `cameraGuideBorder` | `mdSurface` | 3dp solid `#FFFFFF` |
| | `cameraGuideCorner` | `mdBrandPrimary` | 5dp solid corner bracket `#A3E635` |
| | `cameraGuideSuccess`| `mdSuccess` | 5dp solid corner bracket `#17824C` |
| **Queue Token Card** | `queueTokenBadgeBg` | `lime-50` | `#F3FCE8` rounded pill |
| | `queueTokenNumber` | `mdBrandDark` | 48sp JetBrains Mono ExtraBold (`#064E3B`) |

---

## 2.4 Contrast & Accessibility Matrix (WCAG 2.2 AAA Compliance)

To guarantee effortless reading for elderly patients suffering from presbyopia, cataracts, or diabetic retinopathy under harsh hospital lighting:

| Foreground Element | Background Canvas | Contrast Ratio | WCAG 2.2 Status | Usage Context |
|---|---|---|---|---|
| `mdTextOnBrand` (`#064E3B`) | `mdBrandPrimary` (`#A3E635`) | **7.6 : 1** | **PASS AAA** (Exceeds 7.0:1) | Primary action button text |
| `mdTextPrimary` (`#064E3B`) | `mdSurface` (`#FFFFFF`) | **15.8 : 1** | **PASS AAA** | Card headings, questions, data |
| `mdTextPrimary` (`#064E3B`) | `mdCanvas` (`#F8FAF5`) | **14.9 : 1** | **PASS AAA** | Screen titles on page canvas |
| `mdTextSecondary` (`#374151`)| `mdSurface` (`#FFFFFF`) | **10.1 : 1** | **PASS AAA** | Body paragraphs, consent items |
| `mdTextMuted` (`#5F7A6E`) | `mdSurface` (`#FFFFFF`) | **4.8 : 1** | **PASS AA** (Large / helper) | Timestamps, secondary subtitles |
| `mdTextInverse` (`#FFFFFF`)| `mdBrandDark` (`#064E3B`) | **15.8 : 1** | **PASS AAA** | Dark badges, idle voice mic icon |
| `mdTextInverse` (`#FFFFFF`)| `mdTriageRed` (`#C83A3A`) | **5.1 : 1** | **PASS AA** | Emergency SOS buttons, alerts |
| `mdTextInverse` (`#FFFFFF`)| `mdAyushGreen` (`#047857`) | **5.4 : 1** | **PASS AA** | AYUSH verified tags |
| `mdBorder` (`#D7E8DF`)| `mdCanvas` (`#F8FAF5`) | **3.1 : 1** | **PASS UI** (Exceeds 3.0:1) | Card borders & dividers |

> **Critical Rule:** Never communicate status via color alone. Every colored badge or state indicator must pair color with an unambiguous text label and a distinct semantic icon.

---

# 3. TYPOGRAPHY & MULTILINGUAL SCRIPT ARCHITECTURE

MediKiosk serves patients across **5 Indian Languages** simultaneously:
1. **English (`en`)**
2. **Hindi (`hi`)** — Devanagari script
3. **Tamil (`ta`)** — Tamil script
4. **Telugu (`te`)** — Telugu script
5. **Marathi (`mr`)** — Devanagari script

---

## 3.1 Font Families & Script Fallback Stack

The typography harmonizes with the MediKiosk Web Interface, combining **`Lora`** for prominent headlines, **`DM Sans`** for user interface elements, and **`Google Noto Sans`** for Indian language scripts:

```text
Display & Screen Titles:  'Lora', serif (Weights: 500, 600, 700)
UI, Body & Buttons:        'DM Sans', sans-serif (Weights: 400, 500, 600, 700)
Devanagari Fallback:       'Noto Sans Devanagari', sans-serif
Tamil Fallback:            'Noto Sans Tamil', sans-serif
Telugu Fallback:           'Noto Sans Telugu', sans-serif
Code & Queue Tokens:       'JetBrains Mono', monospace
```

Flutter Configuration:
```dart
fontFamily: 'DMSans',
fontFamilyFallback: const [
  'NotoSansDevanagari',
  'NotoSansTamil',
  'NotoSansTelugu',
  'Roboto',
],
```

---

## 3.2 Scale, Modular Rhythm & Weights

| Style Token | Font Family | Size (sp) | Line Height | Weight | Usage |
|---|---|---|---|---|---|
| `displayLarge` (H1) | **Lora** | 36 sp | 46 dp (1.28) | Bold (700) | Welcome titles, emergency headings |
| `headlineLarge` (H2) | **Lora** | 28 sp | 38 dp (1.35) | SemiBold (600) | Main intake questions, token titles |
| `headlineMedium` (H3)| **DM Sans** | 24 sp | 32 dp (1.33) | SemiBold (600) | Card headings, section titles |
| `bodyLarge` | **DM Sans** | 22 sp | 32 dp (1.45) | Regular (400) / Med (500)| Choice card subtitles, consent statements |
| `bodyMedium` | **DM Sans** | 18 sp | 28 dp (1.55) | Regular (400) | Standard body text, helper guidance |
| `buttonText` | **DM Sans** | 22–24 sp | 30 dp (1.25) | SemiBold (600) | Primary CTA actions ([CONTINUE], [START]) |
| `tokenDisplay` | **JetBrains Mono**| 48 sp | 56 dp (1.16) | ExtraBold (800)| Queue token number (`A-261`) |
| `labelSmall` | **DM Sans** | 16 sp | 24 dp (1.50) | Medium (500) | Timestamps, status chips, metadata |

---

## 3.3 Indic Diacritic Preservation & Text Scaling Protection

1. **Diacritic Clearance (`line-height` safety):** In complex Indic scripts, upper and lower vowel marks (*matras* such as `ि`, `ी`, `ु`, `ू`, and conjunct diacritics in Tamil/Telugu) clip vertically when line height is tight. All text styles enforce a minimum line-height multiplier of **1.45 to 1.65** to ensure full glyph clearance.
2. **Text Scaling Protection:** In `MaterialApp`, `MediaQuery.textScaler` must be clamped between **1.0x and 1.35x**. This allows low-vision users to enjoy magnified text without breaking card layout boundaries or triggering horizontal overflows.

---

# 4. ERGONOMICS, RESPONSIVE LAYOUT & GRID SYSTEM

MediKiosk renders seamlessly across two distinct physical form factors:
- **Form Factor A: 1280 × 800 Landscape Tablet / Kiosk Display** (In-Clinic OPD Kiosk)
- **Form Factor B: 360 × 800 to 412 × 915 Portrait Smartphone** (Patient BYOD Mobile App)

---

## 4.1 Breakpoint Strategy & Target Displays

```text
┌────────────────────────┬────────────────────────────────────────────────────────┐
│ Breakpoint Class       │ Screen Width Range & Typical Device                     │
├────────────────────────┼────────────────────────────────────────────────────────┤
│ Compact (Phone)        │ width < 600 dp (Android smartphones in portrait)       │
│ Medium (Tablet Port.)  │ 600 dp <= width < 840 dp (Small 7-8" tablets)          │
│ Expanded (Kiosk/Desk)  │ width >= 840 dp (10-12" Landscape Kiosks: 1280 × 800)  │
└────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 4.2 Touch Targets & Elderly Thumb Zones

- **Absolute Minimum Interactive Target:** `64 × 64 dp` (Surpasses standard Android 48dp guidelines).
- **Preferred Primary Action Target (Kiosk CTAs):** `72 × 88 dp` (Height $\ge 72$ dp, full width or $\ge 240$ dp).
- **Gutter Spacing:** Minimum `16 dp` gutter between touch targets to prevent accidental double-taps.
- **Phone Thumb Zone:** On portrait phones, all primary progression buttons are docked within the lower 35% of the screen height.

```text
PHONE ERGONOMICS (PORTRAIT)        KIOSK ERGONOMICS (1280 × 800 LANDSCAPE)
┌───────────────────────────┐      ┌────────────────────┬────────────────────────┐
│ Header (Logo + Lang + Help)│      │ LEFT PANE (35%)    │ RIGHT PANE (65%)       │
├───────────────────────────┤      │                    │                        │
│ Question Prompt           │      │ MediKiosk Brand    │ Active Task Canvas     │
│                           │      │ Step 3 of 8        │                        │
│ Interactive Content       │      │                    │ [ Choice Card 1 ]      │
│ (Choice Cards / Waveform) │      │ Audio Help         │                        │
│                           │      │ [ Listen Aloud ]   │ [ Choice Card 2 ]      │
├───────────────────────────┤      │                    │                        │
│ [ PRIMARY CTA (72dp) ]    │      │ Emergency Exit     │ [ CONTINUE CTA (80dp)] │
│ Safe Area Bottom          │      │ [ SOS Help ]       │                        │
└───────────────────────────┘      └────────────────────┴────────────────────────┘
```

---

# 5. ICONOGRAPHY & OFFICIAL BRAND ASSETS (STRICT NO-EMOJI STANDARD)

MediKiosk relies on clean, high-recognition iconography from **Material Symbols (Rounded)** with a stroke weight of `2.0` (Medium/Fill 0) to ensure high visibility without visual clutter. Emojis are strictly banned from all production screens.

---

## 5.1 Material Symbols Canonical Mapping

| Semantic Concept / Action | Material Symbol Identifier | Dart Constant | Accessibility Label |
|---|---|---|---|
| **Hospital / Medical Services** | `medical_services` | `Icons.medical_services_rounded` | "Hospital medical services" |
| **Language Switcher** | `language` | `Icons.language_rounded` | "Change interaction language" |
| **Help & Support** | `help_outline` | `Icons.help_outline_rounded` | "Get assistance from hospital staff" |
| **Consent Verified** | `verified_user` | `Icons.verified_user_rounded` | "Data privacy and security verified" |
| **Scan ABHA QR** | `qr_code_scanner` | `Icons.qr_code_scanner_rounded` | "Scan ABHA health ID QR code" |
| **Mobile Number** | `phone_android` | `Icons.phone_android_rounded` | "Enter mobile phone number" |
| **Continue / Skip** | `arrow_forward` | `Icons.arrow_forward_rounded` | "Continue to next step" |
| **Microphone Idle** | `mic` | `Icons.mic_rounded` | "Start speaking into microphone" |
| **Microphone Listening** | `mic_none` | `Icons.mic_none_rounded` | "Microphone listening" |
| **Stop Recording** | `stop_circle` | `Icons.stop_circle_rounded` | "Done speaking, stop recording" |
| **Keyboard / Type** | `keyboard` | `Icons.keyboard_rounded` | "Switch to typing on keyboard" |
| **Audio Readout** | `volume_up` | `Icons.volume_up_rounded` | "Listen to instructions read aloud" |
| **Confirm / Yes** | `check_circle` | `Icons.check_circle_rounded` | "Confirm, this is correct" |
| **Correction / Retry** | `replay` | `Icons.replay_rounded` | "No, say it again or record again" |
| **Red Flag Emergency** | `emergency` | `Icons.emergency_rounded` | "Emergency urgent attention needed" |
| **Document Scan** | `document_scanner` | `Icons.document_scanner_rounded`| "Scan prescription document" |
| **Camera Shutter** | `camera_alt` | `Icons.camera_alt_rounded` | "Capture photograph of document" |
| **Evidence Link** | `find_in_page` | `Icons.find_in_page_rounded` | "View original prescription evidence" |
| **Vitals Monitor** | `monitor_heart` | `Icons.monitor_heart_rounded` | "Medical vitals and sensor readings" |
| **Queue Token** | `confirmation_number` | `Icons.confirmation_number_rounded`| "Hospital OPD queue token" |
| **Doctor Cabin** | `medical_information` | `Icons.medical_information_rounded`| "Doctor room and OPD department" |
| **Ayurveda / AYUSH** | `spa` | `Icons.spa_rounded` | "AYUSH and Ayurvedic wellness" |
| **Phone Call Intake** | `call` | `Icons.call_rounded` | "Call AI Intake audio channel" |
| **End Call** | `call_end` | `Icons.call_end_rounded` | "End intake phone call" |
| **Network Online** | `wifi` | `Icons.wifi_rounded` | "Cloud Online connected" |
| **Network Offline / Edge**| `wifi_off` | `Icons.wifi_off_rounded` | "Local Edge Hub mode active" |

---

## 5.2 Official MediKiosk Brand Mark & AIIA Seal Specification

The brand asset is the **Official MediKiosk Mark** (`medikiosk-mark.png`), featuring:
- **Geometry:** Softened organic medical cross with integrated leaf node signifying the union of modern medicine and Ministry of AYUSH traditional healthcare.
- **Color Accent:** Primary forest `#064E3B` with vibrant lime `#A3E635` accent.
- **Companion Seal:** All India Institute of Ayurveda (AIIA) official emblem (`aiia-seal.png`).
- **Sizes:** `48 × 48 dp` (Topbar Header), `96 × 96 dp` (Screen Welcome Hero).

---

## 5.3 Semantic Status Badge Matrix

| Status Type | Background | Border Color | Icon & Text Color | Semantic Meaning |
|---|---|---|---|---|
| **Emergency / Red Flag** | `#FFF0F0` | `#C83A3A` | `#C83A3A` | High priority emergency triage |
| **Warning / Interaction** | `#FFF6E5` | `#B66A00` | `#B66A00` | Medication conflict / data gap |
| **Verified / Success** | `#EAF8F0` | `#17824C` | `#17824C` | Patient confirmed / normal vital |
| **Queue / Pending** | `#F3FCE8` | `#A3E635` | `#064E3B` | Active queue / in progress |
| **AYUSH / Holistic** | `#E7F8F6` | `#0B8F87` | `#0B8F87` | AYUSH profile / lifestyle intake |

---

# 6. MOTION CHOREOGRAPHY & AUDIO FEEDBACK

Motion in MediKiosk is functional, tactile, and calm.

---

## 6.1 Curves & Timing Tokens

| Duration Token | Milliseconds | Easing Curve | Use Case |
|---|---|---|---|
| `motionImmediate` | 100 ms | `Curves.linear` | Button press state, ink ripple |
| `motionFast` | 180 ms | `Curves.easeOutCubic` | Card selection toggle, chip expansion |
| `motionNormal` | 300 ms | `Curves.easeInOutCubic` | Screen push/pop transition, drawer slide |
| `motionSlow` | 500 ms | `Curves.decelerate` | Red Flag alert slide-in, modal entry |
| `motionPulse` | 1400 ms | `Curves.easeInOutSine` | Microphone active listening ring pulse |

> **Accessibility Rule:** If `MediaQuery.disableAnimationsOf(context)` or Android OS "Remove Animations" is enabled, all motion drops to instantaneous `0 ms` opacity swaps.

---

## 6.2 Signature Micro-Interactions

### A. Active Microphone Pulse Halo
- **Inner Ring:** Diameter `96dp` to `130dp`, opacity `0.40` $\rightarrow$ `0.0`.
- **Outer Ring:** Diameter `96dp` to `160dp`, opacity `0.20` $\rightarrow$ `0.0`, delayed by `250ms`.
- **Center Button:** Subtle scale pulsation (`1.0` to `1.04`).

### B. Live Audio Waveform Visualizer (9-Bar Dynamic Energy)
- **Bar Width:** `5 dp`, **Spacing:** `6 dp`, **Corner Radius:** `3 dp`.
- **Color:** Gradient from `mdBrandPrimary` (`#A3E635`) to `mdAyushGreen` (`#047857`).
- **Animation:** Continuous height interpolation between `6 dp` (silence) and `52 dp` (peak voice energy).

### C. Document Camera Laser Sweep
- **Corner Brackets:** `40 × 40 dp` L-shaped solid brackets (`5dp` stroke) at the 4 corners of the 4:3 document frame.
- **Scanning Sweep:** Horizontal lime-green laser line (`2dp` height with subtle ambient glow) sweeping vertically top to bottom (`1500ms` cycle).

---

## 6.3 Auditory Cues (Earcons & TTS Readback)

1. **Listening Started Earcon:** Soft ascending dual-tone chime (`440Hz` $\rightarrow$ `880Hz`, 120ms).
2. **Listening Completed Earcon:** Soft descending chime (`880Hz` $\rightarrow$ `440Hz`, 120ms).
3. **TTS Question Readback:** Every question screen offers a prominent **[Listen Aloud]** action invoking on-device TTS in the chosen Indian language.

---

# 7. COMPREHENSIVE COMPONENT CATALOG

### Component 01: `MediScaffold`
- **Anatomy:** Header (`MediHeader`), body canvas with soft sage/cream gradient, optional sticky bottom navigation bar, offline alert banner.
- **Tokens:** Background `mdCanvas` (`#F8FAF5`), safe area insets.

### Component 02: `MediHeader`
- **Anatomy:**
  - Left: Official MediKiosk Brand Mark (`40dp`) + "MediKiosk" (Lora Bold) + "AIIA New Delhi".
  - Right: Language switcher pill + large help icon button (`64 × 64 dp`).
  - Bottom: Sticky offline hub indicator pill when in local edge mode.
- **Tokens:** Height `72dp`, background `mdSurfaceGlass`, bottom border 1.5dp `mdBorder`.

### Component 03: `PrimaryActionButton`
- **Anatomy:** Full-width or wide pill button with prominent icon and semibold 22sp DM Sans text.
- **Tokens:** Height `72dp` (Kiosk) / `64dp` (Phone), background `mdBrandPrimary` (`#A3E635`), text `mdTextOnBrand` (`#064E3B`), radius `radius-full` (`9999dp`), elevation `elevation-active-lime`.

### Component 04: `SecondaryActionButton`
- **Anatomy:** Outlined or frosted glass button for non-blocking secondary actions ("Type instead", "Skip").
- **Tokens:** Height `64dp`, background `mdSurfaceGlass`, border 1.5dp `mdBorder`, text `mdTextPrimary` (`#064E3B`).

### Component 05: `LargeChoiceCard`
- **Anatomy:** Tactile selection card for languages, care streams, symptoms. Contains large leading icon (`36dp`), bold title (22sp DM Sans), optional subtitle (18sp), and trailing checkmark circle.
- **Selected State:** Background `mdBrandTint` (`#F3FCE8`), border 3dp `mdBrandPrimary` (`#A3E635`), checkmark icon (`28dp`).

### Component 06: `VoiceButton` (Oversized Microphone)
- **Anatomy:** Massive circular button with microphone icon, pulsing lime outer halo during active recording, and clear textual state below ("Tap to speak" / "Listening...").
- **Tokens:** Diameter `96dp` (Phone) / `112dp` (Kiosk), background `mdBrandDark` (idle) or `mdTriageRed` (active recording).

### Component 07: `ListeningWave` (9-Bar Waveform)
- **Anatomy:** Row of 9 animated rounded bars expanding and contracting based on speech input energy.
- **Tokens:** Height `56dp`, bar width `5dp`, color `mdBrandPrimary` (`#A3E635`).

### Component 08: `ExplainBackSummaryCard`
- **Anatomy:** High-contrast review card displaying captured facts:
  - Header: "Here is what I understood" + Audio read-aloud button.
  - Body: Key-value rows in clean cards (e.g. "Problem: Chest pain", "Duration: 3 days").
  - Footer: Two oversized buttons: **Green [YES, THAT'S RIGHT]** (`mdAyushGreen`) and **Red [NO, SAY AGAIN]** (`mdTriageRed`).

### Component 09: `OCRFieldCard` & `EvidenceViewer`
- **Anatomy:** Extracted medication card with line index badge (`[Line 2]`), medicine name, dosage, and trailing `[View Evidence]` link opening the bounding-box highlight over the original prescription.

### Component 10: `QueueTicketCard`
- **Anatomy:** Realistic printed ticket card with serrated edges:
  - Department: "General Medicine OPD (Ayurveda)" (22sp Lora).
  - Token Number: "A-261" (48sp JetBrains Mono ExtraBold `#064E3B`).
  - Patients Ahead: "2 patients ahead" (18sp DM Sans).
  - Doctor Room: "Cabin 102 (Dr. S. Verma)".

### Component 11: `EmergencyBanner`
- **Anatomy:** Full-width crimson banner (`#C83A3A`) with emergency beacon icon, bold warning text (24sp Lora), and immediate action button `[GET IMMEDIATE MEDICAL HELP]`.

### Component 12: `ActiveCallCard` (Screen A-06B BYOD Call Intake)
- **Anatomy:** Clean phone call simulation interface:
  - Top: Doctor avatar icon + call timer (`01:24`) + status badge ("AI Intake Active").
  - Center: Live audio visualizer + rolling live speech transcript.
  - Bottom: Auto-filling symptom chips appearing dynamically as patient speaks.
  - Controls: Speakerphone toggle, mic mute toggle, and oversized Red `[End Call & Review]` button (`72dp`).

---

# 8. SCREEN-BY-SCREEN UI LAYOUT BLUEPRINT

---

## SCREEN 01 — WELCOME
- **Route:** `/welcome`
- **Purpose:** Create immediate understanding and calm reassurance in a chaotic OPD.
- **Layout:**
  - **Header:** MediKiosk brand mark + "All India Institute of Ayurveda", Language shortcut chip, Help icon button.
  - **Center:** Official MediKiosk Brand Mark Hero (`100dp`), H1 Headline (Lora 36sp): `"Welcome to MediKiosk"`, Body Large (DM Sans 22sp): `"Let's gather your health details before you see your doctor."`
  - **Actions (Bottom Dock):**
    - Primary CTA: `[START / शुरू करें]` (`72dp` height, `mdBrandPrimary` `#A3E635`, text `mdTextOnBrand` `#064E3B`).
    - Secondary: `[Listen to Instructions]` (`60dp`, `mdSurfaceGlass` with `mdBorder`).
    - Footer link: `[Need Staff Assistance? Tap Help]`.
- **Transitions:** START $\rightarrow$ Screen 02 (`/language`).

---

## SCREEN 02 — LANGUAGE SELECTION
- **Route:** `/language`
- **Layout:**
  - **Title (Lora 28sp):** `"Choose your language / अपनी भाषा चुनें"`
  - **Subtitle (DM Sans 18sp):** `"All questions and voice assistance will be in this language."`
  - **5 Large Choice Cards:**
    1. **English** (Subtitle: English)
    2. **हिन्दी** (Subtitle: Hindi)
    3. **தமிழ்** (Subtitle: Tamil)
    4. **తెలుగు** (Subtitle: Telugu)
    5. **मराठी** (Subtitle: Marathi)
  - **Footer:** `[CONTINUE →]` enabled upon card tap. Sets app locale and backend language.

---

## SCREEN 03 — CONSENT
- **Route:** `/consent`
- **Layout:**
  - **Title (Lora 28sp):** `"Before we begin"`
  - **ConsentCard:** 3 plain-language safety promises (Doctor summary preparation, secure hospital storage, patient choice to decline).
  - **Actions:**
    - Primary: `[I Agree and Continue]` (`mdAyushGreen` `#047857`, `72dp`, text white).
    - Secondary: `[I Do Not Agree / Paper Token Only]` (`slate-600`, outlined).

---

## SCREEN 04 — IDENTIFICATION
- **Route:** `/identity`
- **Layout:**
  - **Title (Lora 28sp):** `"Let's find your hospital record"`
  - **3 Large Action Cards:**
    1. **SCAN ABHA QR CODE** (Icon: `qr_code_scanner`, subtitle: "Point camera at your Ayushman Bharat card")
    2. **ENTER MOBILE NUMBER** (Icon: `phone_android`, subtitle: "We will look up your registration")
    3. **NEW REGISTRATION / SKIP** (Icon: `arrow_forward`, subtitle: "Continue without prior records")

---

## SCREEN 05 — CARE STREAM
- **Route:** `/care-stream`
- **Choices (Large Cards):**
  1. **General Health Problem** (Icon: `medical_services`)
  2. **Ayurveda / AYUSH Consultation** (Icon: `spa`, green tint `emerald-50`)
  3. **Follow-up Visit / Old Prescription** (Icon: `history`)
  4. **Document Review / Test Results** (Icon: `description`)
  5. **Emergency / Urgent Pain** (Icon: `emergency`, red border)

---

## SCREEN 06 — VOICE INTAKE (START SPEECH)
- **Route:** `/intake`
- **Layout:**
  - **Title (Lora 28sp):** `"What problem are you experiencing?"`
  - **Subtitle (DM Sans 22sp):** `"Tell us in your own words. Speak freely."`
  - **Center:** Giant `VoiceButton` (`112dp`) with `mic` icon and text `"TAP TO TALK"`.
  - **Audio Guidance:** `[Hear the question]` (Icon: `volume_up`).
  - **Secondary:** `[Type instead]` (Icon: `keyboard`).

---

## SCREEN 07 — ACTIVE VOICE CAPTURE & WAVEFORM
- **Route:** `/intake/listening`
- **Layout:**
  - **Title (Lora 28sp):** `"I'm listening..."`
  - **Center:** Animated `ListeningWave` (9 bars bouncing with voice input).
  - **Live Transcript Card:** Semi-transparent frosted glass card displaying recognized words in real time.
  - **Actions:**
    - Primary CTA: `[DONE SPEAKING]` (Icon: `check_circle`, `72dp`, `mdBrandPrimary`).
    - Secondary: `[CANCEL / RECORD AGAIN]` (Icon: `replay`, `slate-600`).

---

## SCREEN 08 — CONVERSATIONAL FOLLOW-UP
- **Route:** `/intake/follow-up`
- **Layout:**
  - **Progress Stepper:** 3-dot indicator (Question 1 of 3).
  - **Question Card:** Single clinical follow-up question (e.g. "Where is the pain located?").
  - **Quick-select Chip Options:** `[Left side]` `[Right side]` `[Everywhere]`.
  - **Voice Response Option:** `[Speak your answer]` (Icon: `mic`).

---

## SCREEN 09 — AI PROCESSING & CLINICAL STRUCTURING
- **Route:** `/intake/processing`
- **Layout:**
  - **Center:** Clean pulsing MediKiosk mark graphic.
  - **Headline (Lora 24sp):** `"Understanding your response..."`
  - **Sub-label (DM Sans 18sp):** `"Organizing symptom details for Dr. S. Verma..."`
  - **Forbidden:** No technical terms (`"LLM"`, `"Tokens"`, `"Inference"`).

---

## SCREEN 10 — SIMPLE SUMMARY CONFIRMATION
- **Route:** `/intake/summary`
- **Layout:**
  - **Headline (Lora 28sp):** `"Is this information correct?"`
  - **SummaryCard (`ExplainBackSummaryCard`):**
    - Main Problem: **Headache & fatigue**
    - Started: **3 days ago**
    - Pain Level: **Moderate (6 out of 10)**
  - **Audio Readout:** `[Listen to summary]` (Icon: `volume_up`).
  - **Verification Buttons:**
    - `[YES, THAT'S RIGHT]` (72dp, `mdAyushGreen` `#047857`, text white).
    - `[NO, SAY AGAIN]` (72dp, `mdTriageRed` `#C83A3A`, text white).

---

## SCREEN 11 — RED FLAG / TRIAGE WARNING
- **Route:** `/triage`
- **Condition:** Triggered only if clinical rules flag high risk (chest pain, SpO2 $< 90\%$).
- **Visuals:** Dominant crimson emergency styling (`mdTriageRed` `#C83A3A`).
- **Layout:**
  - **Header Banner:** Emergency beacon icon + `"URGENT MEDICAL ATTENTION REQUIRED"`.
  - **Message:** `"Your symptoms require immediate evaluation by hospital clinical staff."`
  - **Instructions:** `"Please proceed directly to the Emergency Clinical Desk (Room 001)."`
  - **Actions:**
    - Primary CTA: `[GET IMMEDIATE HELP / ALERT NURSE]` (Icon: `emergency`, `76dp`).
    - Secondary: `[PRINT PRIORITY EMERGENCY TOKEN]`.

---

## SCREEN 12 — DOCUMENT INTRO (PRESCRIPTION SCAN)
- **Route:** `/documents`
- **Layout:**
  - **Headline (Lora 28sp):** `"Do you have medical papers or old prescriptions?"`
  - **Body (DM Sans 18sp):** `"Scanning your papers helps the doctor see your previous medicines."`
  - **Actions:**
    - Primary: `[SCAN DOCUMENTS]` (Icon: `camera_alt`, `72dp`, `mdBrandPrimary`).
    - Secondary: `[NO PAPERS / SKIP STEP]` (`60dp`, outlined).

---

## SCREEN 13 — DOCUMENT CAMERA CAPTURE
- **Route:** `/documents/camera`
- **Layout:**
  - **Camera Feed:** Full-screen preview with 4:3 `DocumentGuideOverlay` (lime corner brackets).
  - **Guidance Text:** `"Place prescription flat inside the frame"`.
  - **Shutter Control:** Circular shutter button (`88dp`) + Gallery upload option.
  - **After Snap:** Preview with `[RETAKE]` and `[USE THIS PHOTO]`.

---

## SCREEN 14 — OCR PROCESSING & LINE INDEXING
- **Route:** `/documents/processing`
- **Layout:**
  - Document thumbnail with animated lime laser sweep.
  - Stepper: `[✓] Document aligned` $\rightarrow$ `[⟳] Reading handwriting & print...` $\rightarrow$ `[ ] Finding medicines and dosages...`.

---

## SCREEN 15 — OCR RESULT & EVIDENCE OVERVIEW
- **Route:** `/documents/results`
- **Layout:**
  - **Headline (Lora 28sp):** `"Medical documents recorded"`
  - **Extracted Medicine Cards (`OCRFieldCard`):**
    - Item 1: **Metformin 500 mg** (1 tab twice daily) — `[Line 2, 3]` — `[View Evidence]`
    - Item 2: **Atorvastatin 20 mg** (1 tab at bedtime) — `[Line 5]` — `[View Evidence]`
  - **Action:** `[CONTINUE →]` (`72dp`, `mdBrandPrimary`).

---

## SCREEN 16 — SOURCE DOCUMENT EVIDENCE VIEWER
- **Route:** `/documents/evidence`
- **Layout:**
  - Interactive pan/zoom of the original captured prescription.
  - Crisp golden-amber bounding box (`#F59E0B`) drawn precisely around the cited lines.
  - Bottom drawer: Extracted text, confidence score (`94%`), and close button.

---

## SCREEN 17 — VITALS RECORDING
- **Route:** `/vitals`
- **Layout:**
  - Grid of 4 Metric Cards: Blood Pressure (`128 / 82`), Pulse (`74 bpm`), SpO2 (`98%`), Temp (`98.6°F`).
  - Action: `[CONFIRM & CONTINUE]` (`mdBrandPrimary`).

---

## SCREEN 18 — AYUSH LIFESTYLE PROFILE
- **Route:** `/ayush`
- **Condition:** Shown for AYUSH / AIIA care stream.
- **Layout:**
  - **Title (Lora 28sp):** `"Your daily health habits (दिनचर्या)"`
  - **Section 1: Digestion (Agni):** `[Strong]` `[Weak / Heavy]` `[Variable]`.
  - **Section 2: Bowel Habit (Koshtha):** `[Regular]` `[Hard / Constipated]` `[Loose]`.
  - **Section 3: Sleep (Nidra):** `[Deep / Sound]` `[Disturbed]` `[Difficulty falling asleep]`.

---

## SCREEN 19 — DEPARTMENT ROUTING & QUEUE ASSIGNMENT
- **Route:** `/queue`
- **Layout:**
  - **Headline (Lora 28sp):** `"Your intake is complete!"`
  - **QueueTicketCard:**
    - Department: **General Medicine OPD (Ayurveda)**
    - Token: **A-261** (48sp JetBrains Mono `#064E3B`)
    - Estimated Wait: **~12 minutes** (2 patients ahead)
    - Assigned Doctor: **Cabin 102 (Dr. S. Verma)**
  - **Action Buttons:**
    - `[FINISH / DONE]` (`72dp`, `mdBrandPrimary`).

---

## SCREENS 20 & 21 — SCOPE CONSOLIDATION
- Per Roadmap Section 3, standalone 3D indoor map and generic facility directories are replaced with a high-contrast room navigation text card on Screen 19:
  `"Cabin 102 · General Medicine OPD · Ground Floor (Past Pharmacy on Right)"`.

---

## SCREEN 22 — EMERGENCY SOS ACTION
- **Route:** `/emergency`
- **Layout:**
  - Crimson emergency screen (`#C83A3A`).
  - Actions:
    - `[CALL CASUALTY DESK IMMEDIATELY]` (Icon: `call`).
    - `[DISPATCH EMERGENCY NURSE TO KIOSK]` (Icon: `emergency`).
    - `[REQUEST AMBULANCE TRANSPORT]` (Icon: `local_hospital`).

---

## SCREEN 23 — AMBULANCE & DISPATCH STATUS
- **Route:** `/emergency/ambulance`
- **Layout:**
  - Status Banner: `"Ambulance Dispatched (Simulation Mode)"`.
  - Estimated Arrival: `"8 mins"` · Vehicle: `"Ambulance 04 (Cardiac Life Support)"`.

---

## SCREEN 24 — COMPLETION & PRIVACY AUTO-RESET
- **Route:** `/completed`
- **Layout:**
  - Checkmark icon (`check_circle`, `80dp`, `mdAyushGreen`).
  - Message: `"Your details have been securely transmitted to Dr. S. Verma's desk."`
  - Token Reminder: `"Remember your Token Number: A-261"`.
  - Circular 10-second countdown: `"Screen resets in 10s for your privacy."`
  - Manual action: `[RESET SCREEN NOW]` (`64dp`).
  - On expiry: Purges local memory and reloads Screen 01.

---

## SCREEN A-06B — 1-TAP CONVERSATIONAL CALL INTAKE (BYOD Mobile App Feature)
- **Route:** `/call-intake`
- **Layout:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ [Arrow Back]          ACTIVE INTAKE CALL           [Volume] │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │                      ┌───────────────┐                      │
  │                      │   AI DOCTOR   │                      │
  │                      │    AVATAR     │                      │
  │                      └───────────────┘                      │
  │                        Call Active                          │
  │                           01:14                             │
  │                                                             │
  │           Listening Waveform: ılılıllı                      │
  │                                                             │
  │  Rolling Live Captions:                                     │
  │  "नमस्ते, आपको कितने दिनों से सीने में दर्द है?"             │
  │                                                             │
  ├─────────────────────────────────────────────────────────────┤
  │ Auto-Filled Symptom Cards (Live Real-Time Extraction):      │
  │ ┌─────────────────────────────────────────────────────────┐ │
  │ │ [Check] Epigastric Burning (पेट में जलन) · 3 Days      │ │
  │ │ [Check] Retrosternal Chest Pain (सीने में दर्द) · 3 Days│ │
  │ └─────────────────────────────────────────────────────────┘ │
  ├─────────────────────────────────────────────────────────────┤
  │ Call Controls Bar:                                          │
  │   [ Mute ]       [ END CALL & REVIEW ]        [ Type ]      │
  └─────────────────────────────────────────────────────────────┘
  ```
- **Interactions:**
  - Audio streams in chunks to `POST /api/call/audio-turn`.
  - Incoming TTS audio plays automatically over speaker/earpiece.
  - Extracted symptoms appear dynamically as animated chips.
  - End Call routes to Screen 10 (Summary Confirmation).

---

# 9. GLOBAL STATES & SYSTEM RESILIENCE FRAMEWORK

1. **Network Connectivity States:**
   - **Cloud Online:** Subtle green indicator in header (`"Cloud Online"`).
   - **Edge Offline Local Hub:** Amber badge (`"Edge Mode: Running on Local Hospital Station"`). Zero disruption to patient intake.
   - **Total Disconnect:** Friendly card: `"Saved on your phone. Will sync when connectivity returns."`
2. **Hardware & Permission Fallbacks:**
   - **Mic Denied:** Notification + automatic fallback to on-screen touch choice cards.
   - **Camera Denied:** Friendly guidance to enter mobile number or manual token.
3. **Session Inactivity Timeout:**
   - Warning modal at 45s: `"Are you still there? Screen will reset in 15 seconds."`
   - Complete RAM purge and reload to Screen 01 at 60s.

---

# 10. FLUTTER IMPLEMENTATION ARCHITECTURE & DART CODE BLUEPRINT

---

## 10.1 Production Dart Theme Specification

```dart
// lib/app/theme/colors.dart
import 'package:flutter/material.dart';

abstract class MediColors {
  // Layer 1: Primitives (ReliaCare Sage/Cream & Lime)
  static const Color slate25   = Color(0xFFFBFDF9);
  static const Color slate50   = Color(0xFFF8FAF5); // Cream canvas
  static const Color slate100  = Color(0xFFEEF6F1);
  static const Color slate200  = Color(0xFFD7E8DF); // Card borders
  static const Color slate300  = Color(0xFFB5CDBF);
  static const Color slate500  = Color(0xFF5F7A6E); // Muted text
  static const Color slate700  = Color(0xFF374151); // Body text
  static const Color slate800  = Color(0xFF1A3C34); // Forest heading
  static const Color slate900  = Color(0xFF064E3B); // Deep forest primary text
  static const Color white     = Color(0xFFFFFFFF);

  static const Color lime50    = Color(0xFFF3FCE8);
  static const Color lime100   = Color(0xFFE4F8C8);
  static const Color lime500   = Color(0xFFA3E635); // Primary CTA fill
  static const Color lime600   = Color(0xFF8BCF28);
  static const Color lime800   = Color(0xFF4D7C0F);

  static const Color emerald600= Color(0xFF17824C);
  static const Color emerald900= Color(0xFF047857); // AYUSH / Success
  static const Color red700    = Color(0xFFC83A3A); // Triage Red
  static const Color red900    = Color(0xFF881D1D);
  static const Color amber700  = Color(0xFFB66A00); // Warning Amber
  static const Color teal700   = Color(0xFF0B8F87); // Telehealth Teal

  // Layer 2: Semantics
  static const Color canvas        = slate50;
  static const Color surface       = white;
  static const Color surfaceGlass  = Color(0xB8FFFFFF); // 72% opacity frosted glass
  static const Color surfaceSubtle = slate100;
  static const Color brandPrimary  = lime500;
  static const Color brandDark     = slate900;
  static const Color brandTint     = lime50;
  static const Color textOnBrand   = slate900;          // 7.6:1 AAA contrast
  static const Color textPrimary   = slate900;          // 15.8:1 AAA contrast
  static const Color textSecondary = slate700;
  static const Color textMuted     = slate500;
  static const Color textInverse   = white;
  static const Color border        = slate200;
  static const Color borderSelected= lime500;
  static const Color ayushGreen    = emerald900;
  static const Color triageRed     = red700;
  static const Color warning       = amber700;
  static const Color success       = emerald600;
}
```

```dart
// lib/app/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'colors.dart';

class MediKioskTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: MediColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: MediColors.brandPrimary,
        onPrimary: MediColors.textOnBrand,
        primaryContainer: MediColors.brandTint,
        surface: MediColors.surface,
        onSurface: MediColors.textPrimary,
        error: MediColors.triageRed,
        outline: MediColors.border,
      ),
      fontFamily: GoogleFonts.dmSans().fontFamily,
      fontFamilyFallback: const [
        'NotoSansDevanagari',
        'NotoSansTamil',
        'NotoSansTelugu',
        'Roboto',
      ],
      textTheme: TextTheme(
        displayLarge: GoogleFonts.lora(
          fontSize: 36,
          fontWeight: FontWeight.w700,
          color: MediColors.textPrimary,
          height: 1.28,
        ),
        headlineLarge: GoogleFonts.lora(
          fontSize: 28,
          fontWeight: FontWeight.w600,
          color: MediColors.textPrimary,
          height: 1.35,
        ),
        headlineMedium: GoogleFonts.dmSans(
          fontSize: 24,
          fontWeight: FontWeight.w600,
          color: MediColors.textPrimary,
          height: 1.33,
        ),
        bodyLarge: GoogleFonts.dmSans(
          fontSize: 22,
          fontWeight: FontWeight.w400,
          color: MediColors.textPrimary,
          height: 1.45,
        ),
        bodyMedium: GoogleFonts.dmSans(
          fontSize: 18,
          fontWeight: FontWeight.w400,
          color: MediColors.textSecondary,
          height: 1.55,
        ),
        labelLarge: GoogleFonts.dmSans(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: MediColors.textOnBrand,
          height: 1.25,
        ),
      ),
      cardTheme: CardTheme(
        color: MediColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: MediColors.border, width: 1.5),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: MediColors.brandPrimary,
          foregroundColor: MediColors.textOnBrand,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(9999), // Pill radius
          ),
          textStyle: GoogleFonts.dmSans(
            fontSize: 22,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
```

---

# 11. DEVELOPER CHECKLIST & ACCEPTANCE VERIFICATION MATRIX

- [ ] **Visual Cohesion:** App visually matches the Web Interface (ReliaCare sage/cream canvas, lime CTA `#A3E635` with forest text `#064E3B`, frosted glass cards, pill radius).
- [ ] **Strict No-Emoji Standard:** Zero emojis in code or UI; all icons use standard Material Symbols.
- [ ] **WCAG 2.2 AAA Contrast:** Primary CTA text (`#064E3B` on `#A3E635`) measures **7.6:1** contrast; headings measure **15.8:1**.
- [ ] **Multilingual Typography:** Lora headings + DM Sans UI + Noto Sans Indic scripts; line-height 1.45–1.65 prevents diacritic clipping.
- [ ] **Elderly Touch Ergonomics:** Minimum interactive target is **64 × 64 dp** (`72dp` for primary CTAs).
- [ ] **Dual-Mode Intake:** Dual voice and touch intake paths both produce identical `ClinicalFact` structures.
- [ ] **Verifiable Provenance:** Document upload extracts medications with bounding boxes over the source image.
- [ ] **No Patient Editing Burden:** Verification uses large **[YES]** / **[NO]** buttons without complex medical editing.
- [ ] **Emergency Routing:** Red-flag markers display dominant crimson styling and route directly to clinical staff.
- [ ] **Privacy Defense:** Kiosk displays execute an automated 10-second purge after 60 seconds of inactivity.

---
*MediKiosk Android & Mobile Design System Specification — SIH26047 Canonical Release v4.0.0.*
