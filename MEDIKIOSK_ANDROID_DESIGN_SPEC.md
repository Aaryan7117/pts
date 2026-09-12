# MediKiosk — Android & Mobile Kiosk Design System Specification
## Canonical UI/UX Design System, Component Catalog & Screen Blueprint
**Document Version:** 3.0.0 (SIH26047 Production Specification)  
**Target Clients:** Android Mobile (BYOD Patient App), Android Tablet / Kiosk (1280 × 800 Landscape)  
**Primary Users:** OPD Patients (Elderly 68+ yrs, Rural, Low-Literacy, 5 Indian Languages) & Clinical Attendants  
**Source Prompt:** `MEDIKIOSK_FLUTTER_UI_MASTER_PROMPT.md` & `MediKiosk_Android_Two_Developer_Execution_Plan.md`

---

## Table of Contents
1. [Design Philosophy & Foundational Rules](#1-design-philosophy--foundational-rules)
2. [Three-Layer Design Token Architecture](#2-three-layer-design-token-architecture)
   - [2.1 Primitive Tokens (Layer 1)](#21-primitive-tokens-layer-1)
   - [2.2 Semantic Tokens (Layer 2)](#22-semantic-tokens-layer-2)
   - [2.3 Component Tokens (Layer 3)](#23-component-tokens-layer-3)
   - [2.4 Contrast & Accessibility Matrix (WCAG AAA)](#24-contrast--accessibility-matrix-wcag-aaa)
3. [Typography & Multilingual Script Architecture](#3-typography--multilingual-script-architecture)
   - [3.1 Font Families & Script Fallbacks](#31-font-families--script-fallbacks)
   - [3.2 Scale, Weights & Metrics](#32-scale-weights--metrics)
   - [3.3 Diacritic Clearance & Text Scaling Protection](#33-diacritic-clearance--text-scaling-protection)
4. [Ergonomics, Responsive Layout & Grid System](#4-ergonomics-responsive-layout--grid-system)
   - [4.1 Breakpoint Strategy & Target Displays](#41-breakpoint-strategy--target-displays)
   - [4.2 Touch Targets & Elderly Thumb Zones](#42-touch-targets--elderly-thumb-zones)
   - [4.3 Spacing Scale & Layout Constraints](#43-spacing-scale--layout-constraints)
5. [Iconography & Brand Geometry](#5-iconography--brand-geometry)
   - [5.1 Material Symbols Canonical Mapping](#51-material-symbols-canonical-mapping)
   - [5.2 MediKiosk Medical Cross Mark Spec](#52-medikiosk-medical-cross-mark-spec)
6. [Motion Choreography & Audio Feedback](#6-motion-choreography--audio-feedback)
   - [6.1 Curves & Timing Tokens](#61-curves--timing-tokens)
   - [6.2 Signature Micro-Interactions (Mic Halo, Waveform, Camera Laser)](#62-signature-micro-interactions)
   - [6.3 Audio Cues (Earcons & TTS Readback)](#63-audio-cues)
7. [Comprehensive Component Catalog (29 Production Components)](#7-comprehensive-component-catalog)
8. [Screen-by-Screen UI Layout Blueprint (Screens 01 to 24 + A-06B)](#8-screen-by-screen-ui-layout-blueprint)
9. [Global States & System Resilience Framework](#9-global-states--system-resilience-framework)
10. [Flutter Implementation Architecture & Code Blueprint](#10-flutter-implementation-architecture--code-blueprint)

---

# 1. DESIGN PHILOSOPHY & FOUNDATIONAL RULES

MediKiosk is deployed in high-stress, noisy government hospital outpatient departments (OPDs) where patients wait 45–90 minutes for a 2-minute doctor consultation. The design system must solve the **first-mile barrier** for rural and elderly patients who may have never touched a tablet or smartphone.

### Core Principles:
1. **Calm Healthcare Dignity:** Clean, trustworthy, hospital-grade aesthetic. Zero gimmicky glassmorphism, zero distracting saturated gradients, zero decorative particle effects.
2. **Extreme Cognitive Simplicity:** One primary task per screen. No multi-field diagnostic questionnaires. Information is presented in plain conversational language, not medical jargon (e.g., *"Pain in stomach"* instead of *"Epigastric tenderness"*).
3. **Voice-First & Closed-Loop Verification:** Patients speak naturally in their mother tongue; the interface reflects back what it understood using massive tactile cards and synthetic speech readback (Closed-Loop Explain-Back).
4. **No Patient Clinical Editing Burden:** Patients confirm or deny statements using simple **[YES]** / **[NO]** buttons. They are never forced to edit dosage numbers, clinical codes, or prescription OCR line indices.
5. **No Receipt, No Fact (Verifiable Provenance):** Any extracted medication or lab fact is linked to a visual bounding box on the original scanned prescription.
6. **Self-Sufficient Offline Resilience:** Interface visibly adapts when internet fails, falling back smoothly to local edge intelligence without breaking or showing unhandled exceptions.

---

# 2. THREE-LAYER DESIGN TOKEN ARCHITECTURE

The design tokens follow a strict 3-tier system: **Primitive (Raw Values) $\rightarrow$ Semantic (Intent/Role) $\rightarrow$ Component (Scoped).**

```
┌────────────────────────────────────────────────────────┐
│  LAYER 1: PRIMITIVE TOKENS (Raw Hex, DP, Durations)    │
│  mdColorBlue900 (#1E3A8A), mdSpace16 (16dp), etc.      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: SEMANTIC TOKENS (Intent & Context)           │
│  mdBrandPrimary, mdSurface, mdTextMuted, mdTriageRed   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 3: COMPONENT TOKENS (Widget-Scoped)             │
│  choiceCardBg, voiceBtnHalo, triageBannerBorder        │
└────────────────────────────────────────────────────────┘
```

---

## 2.1 Primitive Tokens (Layer 1)

### A. Raw Color Palette
```text
/* Slate Neutrals */
slate-50:    #F8FAFC    /* mdCanvas (Base screen background) */
slate-100:   #F1F5F9    /* mdSurfaceSubtle (Card hover / input bg) */
slate-200:   #E2E8F0    /* mdBorder (Card borders, dividers) */
slate-400:   #94A3B8    /* mdBorderStrong / Disabled text */
slate-600:   #475569    /* mdTextMuted (Secondary descriptions) */
slate-800:   #1E293B    /* mdTextPrimaryDark */
slate-900:   #0F172A    /* mdBrandDark (Headings, primary typography) */
white:       #FFFFFF    /* mdSurface (Card backgrounds, modals) */

/* Healthcare Navy & Primary */
blue-50:     #EFF6FF    /* mdBrandTint (Selected card background) */
blue-100:    #DBEAFE    /* mdBrandTintBorder */
blue-600:    #2563EB    /* mdBrandInteractive */
blue-800:    #1E3A8A    /* mdBrandPrimary (Dominant CTA, Header brand) */
blue-900:    #172554    /* mdBrandDarkNavy */

/* Clinical AYUSH Forest Green */
emerald-50:  #ECFDF5    /* mdAyushTint */
emerald-700: #047857    /* mdSuccessInteractive */
emerald-800: #065F46    /* mdAyushGreen (Safe state, AYUSH branding) */
emerald-900: #064E3B    /* mdSuccessText */

/* Triage Red & Warning Amber */
red-50:      #FEF2F2    /* mdTriageTint */
red-600:     #DC2626    /* mdTriageRedInteractive */
red-800:     #991B1B    /* mdTriageRed (Red Flag Emergency Banner) */
red-900:     #7F1D1D    /* mdTriageDarkText */

amber-50:    #FFFBEB    /* mdWarningTint */
amber-600:   #D97706    /* mdWarningInteractive */
amber-800:   #92400E    /* mdWarning (Clinical gap, missing document) */
```

### B. Spacing Scale (4dp / 8dp Base System)
```text
space-2:     2dp     /* Micro border offsets */
space-4:     4dp     /* Tight icon-text padding */
space-8:     8dp     /* Compact element spacing */
space-12:    12dp    /* Inner chip padding, badge inset */
space-16:    16dp    /* Standard card internal padding (Phone) */
space-20:    20dp    /* Medium button horizontal padding */
space-24:    24dp    /* Standard screen edge margin (Phone) / Card padding (Tablet) */
space-32:    32dp    /* Section vertical separation */
space-40:    40dp    /* Kiosk screen margin */
space-48:    48dp    /* Major grouping separation */
space-64:    64dp    /* Large CTA vertical margin */
space-80:    80dp    /* Hero spacing */
```

### C. Border Radius Scale
```text
radius-none: 0dp     /* Full bleed containers */
radius-sm:   6dp     /* Small chips, evidence tags */
radius-md:   12dp    /* Text inputs, secondary action buttons */
radius-lg:   16dp    /* Cards, modal dialogs, choices */
radius-xl:   24dp    /* Primary intake cards, oversized buttons */
radius-full: 999dp   /* Circular buttons, mic triggers, pills */
```

### D. Shadow & Elevation Scale
MediKiosk avoids heavy, dirty shadows. Shadows are crisp, low-blur, and tinted with `slate-900` at low opacity to maintain clinical hygiene:
```text
elevation-0: None
elevation-1: Offset(0, 2), Blur: 4,  Color: rgba(15, 23, 42, 0.05)  /* Static cards */
elevation-2: Offset(0, 4), Blur: 8,  Color: rgba(15, 23, 42, 0.08)  /* Interactive cards, hover */
elevation-3: Offset(0, 8), Blur: 16, Color: rgba(15, 23, 42, 0.12)  /* Modals, Sticky footers */
elevation-4: Offset(0, 12), Blur: 24, Color: rgba(30, 58, 138, 0.18) /* Active voice button glow */
```

---

## 2.2 Semantic Tokens (Layer 2)

| Token Name | Hex Code | Material 3 Mapping | Semantic Role & Intent |
|---|---|---|---|
| `mdCanvas` | `#F8FAFC` | `colorScheme.surface` | Base app background (cool sterile grey) |
| `mdSurface` | `#FFFFFF` | `colorScheme.surfaceContainer` | White card background, modals, dialogs |
| `mdSurfaceSubtle` | `#F1F5F9` | `colorScheme.surfaceContainerHigh` | Disabled states, unselected radio pills |
| `mdBrandPrimary` | `#1E3A8A` | `colorScheme.primary` | Dominant healthcare action, active steps |
| `mdBrandDark` | `#0F172A` | `colorScheme.onSurface` | Primary typography, headers, high contrast |
| `mdBrandTint` | `#EFF6FF` | `colorScheme.primaryContainer` | Selected card tint, subtle brand focus |
| `mdAyushGreen` | `#065F46` | `colorScheme.tertiary` | AYUSH stream, positive confirmation |
| `mdTriageRed` | `#991B1B` | `colorScheme.error` | Red Flag urgent warning, emergency call |
| `mdSuccess` | `#166534` | `colorScheme.outlineVariant` | Confirmed facts, successful OCR line match |
| `mdWarning` | `#92400E` | `colorScheme.errorContainer` | Medication gaps, incomplete documents |
| `mdTextPrimary` | `#0F172A` | `colorScheme.onSurface` | Main headings, question prompts |
| `mdTextMuted` | `#475569` | `colorScheme.onSurfaceVariant` | Subtitles, helper text, explanations |
| `mdTextInverse` | `#FFFFFF` | `colorScheme.onPrimary` | White text on primary buttons / red alerts |
| `mdBorder` | `#E2E8F0` | `colorScheme.outline` | Unselected card border (1.5dp) |
| `mdBorderSelected` | `#1E3A8A` | `colorScheme.primary` | Selected card border (3dp strong) |

---

## 2.3 Component Tokens (Layer 3)

| Component Area | Component Token | Semantic Source Token | Visual Spec |
|---|---|---|---|
| **Large Choice Card** | `choiceCardBg` | `mdSurface` | White with 1.5dp `mdBorder` |
| | `choiceCardBgSelected`| `mdBrandTint` | `#EFF6FF` with 3dp `mdBorderSelected` |
| | `choiceCardTitleColor`| `mdBrandDark` | 22sp Semibold |
| **Voice Button** | `voiceBtnBgIdle` | `mdBrandPrimary` | Circular 88dp, `#1E3A8A` |
| | `voiceBtnBgActive` | `mdTriageRed` | Circular 88dp, `#991B1B` |
| | `voiceBtnHaloColor` | `mdBrandTint` | Expanding 24dp ring, opacity 0.35 |
| **Triage Banner** | `triageBannerBg` | `red-50` | `#FEF2F2` background |
| | `triageBannerBorder`| `mdTriageRed` | 2dp solid `#991B1B` |
| | `triageBannerText` | `red-900` | `#7F1D1D` 24sp Bold |
| **Document Frame** | `cameraGuideBorder` | `mdSurface` | 3dp dashed or solid `#FFFFFF` |
| | `cameraGuideCorner` | `mdBrandPrimary` | 5dp solid corner bracket `#1E3A8A` |
| | `cameraGuideSuccess`| `mdSuccess` | 5dp solid corner bracket `#166534` |
| **Queue Token** | `queueTokenBadgeBg` | `blue-50` | `#EFF6FF` rounded pill |
| | `queueTokenNumber` | `mdBrandPrimary` | 44sp ExtraBold `#1E3A8A` |

---

## 2.4 Contrast & Accessibility Matrix (WCAG AAA)

To accommodate elderly patients suffering from presbyopia, cataracts, and diabetic retinopathy, all text and interactive borders meet or exceed **WCAG 2.2 Level AAA (7:1 for normal text, 4.5:1 for large text)**:

| Foreground Element | Background Canvas | Contrast Ratio | WCAG 2.2 Status |
|---|---|---|---|
| `mdTextPrimary` (`#0F172A`) | `mdSurface` (`#FFFFFF`) | **16.1 : 1** | **PASS AAA** (Exceeds 7.0:1) |
| `mdTextPrimary` (`#0F172A`) | `mdCanvas` (`#F8FAFC`) | **15.4 : 1** | **PASS AAA** |
| `mdTextMuted` (`#475569`) | `mdSurface` (`#FFFFFF`) | **8.3 : 1** | **PASS AAA** |
| `mdBrandPrimary` (`#1E3A8A`) | `mdSurface` (`#FFFFFF`) | **10.7 : 1** | **PASS AAA** |
| `mdTextInverse` (`#FFFFFF`) | `mdBrandPrimary` (`#1E3A8A`) | **10.7 : 1** | **PASS AAA** |
| `mdTextInverse` (`#FFFFFF`) | `mdTriageRed` (`#991B1B`) | **7.4 : 1** | **PASS AAA** |
| `mdTextInverse` (`#FFFFFF`) | `mdAyushGreen` (`#065F46`) | **7.8 : 1** | **PASS AAA** |
| `mdBorderSelected` (`#1E3A8A`) | `mdCanvas` (`#F8FAFC`) | **10.2 : 1** | **PASS AAA** (UI Components) |

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

## 3.1 Font Families & Script Fallbacks

To eliminate font rendering stutter and missing glyphs (tofu boxes), the Flutter typography system declares a robust script fallback chain:

```text
Primary Font Family:    'Inter', 'Roboto', sans-serif
Devanagari Fallback:   'Noto Sans Devanagari', sans-serif
Tamil Fallback:        'Noto Sans Tamil', sans-serif
Telugu Fallback:       'Noto Sans Telugu', sans-serif
```

In Flutter Dart configuration:
```dart
fontFamilyFallback: const [
  'NotoSansDevanagari',
  'NotoSansTamil',
  'NotoSansTelugu',
  'Roboto',
],
```

---

## 3.2 Scale, Weights & Metrics

| Style Token | Size (sp) | Line Height | Weight | Letter Spacing | Target Usage |
|---|---|---|---|---|---|
| `displayLarge` (H1) | 36 sp | 44 dp (1.22) | Bold (700) | -0.5 px | Screen welcome, emergency titles |
| `headlineLarge` (H2) | 28 sp | 36 dp (1.28) | SemiBold (600) | -0.2 px | Main intake questions, token titles |
| `headlineMedium` (H3) | 24 sp | 32 dp (1.33) | SemiBold (600) | 0.0 px | Card headings, section dividers |
| `bodyLarge` | 22 sp | 30 dp (1.36) | Regular (400) / Med (500) | +0.15 px | Choice card subtitles, consent statements |
| `bodyMedium` | 18 sp | 26 dp (1.44) | Regular (400) | +0.25 px | Standard body text, helper guidance |
| `buttonText` | 22–24 sp | 28 dp (1.20) | SemiBold (600) | +0.5 px | Primary CTA actions ([CONTINUE], [START]) |
| `labelSmall` (Caption)| 16 sp | 22 dp (1.37) | Medium (500) | +0.4 px | Timestamps, token sub-labels, metadata |

---

## 3.3 Diacritic Clearance & Text Scaling Protection

1. **Indic Diacritic Preservation:** Complex vowel signs (e.g., Hindi *matras* `ि`, `ी`, `ु`, `ू`, and conjuncts in Marathi/Tamil) often get clipped by default Latin line-height calculations. All text styles enforce a minimum line-height multiplier of **1.35 to 1.45** to ensure full glyph clearance.
2. **Text Scaling Protection:** In `MaterialApp`, `MediaQuery.textScaler` must be clamped between **1.0x and 1.35x**. This allows low-vision users to enjoy magnified text without breaking card layout boundaries or triggering horizontal overflows.

```dart
builder: (context, child) {
  final mediaQuery = MediaQuery.of(context);
  final clampedScaler = mediaQuery.textScaler.clamp(minScaleFactor: 1.0, maxScaleFactor: 1.35);
  return MediaQuery(
    data: mediaQuery.copyWith(textScaler: clampedScaler),
    child: child!,
  );
}
```

---

# 4. ERGONOMICS, RESPONSIVE LAYOUT & GRID SYSTEM

MediKiosk must seamlessly render across two distinct physical form factors:
- **Form Factor A: 1280 × 800 Landscape Tablet / Kiosk Display** (In-Clinic OPD Kiosk)
- **Form Factor B: 360 × 800 to 412 × 915 Portrait Smartphone** (Patient BYOD Mobile App)

---

## 4.1 Breakpoint Strategy & Target Displays

```
┌────────────────────────┬────────────────────────────────────────────────────────┐
│ Breakpoint Class       │ Screen Width Range & Typical Device                     │
├────────────────────────┼────────────────────────────────────────────────────────┤
│ Compact (Phone)        │ width < 600 dp (Android smartphones in portrait)       │
│ Medium (Tablet Port.)  │ 600 dp <= width < 840 dp (Small 7-8" tablets)          │
│ Expanded (Kiosk/Desk)  │ width >= 840 dp (10-12" Landscape Kiosks: 1280 × 800)  │
└────────────────────────┴────────────────────────────────────────────────────────┘
```

### Layout Shift Rules:
- **Phone (Compact):** Single-column vertical layout. Sticky bottom action bar for the primary CTA. Thumb-accessible zone.
- **Kiosk (Expanded — 1280 × 800):** Dual-pane layout:
  - **Left Pane (35% width, ~420dp):** Persistent brand identity, current step indicator, live audio guidance, and doctor assistance status.
  - **Right Pane (65% width, ~800dp):** Interactive card canvas, oversized choice buttons, live waveform, and camera feed.

---

## 4.2 Touch Targets & Elderly Thumb Zones

In an OPD environment, patients with hand tremors, joint stiffness, or thick fingers will touch the screen inaccurately.
- **Absolute Minimum Interactive Target:** `64 × 64 dp` (Surpasses Android 48dp guidelines).
- **Preferred Primary Action Target (Kiosk CTAs):** `72 × 88 dp` (Height $\ge 72$ dp, full width or $\ge 240$ dp).
- **Spacing Between Touch Targets:** Minimum `16 dp` gutter to prevent accidental double-taps.
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
│                           │      │ 🔊 Read Aloud      │ [ Choice Card 2 ]      │
├───────────────────────────┤      │                    │                        │
│ [ PRIMARY ACTION (72dp) ] │      │ Emergency Exit     │ [ CONTINUE CTA (80dp)] │
│ Safe Area Bottom          │      │ [ SOS Help ]       │                        │
└───────────────────────────┘      └────────────────────┴────────────────────────┘
```

---

## 4.3 Spacing Scale & Layout Constraints

- **Max Content Width (Desktop/Tablet):** Center-constrained to `1080 dp` to prevent wide unreadable text scanning.
- **Phone Screen Inset:** `horizontal: 20dp, vertical: 16dp`.
- **Kiosk Screen Inset:** `horizontal: 36dp, vertical: 24dp`.
- **Card Padding:** `20dp` (Phone), `28dp` (Kiosk).

---

# 5. ICONOGRAPHY & BRAND GEOMETRY

MediKiosk relies on clean, high-recognition iconography from **Material Symbols (Rounded)** with a stroke weight of `2.0` (Medium/Fill 0) to ensure high visibility without visual clutter.

---

## 5.1 Material Symbols Canonical Mapping

| Semantic Action | Material Icon Identifier | Codepoint / Enum | Accessibility Label (Screen Reader) |
|---|---|---|---|
| **Welcome / Clinic** | `medical_services_rounded` | `Icons.medical_services_rounded` | "Hospital medical services" |
| **Language Select** | `language_rounded` | `Icons.language_rounded` | "Change interaction language" |
| **Help & Support** | `help_outline_rounded` | `Icons.help_outline_rounded` | "Get assistance from hospital staff" |
| **Consent Verified** | `verified_user_rounded` | `Icons.verified_user_rounded` | "Data privacy and security verified" |
| **Scan ABHA QR** | `qr_code_scanner_rounded` | `Icons.qr_code_scanner_rounded` | "Scan ABHA health ID QR code" |
| **Mobile Number** | `phone_android_rounded` | `Icons.phone_android_rounded` | "Enter mobile phone number" |
| **Skip / Anonymous** | `arrow_forward_rounded` | `Icons.arrow_forward_rounded` | "Continue without registration" |
| **Microphone Idle** | `mic_rounded` | `Icons.mic_rounded` | "Start speaking into microphone" |
| **Microphone Active**| `mic_none_rounded` | `Icons.mic_none_rounded` | "Microphone listening" |
| **Stop Recording** | `stop_circle_rounded` | `Icons.stop_circle_rounded` | "Done speaking, stop recording" |
| **Keyboard / Type** | `keyboard_rounded` | `Icons.keyboard_rounded` | "Switch to typing on keyboard" |
| **Audio Readout** | `volume_up_rounded` | `Icons.volume_up_rounded` | "Listen to instructions read aloud" |
| **Confirm / Yes** | `check_circle_rounded` | `Icons.check_circle_rounded` | "Confirm, this is correct" |
| **Correction / Retry**| `replay_rounded` | `Icons.replay_rounded` | "No, say it again or record again" |
| **Red Flag Emergency**| `emergency_rounded` | `Icons.emergency_rounded` | "Emergency urgent attention needed" |
| **Document Scan** | `document_scanner_rounded`| `Icons.document_scanner_rounded`| "Scan prescription document" |
| **Camera Shutter** | `camera_alt_rounded` | `Icons.camera_alt_rounded` | "Capture photograph of document" |
| **Evidence Link** | `find_in_page_rounded` | `Icons.find_in_page_rounded` | "View original prescription evidence" |
| **Vitals Monitor** | `monitor_heart_rounded` | `Icons.monitor_heart_rounded` | "Medical vitals and sensor readings" |
| **Queue Token** | `confirmation_number_rounded`| `Icons.confirmation_number_rounded`| "Hospital OPD queue token" |
| **Doctor Cabin** | `medical_information_rounded`| `Icons.medical_information_rounded`| "Doctor room and OPD department" |
| **Hospital Map** | `map_rounded` | `Icons.map_rounded` | "Hospital navigation and floor plan" |
| **Ambulance SOS** | `airport_shuttle_rounded` | `Icons.airport_shuttle_rounded` | "Ambulance dispatch status" |
| **Network Offline** | `wifi_off_rounded` | `Icons.wifi_off_rounded` | "Offline local edge mode active" |

---

## 5.2 MediKiosk Medical Cross Mark Spec

The brand symbol is a **Harmonized Rounded Greek Cross** with softened pill geometry and an inner concentric heart glyph:

```text
Geometry Specifications:
- Overall Dimension: 64 × 64 dp (Header), 120 × 120 dp (Welcome Hero)
- Cross Bar Thickness: 28% of overall width
- Corner Radius: 8dp on bar ends
- Primary Color: mdBrandPrimary (#1E3A8A)
- Accent Node: Center junction tinted in mdAyushGreen (#065F46)
- Screen Reader Semantic: "MediKiosk Official Healthcare Symbol"
```

---

# 6. MOTION CHOREOGRAPHY & AUDIO FEEDBACK

Motion in MediKiosk is functional, not decorative. It communicates **state transitions, processing status, and tactile confirmation**.

---

## 6.1 Curves & Timing Tokens

| Duration Token | Milliseconds | Easing Curve | Typical Use Case |
|---|---|---|---|
| `motionImmediate` | 100 ms | `Curves.linear` | Button press state, ink splash |
| `motionFast` | 180 ms | `Curves.easeOutCubic` | Card selection toggle, chip expansion |
| `motionNormal` | 300 ms | `Curves.easeInOutCubic` | Screen push/pop transition, drawer slide |
| `motionSlow` | 500 ms | `Curves.decelerate` | Red Flag alert slide-in, modal entry |
| `motionPulse` | 1200 ms | `Curves.easeInOutSine` | Microphone active listening ring pulse |

> **Accessibility Rule:** If `MediaQuery.disableAnimationsOf(context)` or Android OS "Remove Animations" is enabled, all motion drops to instantaneous `0 ms` opacity swaps.

---

## 6.2 Signature Micro-Interactions

### A. Active Microphone Pulse Halo
When recording speech, an animated double halo expands outward from the mic button:
- **Inner Ring:** Diameter `88dp` to `120dp`, opacity `0.4` $\rightarrow$ `0.0`.
- **Outer Ring:** Diameter `88dp` to `150dp`, opacity `0.2` $\rightarrow$ `0.0`, delayed by `300ms`.
- **Center Button:** Subtle scale pulsation (`1.0` to `1.05`).

### B. Live Audio Waveform Visualizer (Screen 07 & Screen A-06B)
Displays **9 vertical bars** representing simulated or real audio energy:
- **Bar Width:** `6 dp`, **Spacing:** `8 dp`, **Corner Radius:** `3 dp`.
- **Color:** Gradient from `mdBrandPrimary` (`#1E3A8A`) to `blue-400` (`#60A5FA`).
- **Animation:** Continuous height interpolation between `8 dp` (silence) and `56 dp` (peak voice energy) based on microphone amplitude stream.

### C. Document Camera Guide Laser (Screen 13 & 14)
- **Corner Brackets:** `40 × 40 dp` L-shaped solid brackets (`5dp` stroke) at the 4 corners of the 4:3 document frame.
- **Detection State:** Brackets animate from White (`#FFFFFF`) to Forest Green (`mdSuccess` `#166534`) upon document alignment.
- **Scanning Sweep:** During OCR processing (Screen 14), a horizontal glowing green gradient line sweeps vertically from top to bottom (`1500ms` cycle).

---

## 6.3 Audio Cues (Earcons & TTS Readback)

Elderly and illiterate patients receive instant auditory feedback:
- **Chime 1 (Listening Started):** Soft ascending two-tone earcon (`440Hz` $\rightarrow$ `880Hz`, 150ms).
- **Chime 2 (Listening Completed):** Soft descending tone (`880Hz` $\rightarrow$ `440Hz`, 150ms).
- **TTS Question Readback:** Every new question screen offers a prominent **[🔊 Hear Question]** audio action that invokes on-device TTS in the chosen Indian language.

---

# 7. COMPREHENSIVE COMPONENT CATALOG

Every component is modular, theme-driven, contains zero business logic, and exposes strict Dart typed parameters.

---

### Component 01: `MediScaffold`
- **Anatomy:** Top `MediHeader`, flexible body canvas wrapped in `SafeArea` and `LayoutBuilder`, optional sticky bottom navigation bar, offline alert banner.
- **Parameters:**
  ```dart
  Widget body;
  String title;
  bool showHeader;
  bool showEmergencyAction;
  VoidCallback? onHelpPressed;
  ```
- **Responsive Behavior:** On width $< 600$dp, stacks vertically with bottom-docked CTA. On width $\ge 840$dp, applies landscape split or centered max-width constraint (`1080dp`).

---

### Component 02: `MediHeader`
- **Anatomy:**
  - Left: MediKiosk Brand Cross (`36dp`) + "MediKiosk" title + Hospital Subtitle.
  - Right: Language Switcher Dropdown/Chip + Large Help Icon Button (`64 × 64 dp`).
  - Bottom: Optional Offline/Edge-Mode Pill.
- **Tokens:** Height `76dp`, background `mdSurface`, bottom border 1.5dp `mdBorder`.

---

### Component 03: `LanguageSelector`
- **Anatomy:** Compact pill button displaying current language with a globe icon. Tap opens a bottom sheet or modal with large cards for the 5 languages.
- **Touch Target:** `64dp` height.

---

### Component 04: `PrimaryActionButton`
- **Anatomy:** Full-width or wide pill button with prominent icon and semibold 22sp text.
- **Parameters:**
  ```dart
  String label;
  IconData? icon;
  VoidCallback? onPressed;
  bool isLoading;
  bool isFullWidth;
  ```
- **Tokens:** Height `72dp` (Kiosk) / `64dp` (Phone), background `mdBrandPrimary`, text `mdTextInverse`, radius `16dp`, elevation `2`.
- **States:**
  - *Idle:* Deep Navy (`#1E3A8A`).
  - *Pressed:* Scale `0.98`, darker navy (`#172554`).
  - *Disabled:* Background `slate-200`, text `slate-400`.
  - *Loading:* Replaces text with centered white circular progress indicator (`28dp`).

---

### Component 05: `SecondaryActionButton`
- **Anatomy:** Outlined or ghost button for non-blocking secondary actions (e.g., *"Type instead"*, *"Skip"*).
- **Tokens:** Height `64dp`, background `transparent`, border 2dp `mdBorderStrong`, text `mdBrandDark`, radius `16dp`.

---

### Component 06: `LargeChoiceCard`
- **Anatomy:** Tactile rounded card for categorical selection (e.g., Languages, Care Streams, Symptoms). Contains a large leading icon (`40dp`), bold title (22sp), optional explanatory subtitle (18sp), and trailing checkmark.
- **Parameters:**
  ```dart
  String title;
  String? subtitle;
  IconData icon;
  bool isSelected;
  VoidCallback onTap;
  ```
- **Tokens:** Minimum height `88dp`, padding `20dp`, radius `16dp`.
- **Selection State:**
  - *Unselected:* Background `mdSurface`, border 1.5dp `mdBorder`.
  - *Selected:* Background `mdBrandTint` (`#EFF6FF`), border 3dp `mdBrandPrimary` (`#1E3A8A`), trailing blue checkmark icon (`32dp`).

---

### Component 07: `VoiceButton` (Oversized Microphone)
- **Anatomy:** Massive circular button with microphone icon, pulsing outer halo during active recording, and clear textual state below (`"Tap to speak"` / `"Listening..."`).
- **Parameters:**
  ```dart
  bool isListening;
  VoidCallback onTap;
  ```
- **Tokens:** Diameter `96dp` (Phone) / `112dp` (Kiosk), background `mdBrandPrimary` (idle) or `mdTriageRed` (active recording).

---

### Component 08: `ListeningWave` (Waveform Visualizer)
- **Anatomy:** Row of 9 animated rounded bars expanding and contracting based on speech input energy.
- **Tokens:** Height `64dp`, bar width `6dp`, bar color `mdBrandPrimary`.

---

### Component 09: `SummaryCard` & `ExplainBackCard`
- **Anatomy:** High-contrast review card displaying captured facts with plain-language labels and values:
  - Header: *"Here is what I understood"* + Audio read-aloud button.
  - Body: Key-value rows (e.g., *"Problem: Headache"*, *"Duration: 3 days"*, *"Severity: 6/10"*).
  - Footer: Two oversized buttons: **Green [YES, THAT'S RIGHT]** (`mdSuccess`) and **Red [NO, SAY AGAIN]** (`mdTriageRed`).
- **Tokens:** Background `mdSurface`, border 2dp `mdBorder`, radius `20dp`, elevation `2`.

---

### Component 10: `ClinicalFactCard`
- **Anatomy:** Individual fact container displaying concept name, normalized SNOMED code tag, provenance tier tag (e.g., `VOICE`, `OCR`), and confidence indicator.
- **Tokens:** Radius `12dp`, padding `16dp`, background `slate-50`.

---

### Component 11: `ConsentCard`
- **Anatomy:** Simple, non-legalistic privacy card highlighting 3 plain points with check icons:
  1. Why your symptoms are collected (to help the doctor prepare).
  2. How documents are scanned (secure, encrypted storage).
  3. Who sees the information (only authorized hospital medical staff).
- **Actions:** Prominent `[I Agree and Continue]` + secondary `[I Do Not Agree]` + expandable *"Detailed Privacy Policy"*.

---

### Component 12: `DocumentGuideOverlay`
- **Anatomy:** Semi-transparent dark scrim (`rgba(15, 23, 42, 0.65)`) with a clear 4:3 rectangular viewport cutout. Four solid corner brackets (`40 × 40 dp`, `5dp` stroke) frame the document area with dynamic alignment status text (`"ALIGN DOCUMENT INSIDE THE FRAME"`).

---

### Component 13: `OCRFieldCard`
- **Anatomy:** Card representing an extracted medication or lab value with line index badge (e.g., `[Line 2]`), medicine name, dosage, and trailing `[View Evidence]` link.

---

### Component 14: `EvidenceChip` & `BoundingBoxViewer`
- **Anatomy:** Modal or inline viewer showing the captured document photo with a glowing amber/yellow bounding box (`#F59E0B`) drawn around the exact text region cited by the extraction engine.

---

### Component 15: `VitalCard`
- **Anatomy:** Metric card displaying vital type (BP, Pulse, Temp, SpO2), numeric value in huge 36sp font, measurement unit, timestamp, and hardware connection status badge (`"Connected"` vs `"Manual Entry"`).

---

### Component 16: `EmergencyBanner`
- **Anatomy:** Full-width deep crimson banner (`#991B1B`) with flashing emergency beacon icon, bold warning text (24sp), and immediate action button `[GET IMMEDIATE MEDICAL HELP]`.

---

### Component 17: `QueueTicketCard`
- **Anatomy:** Printed-ticket-style visual card with serrated edge styling:
  - Department: *"General Medicine OPD"* (22sp Semibold).
  - Token Number: *"A-402"* (48sp ExtraBold Navy).
  - Patients Ahead: *"3 patients ahead"* (18sp).
  - Doctor Room: *"Cabin 104 (Dr. Sharma)"*.

---

### Component 18: `HospitalServiceCard`
- **Anatomy:** Grid tile with colorful department icon, title (e.g., *"Pharmacy"*, *"Blood Bank"*, *"Toilets"*), distance/floor indicator, and `[Directions]` button.

---

### Component 19: `OfflineBanner`
- **Anatomy:** Sticky header alert strip:
  - *Cloud Online:* Hidden or subtle green dot (`"Connected"`).
  - *Edge Offline:* Amber banner (`#92400E`): `"Running on Local Edge Hub — All services functional without internet"`.

---

### Component 20: `PrivacyResetOverlay`
- **Anatomy:** Full-screen privacy safety dialog triggered on Screen 24 or after 60s inactivity:
  - Title: *"Session Ending for Your Privacy"*
  - Animated 10-second circular countdown timer.
  - Buttons: `[Reset Immediately]` and `[I'm Still Here]`.
  - On zero: Purges all local memory state, resets language, and routes to Screen 01.

---

### Component 21: `ActiveCallCard` (Screen A-06B BYOD Call Intake)
- **Anatomy:** Phone call simulation interface:
  - Top: Doctor/AI Avatar + Call Timer (`01:24`) + Status (`"AI Intake Active"`).
  - Center: Live audio visualizer + rolling live speech transcript.
  - Bottom: Auto-filling symptom chips appearing dynamically as patient speaks.
  - Controls: Speakerphone toggle, Mic mute toggle, and oversized Red `[End Call & Review]` button (`72dp`).

---

# 8. SCREEN-BY-SCREEN UI LAYOUT BLUEPRINT

Every screen from Screen 01 to Screen 24 (+ Screen A-06B) is specified with exact structural layout, typography, components, and transitions.

---

## SCREEN 01 — WELCOME
- **Route:** `/welcome`
- **Purpose:** Create immediate understanding and calm reassurance in a chaotic OPD.
- **Layout (Phone & Kiosk):**
  - **Header:** MediKiosk logo + Hospital Name (`"All India Institute of Ayurveda"`), Language shortcut chip, Help icon.
  - **Center:** Large MediKiosk Medical Cross Hero (`120dp`), H1 Headline: `"Welcome to MediKiosk"`, Body Large: `"Let's gather your health details before you see your doctor."`
  - **Actions (Bottom Dock):**
    - Primary CTA: `[START / शुरू करें]` (`72dp` height, `mdBrandPrimary`).
    - Secondary: `[🔊 Listen to Instructions]` (`60dp`, `mdSurface` with blue border).
    - Footer link: `[Need Staff Assistance? Tap Help]`.
- **Transitions:** START $\rightarrow$ Screen 02 (`/language`).

---

## SCREEN 02 — LANGUAGE SELECTION
- **Route:** `/language`
- **Purpose:** Lock patient interaction language for UI and voice pipelines before speech intake begins.
- **Layout:**
  - **Title:** `"Choose your language / अपनी भाषा चुनें"` (H2 28sp).
  - **Subtitle:** `"All questions and voice assistance will be in this language."`
  - **Grid (2 columns on Kiosk, 1 column on Phone):**
    1. **English** (Subtitle: English)
    2. **हिन्दी** (Subtitle: Hindi)
    3. **தமிழ்** (Subtitle: Tamil)
    4. **తెలుగు** (Subtitle: Telugu)
    5. **मराठी** (Subtitle: Marathi)
  - **Footer:** Disabled until a card is tapped $\rightarrow$ enables `[CONTINUE →]` (`mdBrandPrimary`).
- **Behavior:** Immediately sets app locale, TTS voice engine, and backend speech recognizer parameters.

---

## SCREEN 03 — CONSENT
- **Route:** `/consent`
- **Purpose:** Obtain clear, non-coercive patient consent.
- **Layout:**
  - **Title:** `"Before we begin"` (H2 28sp).
  - **Component:** `ConsentCard` showing the 3 plain-language safety points.
  - **Expandable Accordion:** `"View detailed privacy information & data rights"`.
  - **Action Stack:**
    - Primary: `[✓ I Agree and Continue]` (`mdSuccess` `#166534`, `72dp`).
    - Secondary: `[I Do Not Agree]` (`slate-600`, outlined).
- **Behavior:** Tapping "Do Not Agree" opens safe exit modal explaining that manual token counter is available without digital intake.

---

## SCREEN 04 — IDENTIFICATION
- **Route:** `/identity`
- **Purpose:** Identify patient or create session token.
- **Layout:**
  - **Title:** `"Let's find your hospital record"` (H2 28sp).
  - **3 Massive Action Cards (`LargeChoiceCard`):**
    1. **SCAN ABHA QR CODE:** Leading icon `qr_code_scanner`, subtitle: `"Point camera at your Ayushman Bharat card"`.
    2. **ENTER MOBILE NUMBER:** Leading icon `phone_android`, subtitle: `"We will look up your registration"`.
    3. **NEW REGISTRATION / SKIP:** Leading icon `arrow_forward`, subtitle: `"Continue without prior records"`.
- **Interactions:**
  - Card 1 opens QR camera dialog.
  - Card 2 opens large on-screen numeric keypad (`72dp` number buttons).
  - Card 3 continues immediately to Care Stream.

---

## SCREEN 05 — CARE STREAM / REASON FOR VISIT
- **Route:** `/care-stream`
- **Purpose:** Direct patient into the appropriate OPD clinical queue.
- **Choices (Large Cards with distinct icons):**
  1. **General Health Problem** (Icon: `medical_services`)
  2. **Ayurveda / AYUSH Consultation** (Icon: `spa`, green tint `mdAyushTint`)
  3. **Follow-up Visit / Old Prescription** (Icon: `history`)
  4. **Document Review / Test Results** (Icon: `description`)
  5. **Emergency / Urgent Pain** (Icon: `emergency`, red border)
- **Behavior:** Emergency choice immediately routes to Screen 11/22. AYUSH choice activates AYUSH Profile (Screen 18).

---

## SCREEN 06 — VOICE INTAKE (START SPEECH)
- **Route:** `/intake`
- **Purpose:** Prompt patient to describe their symptoms in natural voice.
- **Layout:**
  - **Title:** `"What problem are you experiencing?"` (H2 28sp Bold).
  - **Subtitle:** `"Tell us in your own words. Speak freely."` (Body Large 22sp).
  - **Center:** Giant `VoiceButton` (`112dp`) with microphone icon and text `"TAP TO TALK"`.
  - **Audio Guidance:** `[🔊 Hear the question]`.
  - **Secondary:** `[⌨ Type instead]` (Opens keyboard for patients who prefer typing).
- **Behavior:** Tapping mic triggers mic permission check $\rightarrow$ starts recording $\rightarrow$ transitions smoothly to Screen 07.

---

## SCREEN 07 — ACTIVE VOICE CAPTURE & WAVEFORM
- **Route:** `/intake/listening`
- **Purpose:** Real-time audio recording with active visual and textual feedback.
- **Layout:**
  - **Title:** `"I'm listening..."` (H2 28sp Navy).
  - **Center:** Animated `ListeningWave` (9 bars bouncing with voice input).
  - **Live Transcript Card:** Semi-transparent card displaying recognized words in real time as patient speaks (Indic Whisper / Speech API stream).
  - **Actions:**
    - Primary CTA: `[✓ DONE SPEAKING]` (`72dp`, `mdBrandPrimary`).
    - Secondary: `[CANCEL / RECORD AGAIN]` (`slate-600`).
- **Timeouts:** If no speech detected for 8 seconds, plays a gentle chime and prompts: `"Did not catch that. Please speak again."`

---

## SCREEN 08 — CONVERSATIONAL FOLLOW-UP
- **Route:** `/intake/follow-up`
- **Purpose:** AI adaptive clinical clarification (one question at a time).
- **Layout:**
  - **Progress Bar:** 3-dot step indicator (Question 1 of 3).
  - **Question Card:**
    - Prompt: e.g., `"Where is the pain located?"` or `"How many days has it been?"`
    - Quick-select chip options: `[Left side]` `[Right side]` `[Center / Everywhere]`
  - **Voice Response Option:** Centered smaller mic button: `[Speak your answer]`.
  - **Text Option:** `[Type answer]`.
- **Rule:** Never show a dense multi-page form. Maximum 2 to 3 adaptive questions.

---

## SCREEN 09 — AI PROCESSING & CLINICAL STRUCTURING
- **Route:** `/intake/processing`
- **Purpose:** Calm loading state while local/cloud AI extracts clinical facts.
- **Layout:**
  - **Center:** Clean pulsing healthcare graphic (Medical cross pulsing rhythmically).
  - **Headline:** `"Understanding your response..."` (24sp Semibold).
  - **Sub-label:** `"Organizing symptom details for Dr. Sharma..."`
  - **Forbidden:** Never show technical terms (`"LLM"`, `"Tokens"`, `"Inference"`, `"Embedding score"`).

---

## SCREEN 10 — SIMPLE SUMMARY CONFIRMATION
- **Route:** `/intake/summary`
- **Purpose:** Closed-loop explain-back confirmation without clinical editing burden.
- **Layout:**
  - **Headline:** `"Is this information correct?"` (H2 28sp).
  - **Summary Card (`SummaryCard`):**
    - Main Problem: **Headache**
    - Started: **3 days ago**
    - Pain Level: **Moderate (6 out of 10)**
  - **Audio Readout:** Prominent speaker button: `[🔊 Listen to summary]`.
  - **Verification Buttons (Massive Side-by-Side on Kiosk, Stacked on Phone):**
    - `[✓ YES, THAT'S RIGHT]` (72dp, `mdSuccess` `#166534`).
    - `[↻ NO, SAY AGAIN]` (72dp, `mdTriageRed` `#991B1B`).
- **Rule:** Tapping NO returns to voice screen for natural spoken correction. Patient never edits complex medical taxonomy manually.

---

## SCREEN 11 — RED FLAG / TRIAGE WARNING
- **Route:** `/triage`
- **Condition:** Triggered only if clinical engine identifies high-risk criteria (e.g., acute chest pain, SpO2 $< 90\%$, stroke symptoms).
- **Visuals:** Dominant crimson emergency styling (`mdTriageRed` `#991B1B`).
- **Layout:**
  - **Header Banner:** Emergency beacon icon + `"URGENT MEDICAL ATTENTION REQUIRED"`.
  - **Message:** `"Your symptoms require immediate evaluation by hospital clinical staff."`
  - **Instructions:** `"Please proceed directly to the Emergency Clinical Desk (Room 001). Your information has been flagged as Priority."`
  - **Actions:**
    - Primary CTA: `[🚨 GET IMMEDIATE HELP / ALERT NURSE]` (`76dp`, flashing red border).
    - Secondary: `[PRINT PRIORITY EMERGENCY TOKEN]`.
- **Safety Gate:** Normal intake queue progression is blocked.

---

## SCREEN 12 — DOCUMENT INTRO (PRESCRIPTION SCAN)
- **Route:** `/documents`
- **Purpose:** Solicit paper prescriptions, lab slips, or hospital discharge records.
- **Layout:**
  - **Illustration:** Clean document scan graphic.
  - **Headline:** `"Do you have medical papers or old prescriptions?"`
  - **Body:** `"Scanning your papers helps the doctor see your previous medicines."`
  - **Actions:**
    - Primary: `[📷 SCAN DOCUMENTS]` (`72dp`, `mdBrandPrimary`).
    - Secondary: `[NO PAPERS / SKIP STEP]` (`60dp`, `slate-600` outline).

---

## SCREEN 13 — DOCUMENT CAMERA CAPTURE
- **Route:** `/documents/camera`
- **Purpose:** Fast document framing and capture.
- **Layout:**
  - **Camera Feed:** Full-screen preview with 4:3 `DocumentGuideOverlay`.
  - **Guidance Text (Top):** `"Place prescription flat inside the frame"` $\rightarrow$ changes to `"Hold steady, capturing..."`.
  - **Shutter Control (Bottom):** Large circular white shutter button (`88dp`) + Flash toggle + Gallery upload option.
  - **After Snap:** Shows snapshot preview with `[RETAKE]` and `[USE THIS PHOTO]`.

---

## SCREEN 14 — OCR PROCESSING & LINE INDEXING
- **Route:** `/documents/processing`
- **Purpose:** Indicate document digitization progress.
- **Layout:**
  - Thumbnail of captured document with an animated green laser line sweeping up and down.
  - Status progression stepper:
    - `[✓] Document aligned`
    - `[⟳] Reading handwriting & print...`
    - `[ ] Finding medicines and dosages...`

---

## SCREEN 15 — OCR RESULT & EVIDENCE OVERVIEW
- **Route:** `/documents/results`
- **Purpose:** Display extracted medicines with verifiable provenance.
- **Layout:**
  - **Headline:** `"Medical documents recorded"` (H2 28sp).
  - **Extracted Medicine Cards (`OCRFieldCard`):**
    - Item 1: **Metformin 500 mg** (1 tab twice daily) — `[Line 2, 3]` — `[View Prescription Evidence ↗]`
    - Item 2: **Atorvastatin 20 mg** (1 tab at bedtime) — `[Line 5]` — `[View Prescription Evidence ↗]`
  - **Action:** `[CONTINUE →]` (`72dp`, `mdBrandPrimary`).

---

## SCREEN 16 — SOURCE DOCUMENT EVIDENCE VIEWER
- **Route:** `/documents/evidence`
- **Purpose:** Clinical trust through bounding-box verification ("No Receipt, No Fact").
- **Layout:**
  - **Interactive Image Viewer:** Pinch-to-zoom and pan of the original captured prescription.
  - **Highlight Box:** Crisp golden-amber bounding box (`#F59E0B`) drawn precisely around the cited lines.
  - **Detail Drawer (Bottom):** Displays the extracted text, confidence score (`94%`), and close button.

---

## SCREEN 17 — VITALS RECORDING
- **Route:** `/vitals`
- **Purpose:** Collect basic physiological measurements from connected sensors or manual nurse input.
- **Layout:**
  - **Grid of 4 Metric Cards (`VitalCard`):**
    1. **Blood Pressure:** `128 / 82` mmHg (Status: `Normal`)
    2. **Pulse Rate:** `74` bpm (Status: `Connected`)
    3. **Oxygen (SpO2):** `98%` (Status: `Connected`)
    4. **Body Temperature:** `98.6°F` (Status: `Normal`)
  - **Hardware Fallback:** If IoT hardware is unplugged: `"Sensor not detected. Continue without vitals or enter manually."`
  - **Action:** `[CONFIRM & CONTINUE]` (`mdBrandPrimary`).

---

## SCREEN 18 — AYUSH LIFESTYLE PROFILE
- **Route:** `/ayush`
- **Condition:** Shown only when patient selects AYUSH or AIIA care stream.
- **Purpose:** Capture Ayurvedic Dashavidha Pariksha fundamentals in plain conversational words.
- **Layout:**
  - **Title:** `"Your daily health habits (दिनचर्या)"` (H2 28sp).
  - **Section 1: Digestion (Agni):**
    - Choice Pills: `[Strong / Always hungry]` `[Weak / Heavy]` `[Variable / Irregular]`
  - **Section 2: Bowel Habit (Koshtha):**
    - Choice Pills: `[Regular / Smooth]` `[Hard / Constipated]` `[Loose / Frequent]`
  - **Section 3: Sleep (Nidra):**
    - Choice Pills: `[Deep / Sound]` `[Disturbed]` `[Difficulty falling asleep]`
- **Rule:** Never display complex Sanskrit clinical jargon alone; always pair with plain-language everyday descriptions.

---

## SCREEN 19 — DEPARTMENT ROUTING & QUEUE ASSIGNMENT
- **Route:** `/queue`
- **Purpose:** Confirm clinical intake success and assign patient token.
- **Layout:**
  - **Headline:** `"Your intake is complete!"` (H2 28sp Forest Green).
  - **Queue Ticket Card (`QueueTicketCard`):**
    - Department: **General Medicine OPD (Ayurveda)**
    - Token: **A-402** (Giant 48sp Navy)
    - Estimated Wait: **~15 minutes** (3 patients ahead)
    - Assigned Doctor: **Cabin 104 (Dr. Sharma)**
  - **Action Buttons:**
    - `[VIEW HOSPITAL SERVICES & PHARMACY]` (`64dp`, outlined).
    - `[HOSPITAL MAP / GET DIRECTIONS]` (`64dp`, outlined).
    - `[FINISH / DONE]` (`72dp`, `mdBrandPrimary`).

---

## SCREEN 20 — HOSPITAL SERVICES DIRECTORY
- **Route:** `/services`
- **Purpose:** Guide patient to ancillary hospital facilities while waiting.
- **Grid of Service Cards (`HospitalServiceCard`):**
  - **OPD Rooms** (Icon: `local_hospital`)
  - **Pharmacy & Dispensary** (Icon: `medication`)
  - **Diagnostic Lab / Blood Tests** (Icon: `biotech`)
  - **AYUSH Panchakarma Block** (Icon: `spa`)
  - **Help Desk & Registration** (Icon: `support_agent`)
  - **Drinking Water & Washrooms** (Icon: `wc`)
  - **Emergency Casualty** (Icon: `emergency`, red)

---

## SCREEN 21 — HOSPITAL MAP & NAVIGATION
- **Route:** `/map`
- **Purpose:** Accessible wayfinding inside the hospital facility.
- **Layout:**
  - **Floor Plan Canvas:** Simplified high-contrast architectural floor plan showing Current Location (`Kiosk 1`) and Destination Path to `Cabin 104`.
  - **Step-by-Step Text Alternative (For Low Vision):**
    - Step 1: Walk straight past the Pharmacy (20 meters).
    - Step 2: Turn right at the Water Cooler.
    - Step 3: Cabin 104 is the second door on your left.
  - **Action:** `[🔊 Read Directions Aloud]` + `[Back to Token]`.

---

## SCREEN 22 — EMERGENCY SOS ACTION
- **Route:** `/emergency`
- **Purpose:** Immediate distress trigger accessible from header or red flag alert.
- **Layout:**
  - Massive Red Screen with Pulsing Emergency Beacon.
  - Action 1: `[📞 CALL CASUALTY DESK IMMEDIATELY]` (Connects hospital intercom).
  - Action 2: `[DISPATCH EMERGENCY NURSE TO KIOSK]`.
  - Action 3: `[REQUEST AMBULANCE TRANSPORT]` $\rightarrow$ routes to Screen 23.

---

## SCREEN 23 — AMBULANCE & DISPATCH STATUS
- **Route:** `/emergency/ambulance`
- **Purpose:** Transparent emergency transport tracking.
- **Layout:**
  - Status Banner: `"Ambulance Dispatched"` (or clearly labeled `"Simulation Mode: Hackathon Demo"`).
  - Estimated Arrival: `"8 mins"`
  - Vehicle: `"Ambulance 04 (Cardiac Life Support)"`
  - Contact: `[Call Ambulance Driver]`.

---

## SCREEN 24 — COMPLETION & PRIVACY AUTO-RESET
- **Route:** `/completed`
- **Purpose:** Confirm completion and strictly purge all private patient data before the next patient arrives.
- **Layout:**
  - **Success Icon:** Large Green Checkmark (`80dp`).
  - **Message:** `"Your details have been securely transmitted to Dr. Sharma's desk."`
  - **Token Reminder:** `"Please remember your Token Number: A-402"`.
  - **Countdown Timer:** Prominent circular 10-second countdown: `"This screen will automatically reset in 10 seconds for your privacy."`
  - **Manual Trigger:** `[RESET SCREEN NOW]` (`64dp`).
- **On Timer Expiry:** Wipes local secure storage, resets state to initial, and reloads Screen 01 (`/welcome`).

---

## SCREEN A-06B — 1-TAP CONVERSATIONAL CALL INTAKE (BYOD Mobile App Feature)
- **Route:** `/call-intake`
- **Target:** Mobile BYOD Patient Smartphone
- **Purpose:** Provide an effortless phone call experience for elderly patients waiting in OPD queues.
- **Layout:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ [← Back]          ACTIVE INTAKE CALL              [Speaker] │
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
  │ │ ✓ Epigastric Burning (पेट में जलन) · 3 Days             │ │
  │ │ ✓ Retrosternal Chest Pain (सीने में दर्द) · 3 Days      │ │
  │ └─────────────────────────────────────────────────────────┘ │
  ├─────────────────────────────────────────────────────────────┤
  │ Call Controls Bar:                                          │
  │   [ 🔇 Mute ]      [ 🔴 END CALL & REVIEW ]     [ ⌨ Type ]   │
  └─────────────────────────────────────────────────────────────┘
  ```
- **Interactions:**
  - Audio streams in chunks to `POST /api/call/audio-turn`.
  - Incoming TTS audio plays automatically over speakerphone.
  - Extracted symptoms pop into view as animated chips in real-time.
  - End Call button routes patient directly to Screen 10 (Summary Confirmation).

---

# 9. GLOBAL STATES & SYSTEM RESILIENCE FRAMEWORK

MediKiosk runs on edge hardware in hospitals where internet cables get unplugged and Wi-Fi drops unpredictably. The UI must communicate system health with absolute clarity.

---

### 1. Network Connectivity States
- **State A (Cloud Online):** Subtle green indicator in header (`"Cloud Online"`). All models and ABDM synchronization active.
- **State B (Edge Offline Local Hub):** Header banner changes to Amber (`"Edge Mode: Running on Local Laptop Engine"`). Zero disruption to patient intake; speech and OCR run on local ONNX engines.
- **State C (Total Disconnect / Hub Unreachable):** Shows friendly error card: `"Cannot reach local intake station. Your inputs have been saved locally. Please notify hospital attendant."` + `[Retry Connection]` button.

---

### 2. Hardware & Permission Failures
- **Microphone Denied / Unavailable:**
  - Notification: `"Microphone is not accessible on this device."`
  - Automatic Fallback: System displays on-screen touch cards and keyboard without crashing.
- **Camera Denied / Unreadable QR:**
  - Clear message: `"Could not read QR code. Please enter your mobile number or tap Skip."`
- **Vitals Sensor Disconnected:**
  - Unobtrusive badge: `"Sensor offline. Continuing without vitals."`

---

### 3. Session Timeout & Privacy Defense
- If a patient walks away midway through intake, an inactivity timer fires at **45 seconds**:
  - Displays a warning modal: `"Are you still there? Screen will reset in 15 seconds."`
  - If no interaction by 60 seconds, state is completely purged from RAM and app resets to Screen 01.
  - No patient health information or prescription images remain cached on the display.

---

# 10. FLUTTER IMPLEMENTATION ARCHITECTURE & CODE BLUEPRINT

---

## 10.1 Recommended Folder Structure
```text
mobile/lib/
├── app/
│   ├── app.dart                    # Main MaterialApp.router setup
│   ├── router.dart                 # GoRouter route declarations (Screens 01–24)
│   └── theme/
│       ├── colors.dart             # Primitive & Semantic Color Tokens
│       ├── typography.dart         # Multilingual TextTheme definitions
│       ├── dimensions.dart         # Spacing, Radius, Elevation tokens
│       └── app_theme.dart          # M3 ThemeData & MediKioskTheme extension
│
├── core/
│   ├── network/
│   │   ├── api_client.dart         # HTTP & Multipart client
│   │   └── endpoints.dart          # API route definitions
│   ├── widgets/
│   │   ├── medi_scaffold.dart      # Standardized responsive scaffold
│   │   ├── medi_header.dart        # Unified hospital header
│   │   ├── primary_button.dart     # 72dp high-contrast CTA
│   │   ├── secondary_button.dart   # 64dp outline button
│   │   ├── choice_card.dart        # Tactile selection card
│   │   ├── voice_button.dart       # Oversized pulsing mic button
│   │   ├── listening_wave.dart     # Audio visualizer widget
│   │   ├── summary_card.dart       # Explain-back review container
│   │   ├── emergency_banner.dart   # Flashing red triage warning
│   │   └── offline_banner.dart     # Cloud vs Edge connectivity indicator
│   └── utils/
│       ├── responsive.dart         # Breakpoint & screen width helpers
│       └── audio_feedback.dart     # Sound earcon player & TTS helper
│
├── data/
│   ├── models/
│   │   ├── clinical_fact.dart      # Canonical Pydantic-mirror DTO
│   │   ├── encounter.dart          # Encounter bootstrap model
│   │   ├── document_result.dart    # OCR result & line indices
│   │   └── queue_status.dart       # Live token status model
│   ├── datasources/
│   │   ├── mock_datasource.dart    # 100% offline mock data provider
│   │   └── api_datasource.dart     # REST backend datasource
│   └── repositories/
│       ├── intake_repository.dart  # Voice turn & intake orchestration
│       └── document_repository.dart# Camera upload & OCR evidence
│
└── features/
    ├── welcome/                    # Screen 01 Welcome
    ├── language/                   # Screen 02 Language Selection
    ├── consent/                    # Screen 03 Consent
    ├── identity/                   # Screen 04 ABHA QR & Phone
    ├── care_stream/                # Screen 05 Care Stream
    ├── intake/                     # Screens 06–10 Voice Intake & Summary
    ├── triage/                     # Screen 11 Red Flag Warning
    ├── documents/                  # Screens 12–16 Camera, OCR & Evidence
    ├── vitals/                     # Screen 17 Vitals
    ├── ayush/                      # Screen 18 AYUSH Profile
    ├── queue/                      # Screen 19 & Screen 6 Queue Tracker
    ├── call_intake/                # Screen A-06B Conversational Call UI
    ├── services/                   # Screen 20 Hospital Services
    ├── map/                        # Screen 21 Hospital Map
    ├── emergency/                  # Screens 22–23 Emergency & Ambulance
    └── completion/                 # Screen 24 Completion & Privacy Reset
```

---

## 10.2 Production Dart Theme Specification

```dart
// lib/app/theme/colors.dart
import 'package:flutter/material.dart';

abstract class MediColors {
  // Layer 1: Primitives
  static const Color slate50   = Color(0xFFF8FAFC);
  static const Color slate100  = Color(0xFFF1F5F9);
  static const Color slate200  = Color(0xFFE2E8F0);
  static const Color slate400  = Color(0xFF94A3B8);
  static const Color slate600  = Color(0xFF475569);
  static const Color slate800  = Color(0xFF1E293B);
  static const Color slate900  = Color(0xFF0F172A);
  static const Color white     = Color(0xFFFFFFFF);

  static const Color blue50    = Color(0xFFEFF6FF);
  static const Color blue600   = Color(0xFF2563EB);
  static const Color blue800   = Color(0xFF1E3A8A);
  static const Color blue900   = Color(0xFF172554);

  static const Color emerald800= Color(0xFF065F46);
  static const Color red800    = Color(0xFF991B1B);
  static const Color amber800  = Color(0xFF92400E);

  // Layer 2: Semantics
  static const Color canvas        = slate50;
  static const Color surface       = white;
  static const Color surfaceSubtle = slate100;
  static const Color brandPrimary  = blue800;
  static const Color brandDark     = slate900;
  static const Color brandTint     = blue50;
  static const Color ayushGreen    = emerald800;
  static const Color triageRed     = red800;
  static const Color warning       = amber800;
  static const Color border        = slate200;
  static const Color borderSelected= blue800;
  static const Color textPrimary   = slate900;
  static const Color textMuted     = slate600;
  static const Color textInverse   = white;
}
```

```dart
// lib/app/theme/app_theme.dart
import 'package:flutter/material.dart';
import 'colors.dart';

class MediKioskTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: MediColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: MediColors.brandPrimary,
        onPrimary: MediColors.textInverse,
        primaryContainer: MediColors.brandTint,
        surface: MediColors.surface,
        onSurface: MediColors.textPrimary,
        error: MediColors.triageRed,
        outline: MediColors.border,
      ),
      fontFamily: 'Roboto',
      fontFamilyFallback: const [
        'NotoSansDevanagari',
        'NotoSansTamil',
        'NotoSansTelugu',
      ],
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontSize: 36,
          fontWeight: FontWeight.w700,
          color: MediColors.textPrimary,
          height: 1.25,
        ),
        headlineLarge: TextStyle(
          fontSize: 28,
          fontWeight: FontWeight.w600,
          color: MediColors.textPrimary,
          height: 1.30,
        ),
        headlineMedium: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w600,
          color: MediColors.textPrimary,
          height: 1.35,
        ),
        bodyLarge: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w400,
          color: MediColors.textPrimary,
          height: 1.40,
        ),
        bodyMedium: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w400,
          color: MediColors.textMuted,
          height: 1.45,
        ),
        labelLarge: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: MediColors.textInverse,
          height: 1.25,
        ),
      ),
      cardTheme: CardTheme(
        color: MediColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: MediColors.border, width: 1.5),
        ),
      ),
    );
  }
}
```

---

# 11. DEVELOPER CHECKLIST & INTEGRATION CONTRACT

For **Thoufikur** and **Mubashir** during Android project execution:

- [ ] All interactive touch targets must measure at least **64 × 64 dp** (`72dp` for primary CTAs).
- [ ] Text contrast must verify against **WCAG 2.2 Level AAA (>= 7:1)**.
- [ ] Indic text (Hindi, Tamil, Telugu, Marathi) must never clip top or bottom matras.
- [ ] All 24 patient screens must operate cleanly in **Mock Mode** before network calls.
- [ ] All voice turns must trigger visible tactile feedback (pulsing halo, active waveform).
- [ ] Camera screens must include a clear **4:3 document alignment guide** with corner indicators.
- [ ] Emergency and Red Flag screens must visually dominate the UI in **deep crimson (`#991B1B`)**.
- [ ] The patient summary screen must use simple **[YES]** / **[NO]** verification — never ask the patient to manually edit clinical terms.
- [ ] Screen 24 must enforce an **automated 10-second privacy reset** that purges temporary session data.
- [ ] Responsive layouts must look flawless on both an Android smartphone (portrait) and a 1280 × 800 kiosk tablet (landscape).

---
*MediKiosk Android & Mobile Design System Specification — SIH26047 Canonical Release.*
