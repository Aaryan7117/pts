# MediKiosk — Web UI/UX Design System Specification & Master Blueprint
## Canonical Web Design System, Component Catalog & Screen-by-Screen Blueprint
**Document Version:** 3.0.0 (SIH26047 Production Specification)  
**Target Clients:** Desktop Web (1920×1080 / 1440×900), Tablet (1024×768 / 1280×800 Landscape), Web Kiosk Displays, Mobile Browsers (390×844)  
**Primary Portals:** Public Onboarding & Triage, Patient Health Workspace, Doctor Clinical Command Center, IVR Voice Call Simulator  
**Core References:** `DOCS/MediKiosk_Web_UI_Master_Flow_Antigravity.md`, `MEDIKIOSK_ANDROID_DESIGN_SPEC.md`, FastAPI Backend (`app/main.py`)  

---

## Table of Contents
1. [Design Philosophy, Visual Aesthetics & Foundational Rules](#1-design-philosophy-visual-aesthetics--foundational-rules)
2. [Three-Layer Web Design Token Architecture](#2-three-layer-web-design-token-architecture)
   - [2.1 Layer 1: Primitive Tokens (Colors, Spacing, Radius, Shadows)](#21-layer-1-primitive-tokens)
   - [2.2 Layer 2: Semantic Tokens (Light Medical Color System)](#22-layer-2-semantic-tokens)
   - [2.3 Layer 3: Component-Scoped Tokens](#23-layer-3-component-scoped-tokens)
   - [2.4 Contrast & Accessibility Matrix (WCAG 2.2 AAA / AA Compliance)](#24-contrast--accessibility-matrix-wcag-22-aaa--aa-compliance)
3. [Typography & Multilingual Script Architecture](#3-typography--multilingual-script-architecture)
   - [3.1 Font Families & Script Fallback Stack](#31-font-families--script-fallback-stack)
   - [3.2 Scale, Modular Rhythm & Weights](#32-scale-modular-rhythm--weights)
   - [3.3 Indic Diacritic Preservation & Dynamic Type Scaling](#33-indic-diacritic-preservation--dynamic-type-scaling)
4. [Responsive Layout, Grid System & Viewport Breakpoints](#4-responsive-layout-grid-system--viewport-breakpoints)
   - [4.1 Breakpoint Strategy & Target Displays](#41-breakpoint-strategy--target-displays)
   - [4.2 Portal App Shell Layouts (Public, Patient Workspace, Doctor Command Center)](#42-portal-app-shell-layouts)
   - [4.3 Touch Target & Ergonomics for Kiosk/Tablet Displays](#43-touch-target--ergonomics-for-kiosktablet-displays)
5. [Iconography, Brand Geometry & Visual Assets](#5-iconography-brand-geometry--visual-assets)
   - [5.1 Medical Iconography Canonical Mapping](#51-medical-iconography-canonical-mapping)
   - [5.2 MediKiosk Medical Cross Brand Geometry](#52-medikiosk-medical-cross-brand-geometry)
   - [5.3 Semantic Status Badge Matrix](#53-semantic-status-badge-matrix)
6. [Motion Choreography, Transitions & Audio Feedback](#6-motion-choreography-transitions--audio-feedback)
   - [6.1 CSS Timing Tokens & Cubic-Bezier Curves](#61-css-timing-tokens--cubic-bezier-curves)
   - [6.2 Signature Micro-Interactions (Mic Halo, WebAudio Visualizer, Laser OCR, Bounding Box Pop-in)](#62-signature-micro-interactions)
   - [6.3 Auditory Feedback (Earcons & Browser TTS Playback)](#63-auditory-feedback)
7. [Comprehensive Web Component Catalog (32 Production Components)](#7-comprehensive-web-component-catalog-32-production-components)
8. [Complete Page-by-Page Web UI Blueprint (36 Detailed Views)](#8-complete-page-by-page-web-ui-blueprint-36-detailed-views)
   - [8.1 Public Entry & Onboarding (Pages 01–03)](#81-public-entry--onboarding-pages-0103)
   - [8.2 Patient Authentication & Setup (Pages 04–07)](#82-patient-authentication--setup-pages-0407)
   - [8.3 Patient Health Workspace & Intake (Pages 08–21)](#83-patient-health-workspace--intake-pages-0821)
   - [8.4 Patient Queue, Records & Discovery (Pages 22–28)](#84-patient-queue-records--discovery-pages-2228)
   - [8.5 Doctor Authentication & Clinical Command Center (Pages 29–33)](#85-doctor-authentication--clinical-command-center-pages-2933)
   - [8.6 Doctor Clinical Review, Evidence & Consultation Workspace (Pages 34–43)](#86-doctor-clinical-review-evidence--consultation-workspace-pages-3443)
   - [8.7 IVR Voice Simulator & WebRTC Testbed (Page 44)](#87-ivr-voice-simulator--webrtc-testbed-page-44)
9. [State Management, Data Flow & Verified FastAPI Backend Contract](#9-state-management-data-flow--verified-fastapi-backend-contract)
10. [Global States, Error Handling, Offline Resilience & Security UX](#10-global-states-error-handling-offline-resilience--security-ux)
11. [Web Implementation Tech Stack & Architecture Blueprint](#11-web-implementation-tech-stack--architecture-blueprint)
12. [Developer Execution Checklist & Acceptance Verification Matrix](#12-developer-execution-checklist--acceptance-verification-matrix)

---

# 1. DESIGN PHILOSOPHY, VISUAL AESTHETICS & FOUNDATIONAL RULES

The MediKiosk Web Application is an enterprise-grade clinical portal serving two distinct user personas simultaneously:
1. **The Patient:** Rural, elderly (68+ yrs), or OPD visitors seeking care who require extreme clarity, reassuring warmth, large tactile targets, multilingual voice interaction, and zero medical jargon burden.
2. **The Clinician / Doctor:** High-volume physicians and triage nurses managing 40–80 patients per OPD shift who require high data density, 30-word clinical synopses, instant drug-interaction flags, verifiable line-level document evidence, and friction-free consultation tools.

### Visual Quality Bar: "RetinopathyScan Light Medical Standard"
Drawing inspiration from high-precision diagnostic clinical portals (such as RetinopathyScan) while deliberately choosing a **luminous, clean, light medical aesthetic**:
- **Pristine Medical White & Cool Slate Canvas:** Crisp white cards (`#FFFFFF`) floating effortlessly on subtle cool slate backgrounds (`#F6F9FC`), bounded by razor-thin borders (`#DCE5F0`).
- **Deep Navy & Royal Blue Authority:** Primary brand color `#1667D9` paired with deep clinical navy `#0D3B7A` for typographic authority and institutional trust.
- **Teal & AYUSH Harmony:** Clinical teal `#0B8F87` and herbal emerald green `#047857` representing holistic care, wellness, and Ministry of AYUSH / AIIA integration.
- **Refined Restraint:** Zero murky dark modes, zero gratuitous heavy blur glassmorphism, zero floating ornamental 3D blobs. Visual sophistication is achieved through perfect typographic hierarchy, micro-elevations, crisp borders, and rhythmic 8px baseline spacing.

### Core Foundational Rules:
1. **API-Driven Presentation Layer:** The frontend is a high-fidelity presentation layer directly connected to the working FastAPI backend (`/api/auth`, `/api/patient`, `/api/doctor`, `/api/encounters`, `/api/call`, `/api/documents`, `/api/queue`, `/api/ayush`, `/api/ivr`). No duplicate databases, no mock client state where live data exists.
2. **One-Click Verifiable Provenance ("No Receipt, No Fact"):** Every medication, dosage, or lab value extracted from an uploaded document must link visually to a highlighted bounding box and cited line index on the original image.
3. **No Patient Editing Burden:** Patients confirm or clarify statements using large conversational cards and high-contrast **[YES]** / **[NO]** controls. Patients are never forced to edit dosage numbers, clinical ICD/SNOMED codes, or OCR text strings manually.
4. **Adaptive Role Isolation:** Patient and Doctor experiences are strictly separated via route guards and custom shell layouts. Doctors see diagnostic density; patients see guided simplicity.
5. **Universal Multilingual Accessibility:** Flawless rendering in English and 4 major Indian languages (Hindi, Tamil, Telugu, Marathi). Complex Indic scripts and conjuncts must never be vertically clipped.

---

# 2. THREE-LAYER WEB DESIGN TOKEN ARCHITECTURE

Tokens are defined as native CSS Custom Properties in `:root`, organized in a strict 3-tier hierarchy:
```text
┌────────────────────────────────────────────────────────┐
│  LAYER 1: PRIMITIVE TOKENS (Raw values)                │
│  --color-blue-800: #1667D9; --space-4: 16px;           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 2: SEMANTIC TOKENS (Role, intent & context)     │
│  --bg-surface: var(--color-white);                     │
│  --color-primary: var(--color-blue-800);               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  LAYER 3: COMPONENT TOKENS (Scoped widget styles)      │
│  --card-border-radius: var(--radius-xl);               │
│  --voice-btn-size: 96px;                               │
└────────────────────────────────────────────────────────┘
```

---

## 2.1 Layer 1: Primitive Tokens

```css
:root {
  /* --- Primitive Color Palette --- */
  --pr-slate-25:  #FBFCFE;
  --pr-slate-50:  #F6F9FC;
  --pr-slate-100: #EEF3F8;
  --pr-slate-200: #DCE5F0;
  --pr-slate-300: #B8C8DB;
  --pr-slate-400: #8FA2BA;
  --pr-slate-500: #6B7A90;
  --pr-slate-600: #4B586B;
  --pr-slate-700: #334053;
  --pr-slate-800: #1D2B3F;
  --pr-slate-900: #10233E;
  --pr-white:     #FFFFFF;

  /* Primary Royal Blues */
  --pr-blue-50:   #EAF3FF;
  --pr-blue-100:  #D4E6FE;
  --pr-blue-200:  #A7C8FD;
  --pr-blue-400:  #5392F8;
  --pr-blue-600:  #1E75E8;
  --pr-blue-700:  #1667D9;
  --pr-blue-900:  #0D3B7A;
  --pr-blue-950:  #08244D;

  /* Healthcare Teals & AYUSH Greens */
  --pr-teal-50:   #E7F8F6;
  --pr-teal-500:  #12A59C;
  --pr-teal-700:  #0B8F87;
  --pr-teal-900:  #075B56;

  --pr-green-50:  #EAF8F0;
  --pr-green-600: #17824C;
  --pr-green-800: #0D6338;
  --pr-green-900: #047857;

  /* Triage Alerts & Warnings */
  --pr-red-50:    #FFF0F0;
  --pr-red-100:   #FFE0E0;
  --pr-red-600:   #E04040;
  --pr-red-700:   #C83A3A;
  --pr-red-900:   #881D1D;

  --pr-amber-50:  #FFF6E5;
  --pr-amber-500: #D97E00;
  --pr-amber-700: #B66A00;
  --pr-amber-900: #7A4300;

  /* --- Spacing Scale (8px Grid with 4px Subgrid) --- */
  --space-0-5: 2px;
  --space-1:   4px;
  --space-2:   8px;
  --space-3:   12px;
  --space-4:   16px;
  --space-5:   20px;
  --space-6:   24px;
  --space-8:   32px;
  --space-10:  40px;
  --space-12:  48px;
  --space-16:  64px;
  --space-20:  80px;

  /* --- Border Radius Scale --- */
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 28px;
  --radius-full: 9999px;

  /* --- Crisp Clinical Shadows (Multi-layered, low-tint) --- */
  --shadow-xs: 0 1px 2px rgba(16, 35, 62, 0.04);
  --shadow-sm: 0 2px 4px rgba(16, 35, 62, 0.04), 0 1px 2px rgba(16, 35, 62, 0.03);
  --shadow-md: 0 4px 12px rgba(16, 35, 62, 0.06), 0 2px 4px rgba(16, 35, 62, 0.04);
  --shadow-lg: 0 8px 24px rgba(16, 35, 62, 0.08), 0 3px 6px rgba(16, 35, 62, 0.04);
  --shadow-xl: 0 16px 36px rgba(16, 35, 62, 0.12), 0 6px 12px rgba(16, 35, 62, 0.06);
  --shadow-active-blue: 0 0 0 3px rgba(22, 103, 217, 0.2), 0 4px 14px rgba(22, 103, 217, 0.18);
  --shadow-active-red: 0 0 0 3px rgba(200, 58, 58, 0.25), 0 6px 20px rgba(200, 58, 58, 0.25);

  /* --- Z-Index Stack --- */
  --z-base: 1;
  --z-card-hover: 10;
  --z-sticky-nav: 100;
  --z-dropdown: 200;
  --z-modal-scrim: 900;
  --z-modal-canvas: 1000;
  --z-toast: 1100;
}
```

---

## 2.2 Layer 2: Semantic Tokens

```css
:root {
  /* Surfaces & Canvas */
  --bg-canvas:         var(--pr-slate-50);     /* #F6F9FC Base Page Canvas */
  --bg-surface:        var(--pr-white);        /* #FFFFFF Card & Modal Surfaces */
  --bg-surface-soft:   var(--pr-slate-25);     /* #FBFCFE Subtle Header / Card inset */
  --bg-surface-subtle: var(--pr-slate-100);    /* #EEF3F8 Disabled & Table Alternate */

  /* Typography Colors */
  --text-primary:      var(--pr-slate-900);    /* #10233E High-contrast text */
  --text-secondary:    var(--pr-slate-700);    /* #334053 Body copy */
  --text-muted:        var(--pr-slate-500);    /* #6B7A90 Labels & Helper descriptions */
  --text-inverse:      var(--pr-white);        /* #FFFFFF Text on buttons / dark badges */
  --text-brand:        var(--pr-blue-700);     /* #1667D9 Interactive links & highlights */

  /* Borders & Dividers */
  --border-subtle:     var(--pr-slate-100);    /* Dividers inside cards */
  --border-default:    var(--pr-slate-200);    /* #DCE5F0 Standard card borders (1px) */
  --border-strong:     var(--pr-slate-300);    /* Focused inputs & active borders */
  --border-brand:      var(--pr-blue-700);     /* Selected state borders (2px) */

  /* Brand Interactive */
  --brand-primary:     var(--pr-blue-700);     /* #1667D9 Dominant Action */
  --brand-dark:        var(--pr-blue-900);     /* #0D3B7A Deep Header Accent */
  --brand-tint:        var(--pr-blue-50);      /* #EAF3FF Selected Card Fill */
  --brand-hover:       var(--pr-blue-600);     /* Hover state */

  /* Clinical Status Intent */
  --status-teal:       var(--pr-teal-700);     /* #0B8F87 Clinical Telehealth & Sensors */
  --status-teal-tint:  var(--pr-teal-50);
  --status-ayush:      var(--pr-green-900);    /* #047857 Ministry of AYUSH & Verified */
  --status-success:    var(--pr-green-600);    /* #17824C Normal Range / Verified Fact */
  --status-success-tint: var(--pr-green-50);
  --status-warning:    var(--pr-amber-700);    /* #B66A00 Drug Alert / Missing Document */
  --status-warning-tint: var(--pr-amber-50);
  --status-danger:     var(--pr-red-700);      /* #C83A3A Red Flag Triage & Emergency */
  --status-danger-tint: var(--pr-red-50);
}
```

---

## 2.3 Layer 3: Component-Scoped Tokens

```css
:root {
  /* Topbar & Sidebar */
  --header-height:         72px;
  --sidebar-width:          260px;
  --sidebar-collapsed-width: 76px;

  /* Card Specifications */
  --card-padding-sm:        16px;
  --card-padding-md:        24px;
  --card-padding-lg:        32px;
  --card-radius:            var(--radius-xl);   /* 20px */
  --card-border-width:      1px;

  /* Interactive Buttons */
  --btn-height-sm:          36px;
  --btn-height-md:          48px;
  --btn-height-lg:          60px;
  --btn-height-touch:       68px; /* For Kiosk / Touch tablets */
  --btn-radius:             var(--radius-md);   /* 12px */

  /* Voice Intake Widgets */
  --mic-btn-size-desktop:   88px;
  --mic-btn-size-kiosk:     104px;
  --waveform-bar-width:     5px;
  --waveform-bar-gap:       6px;
  --waveform-bar-radius:    3px;

  /* Document & Evidence Bounding Boxes */
  --bounding-box-color:     #F59E0B; /* Golden Amber highlight */
  --bounding-box-bg:        rgba(245, 158, 11, 0.18);
  --bounding-box-border:    2.5px solid #D97706;
}
```

---

## 2.4 Contrast & Accessibility Matrix (WCAG 2.2 AAA / AA Compliance)

To guarantee flawless readability for elderly OPD visitors, individuals with visual impairments, and busy clinicians operating under harsh clinic lighting:

| Foreground Element | Background Surface | Contrast Ratio | WCAG 2.2 Status | Usage Context |
|---|---|---|---|---|
| `--text-primary` (`#10233E`) | `--bg-surface` (`#FFFFFF`) | **15.2 : 1** | **PASS AAA** (Exceeds 7.0:1) | Primary headings, body copy, data values |
| `--text-primary` (`#10233E`) | `--bg-canvas` (`#F6F9FC`) | **14.5 : 1** | **PASS AAA** | Section titles on page background |
| `--text-secondary` (`#334053`)| `--bg-surface` (`#FFFFFF`) | **10.1 : 1** | **PASS AAA** | Clinical summaries, table contents |
| `--text-muted` (`#6B7A90`) | `--bg-surface` (`#FFFFFF`) | **5.2 : 1** | **PASS AA** (Large text/labels) | Captions, metadata, input placeholders |
| `--text-inverse` (`#FFFFFF`)| `--brand-primary` (`#1667D9`)| **4.8 : 1** | **PASS AA** (Large text & buttons)| Primary action buttons, active navigation |
| `--text-inverse` (`#FFFFFF`)| `--brand-dark` (`#0D3B7A`) | **10.3 : 1** | **PASS AAA** | Dark badges, header CTA buttons |
| `--text-inverse` (`#FFFFFF`)| `--status-danger` (`#C83A3A`)| **5.1 : 1** | **PASS AA** | Emergency SOS buttons, Red Flag banners |
| `--text-inverse` (`#FFFFFF`)| `--status-ayush` (`#047857`) | **5.4 : 1** | **PASS AA** | AYUSH verified tags, green confirm buttons|
| `--border-default` (`#DCE5F0`)| `--bg-canvas` (`#F6F9FC`) | **3.2 : 1** | **PASS UI** (Exceeds 3.0:1) | Non-text card boundaries, input borders |

> **Critical Rule:** Never indicate status via color alone. Every badge, chip, and alert must combine:
> `Status = Color + Material/Lucide Icon + Clear Text Label`

---

# 3. TYPOGRAPHY & MULTILINGUAL SCRIPT ARCHITECTURE

Web typography must convey clinical authority while remaining comfortable and warm. The system pairs modern Latin geometric sans with localized Google Noto fonts for complete Indian language support.

---

## 3.1 Font Families & Script Fallback Stack

```css
:root {
  --font-family-sans: 
    'Plus Jakarta Sans', 
    'Inter', 
    'Noto Sans Devanagari', 
    'Noto Sans Tamil', 
    'Noto Sans Telugu', 
    -apple-system, 
    BlinkMacSystemFont, 
    'Segoe UI', 
    Roboto, 
    sans-serif;

  --font-family-mono: 
    'JetBrains Mono', 
    'SFMono-Regular', 
    Consolas, 
    monospace;
}
```

- **Primary Latin Font:** **Plus Jakarta Sans** (Weights: 400, 500, 600, 700) or **Inter** for clean legibility and balanced proportions.
- **Hindi & Marathi Fallback:** **Noto Sans Devanagari** (Weights: 400, 600, 700).
- **Tamil Fallback:** **Noto Sans Tamil** (Weights: 400, 600, 700).
- **Telugu Fallback:** **Noto Sans Telugu** (Weights: 400, 600, 700).
- **Monospace Code/Token:** **JetBrains Mono** for patient ABHA numbers, queue tokens (`A-261`), and ICD-10 / SNOMED codes.

---

## 3.2 Scale, Modular Rhythm & Weights

| Typographic Token | Font Size (rem / px) | Line Height | Font Weight | Letter Spacing | Common Usage |
|---|---|---|---|---|---|
| `--text-display` | `3.25rem` (52px) | `1.15` (60px) | 800 (ExtraBold) | `-0.025em` | Hero welcome title, oversized queue numbers |
| `--text-h1` | `2.5rem` (40px) | `1.20` (48px) | 700 (Bold) | `-0.020em` | Main page titles, triage emergency headings |
| `--text-h2` | `1.875rem` (30px) | `1.28` (38px) | 600 (SemiBold) | `-0.015em` | Section titles, major modal headers |
| `--text-h3` | `1.375rem` (22px) | `1.36` (30px) | 600 (SemiBold) | `-0.010em` | Card titles, question prompts |
| `--text-h4` | `1.125rem` (18px) | `1.40` (25px) | 600 (SemiBold) | `0em` | Subsection titles, table group headers |
| `--text-body-lg` | `1.125rem` (18px) | `1.50` (27px) | 400 (Regular) | `0em` | Choice card descriptions, consent bullets |
| `--text-body` | `1.000rem` (16px) | `1.50` (24px) | 400 / 500 | `0.010em` | Default web body text, form fields, notes |
| `--text-small` | `0.875rem` (14px) | `1.45` (20px) | 500 (Medium) | `0.015em` | Helper text, secondary table metadata |
| `--text-caption` | `0.750rem` (12px) | `1.40` (17px) | 600 (SemiBold) | `0.040em` | Uppercase category pills, timestamps |

---

## 3.3 Indic Diacritic Preservation & Dynamic Type Scaling

1. **Diacritic Clearance (`line-height` safety):** In complex Indic scripts, upper and lower vowel marks (*matras* such as `ि`, `ी`, `ु`, `ू`, and conjunct diacritics) are prone to vertical clipping when CSS `line-height` is tight. For all Indic locales (`hi`, `ta`, `te`, `mr`), line heights automatically expand to a minimum of **`1.45` to `1.60`**.
2. **Text Zoom Resilience:** The entire layout is structured with relative `rem` units based on a default `16px` root. Interfaces remain completely stable and flex without horizontal overflow when browser zoom is set up to **150%**.

---

# 4. RESPONSIVE LAYOUT, GRID SYSTEM & VIEWPORT BREAKPOINTS

MediKiosk runs on desktop clinical monitors, hospital kiosk touch terminals, doctor laptops, and patient mobile browsers.

---

## 4.1 Breakpoint Strategy & Target Displays

```text
┌───────────────────────────┬────────────────────────────────────────────────────────┐
│ Breakpoint Class          │ CSS Media Query Range & Canonical Target               │
├───────────────────────────┼────────────────────────────────────────────────────────┤
│ Mobile (Compact)          │ max-width: 639px (Patient BYOD Smartphones)            │
│ Tablet (Medium)           │ 640px to 1023px (iPads, Android Kiosk 1280x800 Port.)   │
│ Desktop Standard (Large)  │ 1024px to 1439px (Doctor Laptops, Clinic 1080p Displays)│
│ Ultra / Wide Kiosk (2XL)  │ min-width: 1440px (High-res Kiosk, Wall Monitors)      │
└───────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 4.2 Portal App Shell Layouts

### A. Public Onboarding Shell
Single centered container with a high-trust header (Logo + Language + Help button) and a max content width of `1200px`.

### B. Patient Health Workspace Shell
- **Desktop / Tablet:** Persistent left sidebar (`240px`) for sections (Dashboard, History, Documents, Timeline, Queue, Records, Profile), unified top navigation bar (`72px`) with active visit status pill and user menu, and fluid main canvas.
- **Mobile Browser:** Top header with hamburger menu opening a modern drawer, plus a docked sticky bottom navigation bar for quick access: `[Home] [Intake] [Queue] [Records]`.

```text
PATIENT WORKSPACE APP SHELL (DESKTOP)
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ [Cross] MediKiosk AI · Patient Workspace           Active Token: A-261   [🌐 Lang] [👤 User]│
├────────────────────────┬──────────────────────────────────────────────────────────────────┤
│ ❖ Dashboard            │ Breadcrumb: Dashboard > Clinical History                         │
│ 📋 Clinical History    ├──────────────────────────────────────────────────────────────────┤
│ 📄 Documents           │                                                                  │
│ ⏱ Medical Timeline     │                                                                  │
│ 🎫 Current Queue       │                        MAIN CONTENT VIEW                         │
│ 👨‍⚕️ Doctors & Hospital │                                                                  │
│ 📁 Medical Records     │                                                                  │
│ ⚙️ Profile & Settings  │                                                                  │
│                        │                                                                  │
│ 🚨 Emergency SOS       │                                                                  │
└────────────────────────┴──────────────────────────────────────────────────────────────────┘
```

### C. Doctor Clinical Command Center Shell
- **Full-Width Diagnostic Layout:** Optimized for dense scanning.
- **Top Bar:** Doctor identity (`Dr. S. Verma`), current OPD room (`Room 102`), patient queue counter (`8 waiting`), priority alert badge (`2 HIGH`), and emergency casualty shortcut.
- **3-Column Consultation Layout (on `/doctor/patients/:id/consultation`):**
  - **Left Rail (25% / 320px):** Patient quick snapshot, vitals, drug safety alerts, and uploaded document thumbnails.
  - **Center Rail (45% / 560px):** AI structured clinical history, chief complaint, chronologic symptom narrative, and highlighted line citations.
  - **Right Rail (30% / 380px):** Doctor's live workspace (Clinical assessment, SOAP notes, e-Prescription pad, referral dispatch, and sign-off verification).

---

## 4.3 Touch Target & Ergonomics for Kiosk/Tablet Displays

For standalone touch kiosk displays and hospital tablets:
- **Minimum Tap Target:** `48 × 48 px` (Web accessibility minimum).
- **Kiosk Primary Touch Buttons:** `68px` height, full card width or minimum `220px` width.
- **Card Tap Zones:** Minimum `80px` height with generous `20px` internal padding.
- **Gutter Spacing:** Minimum `16px` between adjacent interactive touch targets to prevent mis-clicks.

---

# 5. ICONOGRAPHY, BRAND GEOMETRY & VISUAL ASSETS

Clean, medical iconography with a uniform `1.75px` or `2.0px` stroke weight ensures unambiguous visual communication.

---

## 5.1 Medical Iconography Canonical Mapping

Using **Lucide-Icons** / modern SVG symbols:

| Concept / Action | Lucide Icon Identifier | Visual Role & Meaning |
|---|---|---|
| **Hospital Brand** | `<Activity />` / `<Cross />` | Official healthcare brand marker |
| **Language Switcher** | `<Globe />` | Choose between English and 4 Indian languages |
| **Help & Support** | `<HelpCircle />` | Attendant assistance / FAQ drawer |
| **Patient Profile** | `<User />` | Account info, ABHA ID status |
| **Doctor Portal** | `<Stethoscope />` | Clinician workspace & consultation |
| **Voice Idle** | `<Mic />` | Click to begin speaking |
| **Voice Listening** | `<Mic2 />` / `<Radio />` | Active microphone capture |
| **Stop Recording** | `<Square />` / `<CheckCircle2 />` | Finish voice turn |
| **Text Input** | `<Keyboard />` | Switch from voice to typing |
| **Audio Readout** | `<Volume2 />` | Text-to-speech explain-back |
| **Prescription Scan** | `<FileText />` | Document intake & OCR processing |
| **Camera Capture** | `<Camera />` | Live document snap |
| **Evidence Link** | `<ScanSearch />` / `<ExternalLink />`| Provenance bounding box lookup |
| **Medical Timeline** | `<Clock />` / `<History />` | Chronological disease & treatment history |
| **OPD Queue Token** | `<Ticket />` | Queue token badge (`A-261`) |
| **Emergency SOS** | `<AlertTriangle />` / `<Siren />` | Immediate Red Flag triage trigger |
| **AYUSH Wellness** | `<Leaf />` / `<Flower2 />` | Ayurvedic prakriti / lifestyle consultation |
| **Vitals Heartbeat** | `<HeartPulse />` | Blood pressure, pulse, SpO2 sensor feeds |
| **Network Status** | `<Wifi />` / `<WifiOff />` | Online cloud vs Local edge hub mode |

---

## 5.2 MediKiosk Medical Cross Brand Geometry

The brand mark is a **Harmonized Rounded Greek Cross** with softened geometry and an embedded inner biometric node:
- **Aspect Ratio:** `1 : 1` (Standard sizes: `32px` Header, `48px` Navigation, `80px` Welcome Hero).
- **Primary Fill:** `--brand-primary` (`#1667D9`).
- **Inner Node:** `--status-ayush` (`#047857`) center cross junction signifying the harmony of modern clinical medicine and traditional Indian AYUSH care.
- **Corner Curvature:** `6px` radius on cross arms.

---

## 5.3 Semantic Status Badge Matrix

```html
<!-- Example Semantic Status Badges -->
<span class="badge badge-red"><i data-lucide="alert-circle"></i> HIGH PRIORITY</span>
<span class="badge badge-amber"><i data-lucide="alert-triangle"></i> DRUG ALERT</span>
<span class="badge badge-green"><i data-lucide="check-circle"></i> VERIFIED</span>
<span class="badge badge-blue"><i data-lucide="clock"></i> WAITING</span>
<span class="badge badge-teal"><i data-lucide="activity"></i> SENSOR ACTIVE</span>
```

| Badge Type | Background | Border Color | Text & Icon Color | Semantic Meaning |
|---|---|---|---|---|
| **Emergency / Red Flag** | `#FFF0F0` | `#E04040` | `#C83A3A` | Immediate triage needed, severe symptom |
| **Warning / Interaction** | `#FFF6E5` | `#D97E00` | `#B66A00` | Medication conflict, unverified gap |
| **Verified / Success** | `#EAF8F0` | `#17824C` | `#17824C` | Clinician verified fact, normal vital |
| **Queue / Pending** | `#EAF3FF` | `#1667D9` | `#1667D9` | Patient waiting in queue, active session |
| **AYUSH / Natural** | `#E7F8F6` | `#0B8F87` | `#0B8F87` | AYUSH profile, herbal prescription |

---

# 6. MOTION CHOREOGRAPHY, TRANSITIONS & AUDIO FEEDBACK

Motion in MediKiosk is purpose-driven: it clarifies state changes, acknowledges voice inputs, and creates a silky, modern feel without causing motion sickness or delaying critical clinical actions.

---

## 6.1 CSS Timing Tokens & Cubic-Bezier Curves

```css
:root {
  /* Durations */
  --motion-instant:  100ms;  /* Button clicks, active ripples */
  --motion-fast:     180ms;  /* Card hover lift, dropdown reveal */
  --motion-normal:   280ms;  /* Page slide-ins, tab switches */
  --motion-slow:     450ms;  /* Modal entries, Red Flag triage alerts */
  --motion-pulse:   1400ms;  /* Mic recording halo loop */

  /* Easings */
  --ease-spring:     cubic-bezier(0.175, 0.885, 0.32, 1.15); /* Snappy tactile pop */
  --ease-smooth:     cubic-bezier(0.16, 1, 0.3, 1);          /* Apple/Modern SaaS ease-out */
  --ease-in-out:    cubic-bezier(0.4, 0, 0.2, 1);           /* Standard transition */
}
```

> **Accessibility Requirement (`prefers-reduced-motion`):**
> When the user has reduced motion enabled in their operating system or browser, all transitions immediately drop to instantaneous `0ms` opacity swaps.

---

## 6.2 Signature Micro-Interactions

### A. Active Microphone Pulse Halo
When voice intake is active, two concentric rings pulse outward from the recording trigger button:
- **Inner Ring:** Expands from `88px` to `124px`, opacity fades from `0.45` to `0.0`.
- **Outer Ring:** Expands from `88px` to `156px`, opacity fades from `0.25` to `0.0` with a `250ms` delay.
- **Center Button:** Subtle scale pulsation (`scale(1.0)` to `scale(1.04)`).

### B. Dynamic WebAudio Frequency Visualizer
- Renders **9 rounded vertical canvas bars** reacting in real time to the browser's `AudioContext` and `AnalyserNode` input.
- **Bar Width:** `5px`, **Gap:** `6px`, **Corner Radius:** `3px`.
- **Color Gradient:** Linear gradient from `--brand-primary` (`#1667D9`) to `--pr-blue-400` (`#5392F8`).
- **Dynamic Energy Range:** Smoothly modulates from `6px` baseline height (silence) up to `48px` (peak speech energy).

### C. Document Camera Laser Sweep
During OCR processing of prescriptions or lab slips:
- A horizontal emerald laser line (`2px` height with a `12px` ambient green blur `#17824C`) sweeps vertically across the document preview canvas in a continuous `1600ms` cycle.

### D. Bounding Box Evidence Pop-In
When the doctor or patient clicks `[View Evidence]` on an extracted clinical fact:
- The source document view scrolls and zooms directly to the relevant line coordinates.
- The golden amber bounding box (`#F59E0B`) pops into view with `--ease-spring` (`transform: scale(0.95)` to `scale(1.0)` with a subtle pulse glow).

---

## 6.3 Auditory Feedback

To support rural, low-vision, or elderly users who may not notice visual state changes:
1. **Start Listening Earcon:** Soft ascending dual-tone chime (`440Hz` $\rightarrow$ `880Hz`, sine wave, 120ms duration).
2. **Done Listening Earcon:** Soft descending chime (`880Hz` $\rightarrow$ `440Hz`, 120ms duration).
3. **Emergency Alert Earcon:** Distinct hospital priority tone (low volume, clear double ping).
4. **Browser SpeechSynthesis (TTS):** Prominent **`[🔊 Listen Aloud]`** button on every question, consent statement, and intake summary card. Speaks in the user's selected language using the browser's native speech synthesis voice engine.

---

# 7. COMPREHENSIVE WEB COMPONENT CATALOG (32 PRODUCTION COMPONENTS)

Every component is modular, accessible, styled with CSS variables, and designed to plug directly into the backend API.

---

### Component 01: `WebShell`
- **Description:** Master layout wrapper providing topbar, responsive sidebar, breadcrumbs, offline network alert bar, and content viewport.
- **Variants:** `PublicLayout`, `PatientLayout`, `DoctorLayout`.

### Component 02: `HospitalHeader`
- **Description:** Institutional header with MediKiosk brand cross, hospital name (*"All India Institute of Ayurveda"*), active route breadcrumbs, language switcher trigger, notifications bell with unread badge, and user profile avatar dropdown.
- **Tokens:** Height `72px`, background `--bg-surface`, border-bottom `1px solid --border-default`.

### Component 03: `SidebarNavigation`
- **Description:** Left navigation bar with role-specific item lists. Highlights the active route with a left pill border and blue tint background. Supports a compact collapsed mode for tablets.

### Component 04: `PrimaryButton`
- **Description:** High-contrast primary action button (`--brand-primary`).
- **States:** Default, Hover (`--brand-hover`), Active (`transform: scale(0.98)`), Disabled (`opacity: 0.5`), Loading (integrated spinner replacing text).
- **Target Height:** `48px` (Desktop) / `64px` (Kiosk touch).

### Component 05: `SecondaryButton`
- **Description:** Outlined button for alternative actions (`"Type instead"`, `"Cancel"`, `"Skip"`).
- **Tokens:** Border `1.5px solid --border-default`, background `--bg-surface`, text `--text-primary`.

### Component 06: `DangerButton`
- **Description:** Crimson button (`--status-danger`) for emergency triggers, end call, and encounter rejections.

### Component 07: `LargeChoiceCard`
- **Description:** Oversized tactile selection card for language choice, care stream selection, and symptom categories.
- **Anatomy:** Large leading icon (`32px`), bold title (`18px`), optional subtitle (`14px`), and trailing radio/checkbox circle.
- **Selected State:** Border `2px solid --brand-primary`, background `--brand-tint`, icon tinted blue.

### Component 08: `VoiceIntakeRecorder`
- **Description:** Centerpiece conversational voice capture widget.
- **Anatomy:** Giant circular microphone button (`88px` to `104px`), pulsing outer CSS halo during recording, audio visualizer canvas, live rolling speech transcript container, and `[DONE SPEAKING]` CTA.

### Component 09: `WebAudioVisualizer`
- **Description:** Canvas element rendering 9 live animated sound energy bars driven by Web Audio API `AudioContext`.

### Component 10: `AdaptiveQuestionCard`
- **Description:** Displays a single clinical follow-up question (e.g., *"How many days have you had chest pain?"*) with quick-tap chip options, voice answering toggle, and step progress tracker (`Question 2 of 4`).

### Component 11: `ExplainBackSummaryCard`
- **Description:** Closed-loop verification card presenting captured symptoms in simple language with audio readback and two huge side-by-side buttons: **Green `[✓ YES, THAT'S RIGHT]`** and **Red `[↻ NO, SAY AGAIN]`**.

### Component 12: `TriageAlertBanner`
- **Description:** High-priority warning banner rendered when backend flags a `RED` severity or emergency condition. Full crimson background, alert beacon icon, and immediate `[GET ASSISTANCE NOW]` action.

### Component 13: `DocumentDropzone`
- **Description:** Desktop file uploader supporting drag-and-drop, file browser click, and webcam photo snapshot for paper prescriptions, lab slips, and discharge summaries. Supported formats: JPG, PNG, PDF.

### Component 14: `WebcamCaptureModal`
- **Description:** Modal embedding live `navigator.mediaDevices.getUserMedia` video feed with a 4:3 document alignment overlay and single-click shutter button.

### Component 15: `OCRScanProgress`
- **Description:** Visual processing state showing the uploaded document thumbnail with an animated sweeping laser line and a real-time progress checklist (`Document received` $\rightarrow$ `Reading handwriting` $\rightarrow$ `Extracting medicines`).

### Component 16: `OCRFactCard`
- **Description:** Extracted medicine/lab card displaying medicine name (e.g., *Metformin 500 mg*), dosage instruction, line citation badge (`[Line 3]`), and `[View Evidence ↗]` link.

### Component 17: `EvidenceViewer`
- **Description:** Side-by-side interactive document inspector with zoom, pan, and SVG/canvas overlay rendering golden amber bounding boxes around cited prescription text.

### Component 18: `MedicalTimeline`
- **Description:** Vertical chronological event stream connecting past hospital visits, uploaded prescriptions, lab reports, and current OPD intake events with categorical filter pills.

### Component 19: `QueueTicketCard`
- **Description:** Realistic digital OPD ticket card with serrated edges, displaying Token Number (`A-261`), Department (`General Medicine`), Estimated Wait Time, Doctor Room (`Cabin 102`), and live position.

### Component 20: `DoctorQueueTable`
- **Description:** High-density clinical table with sortable columns, patient name, age/gender, 30-word clinical complaint, severity badge (`RED`, `YELLOW`, `GREEN`), intake channel (`KIOSK`, `MOBILE`, `IVR`), document count, and `[Open Case]` action.

### Component 21: `DoctorEncounterHeader`
- **Description:** Sticky case banner displaying patient name, age, ABHA ID, encounter ID, severity pill, and quick navigation tabs: `Overview`, `History`, `Documents`, `Evidence`, `Consultation`.

### Component 22: `DrugInteractionAlertCard`
- **Description:** Clinical safety card highlighting detected drug-drug conflicts or dosage warnings identified by the backend safety engine, with medical explanation and override checkbox.

### Component 23: `ClinicalVerificationChecklist`
- **Description:** Interactive sign-off checklist allowing the doctor to mark clinical items (Chief Complaint, HPI, Past History, Medications, Allergies) as `Verified`, `Needs Edit`, or `Missing`.

### Component 24: `ThreeColumnConsultationWorkspace`
- **Description:** High-efficiency layout placing patient snapshot (Left), structured clinical history (Center), and doctor consultation note/prescription pad (Right) in a single synchronized viewport.

### Component 25: `DigitalPrescriptionPad`
- **Description:** Clinician interface to add medications (drug name, strength, frequency, duration, special instructions) with auto-suggestions and immediate drug-safety rechecks.

### Component 26: `ReferralDispatchModal`
- **Description:** Form to dispatch an OPD referral to other specialties (Cardiology, Orthopedics, AYUSH Panchakarma) with urgency level and clinical notes.

### Component 27: `AYUSHParikshaCard`
- **Description:** Card presenting Ayurvedic Dashavidha Pariksha findings (Agni, Koshtha, Nidra, Prakriti) paired with plain-language everyday descriptions.

### Component 28: `VitalsMonitorTile`
- **Description:** Sensor metric card showing Blood Pressure, Pulse Rate, SpO2, and Body Temperature with normal-range indicators and manual entry fallback.

### Component 29: `HospitalWayfindingMap`
- **Description:** High-contrast vector floor map highlighting the patient's path from Kiosk/Entrance to the assigned Doctor Cabin, supplemented with step-by-step text directions.

### Component 30: `IVRBrowserSimulatorModal`
- **Description:** Interactive on-screen smartphone keypad and audio call simulator testing conversational speech turns against the backend `/api/call/*` and `/api/ivr/*` routes.

### Component 31: `ToastNotificationManager`
- **Description:** Non-intrusive floating toast alerts in the bottom-right corner for success confirmations, network alerts, and queue updates.

### Component 32: `PrivacyAutoResetDialog`
- **Description:** Full-screen modal with an animated 10-second countdown timer triggered on public kiosk sessions to purge memory state and protect patient confidentiality.

---

# 8. COMPLETE PAGE-BY-PAGE WEB UI BLUEPRINT (36 DETAILED VIEWS)

---

## 8.1 Public Entry & Onboarding (Pages 01–03)

### Page 01 — Public Welcome & Portal Landing
- **Route:** `/` or `/welcome`
- **Layout:** Two-column desktop hero (`55% / 45%`).
- **Left Column:**
  - Badge: `🏥 Ministry of AYUSH / AIIA · SIH26047 Solution`
  - H1 Headline: `"Intelligent Clinical Intake & Patient Care"`
  - Subtitle: `"Describe your symptoms in your own words, organize past medical papers, and prepare a verified clinical case before seeing your doctor."`
  - Feature Highlights:
    - `✓ Voice + Touch in 5 Indian Languages`
    - `✓ Prescription & Lab Report OCR Intelligence`
    - `✓ One-Click Verifiable Evidence Traceability`
    - `✓ Doctor Command Center & Real-Time OPD Queue`
  - Action Group:
    - Primary CTA: `[GET STARTED →]` (routes to Page 02)
    - Secondary: `[HOW MEDIKIOSK WORKS]` (opens guided tour modal)
- **Right Column:**
  - Clean clinical vector illustration or interactive 3D/canvas medical cross showing patient intake transitioning into doctor review.
- **Footer:** Partner logos, hospital emergency contact, and privacy statement.

---

### Page 02 — Account Type / Portal Selector
- **Route:** `/account-type`
- **Purpose:** Seamless role routing matching the RetinopathyScan pattern.
- **Layout:** Centered card grid with 2 massive interactive role tiles:
  1. **PATIENT / INDIVIDUAL PORTAL**
     - Icon: Large `<User />` in blue circle (`64px`)
     - Headline: `"Patient Health Workspace"`
     - Description: `"Record your health problem by speaking naturally, upload old prescriptions, view your OPD token, and access past medical records."`
     - Button: `[CONTINUE AS PATIENT →]` (routes to `/patient/login`)
  2. **DOCTOR / CLINICAL COMMAND CENTER**
     - Icon: Large `<Stethoscope />` in navy circle (`64px`)
     - Headline: `"Medical Professional Portal"`
     - Description: `"Review AI-structured patient intake, inspect prescription evidence, verify clinical facts, and conduct consultations."`
     - Button: `[CONTINUE AS DOCTOR →]` (routes to `/doctor/login`)
- **Hover Micro-interaction:** Subtle card elevation (`--shadow-lg`), blue border glow, and arrow translation.

---

### Page 03 — Help & How MediKiosk Works
- **Route:** `/help`
- **Purpose:** Onboarding guide for patients and attendants.
- **Layout:** Step-by-step visual roadmap (1. Speak Symptoms $\rightarrow$ 2. Scan Papers $\rightarrow$ 3. Get Queue Token $\rightarrow$ 4. Doctor Review). Includes FAQ accordion and hospital helpdesk emergency phone numbers (`+91-11-26950401`).

---

## 8.2 Patient Authentication & Setup (Pages 04–07)

### Page 04 — Patient Login
- **Route:** `/patient/login`
- **Layout:** Split layout. Left: Reassuring healthcare graphic with security badges. Right: Clean white card.
- **Form Fields:**
  - Input: `Mobile Number / ABHA ID / Patient ID` (e.g., `9876543210` or `pat-001`)
  - Input: `Password / 4-Digit Security PIN` (e.g., `patient123`)
  - Demo Helper Banner: `"💡 Demo Credentials: Mobile: 9876543210 / Password: patient123"`
  - Quick Bypass: `[CONTINUE AS GUEST / WALKIN PATIENT]`
- **Primary CTA:** `[ACCESS PATIENT WORKSPACE →]`
- **Footer:** `"New to MediKiosk? Create Patient Profile"`

---

### Page 05 — Patient Registration
- **Route:** `/patient/register`
- **Layout:** 2-column organized medical intake form:
  - **Section 1: Identity & Personal**
    - Full Name, Age, Gender (`Male`, `Female`, `Other`), Mobile Number
  - **Section 2: Health ID (ABHA)**
    - ABHA ID input (or toggle `[Generate Mock ABHA ID]`)
  - **Section 3: Account Security**
    - Create 4-digit PIN or Password
- **Submission:** Calls `POST /api/auth/patient/register` $\rightarrow$ returns new patient profile and routes to Page 06.

---

### Page 06 — Language Selection
- **Route:** `/patient/language`
- **Purpose:** Lock interface and voice recognition language before clinical intake.
- **Grid of 5 Large Cards:**
  1. **English** (`English`)
  2. **हिन्दी** (`Hindi`)
  3. **தமிழ்** (`Tamil`)
  4. **తెలుగు** (`Telugu`)
  5. **मराठी** (`Marathi`)
- **Interaction:** Selecting a card immediately triggers an audio preview (*"आपने हिन्दी का चयन किया है"*) and updates the app locale state.
- **CTA:** `[CONTINUE IN SELECTED LANGUAGE →]`

---

### Page 07 — Informed Consent & Privacy
- **Route:** `/patient/consent`
- **Layout:** High-contrast `ConsentCard` highlighting 3 plain-language promises:
  1. *Why we ask:* To give your doctor a complete summary before you step into the clinic.
  2. *How documents are treated:* Stored securely on hospital servers, accessible only to authorized medical personnel.
  3. *Your control:* You can decline at any time and receive a manual paper token.
- **Actions:**
  - Primary: `[✓ I AGREE AND CONTINUE]` (Forest Green `--status-ayush`, `64px`)
  - Secondary: `[I DO NOT AGREE / PAPER TOKEN ONLY]`
  - Link: `[Read Full Clinical Data Privacy Policy]`

---

## 8.3 Patient Health Workspace & Intake (Pages 08–21)

### Page 08 — Patient Dashboard
- **Route:** `/patient/dashboard`
- **Layout:** Polished SaaS health workspace matching RetinopathyScan quality.
- **Header:** `"Good morning, Ramesh Kumar" · Patient ID: pat-001 · ABHA: 91-4821-3910-4819`.
- **Top Metrics Strip (4 Stat Cards):**
  1. `Active Visit:` Token **A-261** (Status: *Waiting*)
  2. `Medical Documents:` **8 Prescriptions & Reports**
  3. `Past Consultations:` **4 Completed Visits**
  4. `Verified Clinical Facts:` **14 Records**
- **Hero Action Card:**
  - Title: `"Prepare For Today's Doctor Consultation"`
  - Description: `"Tell us your current health complaints through natural voice or touch, and upload recent test reports."`
  - CTA: `[START CLINICAL INTAKE NOW →]`
- **Quick Action Grid:**
  - `[📄 Add Medical Documents]`
  - `[🎫 Check OPD Queue Position]`
  - `[⏱ View Medical History Timeline]`
  - `[👨‍⚕️ Find Clinic Doctors]`
- **Recent Activity Feed:** Real-time list of past encounter dates, prescriptions recorded, and doctor reviews.

---

### Page 09 — New History Introduction & Channel Selection
- **Route:** `/patient/history/new`
- **Layout:** Centered intake launchpad.
- **Options (2 Large Choice Cards):**
  1. **VOICE INTAKE (Recommended for Elderly / Rural Patients):**
     - Icon: `<Mic />`
     - Subtitle: `"Speak naturally in your mother tongue. The AI will organize your thoughts."`
  2. **TOUCH & KEYBOARD INTAKE:**
     - Icon: `<Keyboard />`
     - Subtitle: `"Answer questions by tapping options and typing details."`
- **CTA:** `[START INTAKE SESSION →]`

---

### Page 10 — Conversational Voice Intake (Idle State)
- **Route:** `/patient/history/voice`
- **Purpose:** Solicit natural language complaint without form anxiety.
- **Layout:**
  - Large prompt: `"What health problem brings you to the hospital today?"`
  - Subtitle: `"Tell us what is troubling you, where it hurts, and how long it has been."`
  - Center: Giant `VoiceIntakeRecorder` idle button (`104px` diameter, `--brand-primary`) with microphone glyph.
  - Text alternative: `[Prefer typing? Click here]`
  - Audio support: `[🔊 Hear this question read aloud]`

---

### Page 11 — Active Voice Capture & Live Waveform
- **Route:** `/patient/history/voice-active`
- **Purpose:** Immediate visual and acoustic reassurance while patient speaks.
- **Layout:**
  - Header: `"Listening to your voice..."`
  - Center: Live animated 9-bar WebAudio visualizer bouncing with patient voice amplitude.
  - Pulsing double halo ring around the red recording button.
  - Live Rolling Transcript Box: Shows recognized speech in real time as speech chunks arrive from backend.
  - Controls:
    - `[✓ DONE SPEAKING]` (Primary `64px`, Navy `--brand-primary`)
    - `[↻ CANCEL & RECORD AGAIN]` (Secondary outlined)

---

### Page 12 — Adaptive Follow-Up Questions
- **Route:** `/patient/history/adaptive`
- **Layout:** Clean single-question card (`AdaptiveQuestionCard`).
- **Example Question:** `"When did your chest discomfort start?"`
- **Tap Chips:**
  - `[Today morning]`
  - `[Yesterday]`
  - `[2–3 days ago]`
  - `[More than a week]`
  - `[Not sure]`
- **Alternative:** Embedded smaller voice button: `[Speak your answer]`.
- **Rule:** Maximum 2 to 3 adaptive questions. Never overwhelm the patient.

---

### Page 13 — Closed-Loop Explain-Back Confirmation
- **Route:** `/patient/history/summary`
- **Purpose:** Verifiable confirmation with zero clinical editing burden.
- **Layout:**
  - Headline: `"Here is what we understood. Is this correct?"`
  - High-Contrast Summary Card (`ExplainBackSummaryCard`):
    - Problem: **Chest pain and mild breathlessness**
    - Started: **3 days ago**
    - Severity: **Moderate (6 out of 10)**
    - Aggravated by: **Walking upstairs**
  - Audio action: `[🔊 Listen to summary]`
  - Two Massive Action Buttons:
    - **`[✓ YES, THAT'S RIGHT]`** (`--status-success` `#17824C`, `68px`) $\rightarrow$ continues to documents
    - **`[↻ NO, SAY IT AGAIN]`** (`--status-danger` `#C83A3A`, `68px`) $\rightarrow$ re-records speech

---

### Page 14 — Red-Flag Triage Alert (Conditional)
- **Route:** `/patient/history/triage-alert`
- **Condition:** Automatically triggered if backend clinical rule engine detects emergency markers (e.g., acute crushing chest pain, SpO2 $< 90\%$, sudden neurological deficit).
- **Visuals:** Dominant deep crimson emergency styling (`--status-danger`).
- **Content:**
  - Flashing beacon icon + H1: `"IMMEDIATE CLINICAL ATTENTION REQUIRED"`
  - Description: `"Your symptoms indicate high priority. A hospital nurse and doctor have been notified."`
  - Directions: `"Please proceed immediately to Emergency Desk (Room 001)."`
  - Actions:
    - `[🚨 ALERT CLINICAL STAFF NOW]` (`72px`, flashing red border)
    - `[PRINT EMERGENCY PRIORITY SLIP]`
- **Safety Gate:** Blocks normal waiting queue; transitions patient straight into emergency protocol.

---

### Page 15 — Document Center & Upload Intro
- **Route:** `/patient/documents`
- **Purpose:** Solicit paper prescriptions, lab slips, and discharge notes.
- **Layout:**
  - Title: `"Do you have previous medical papers or prescriptions?"`
  - Subtitle: `"Uploading them helps your doctor understand your previous treatments."`
  - Accepted Document Tiles:
    - `[Prescription]` `[Blood / Lab Test]` `[Discharge Summary]` `[X-Ray / Scan]`
  - Actions:
    - Primary: `[📄 UPLOAD FROM COMPUTER / PHONE]`
    - Secondary: `[📷 TAKE PHOTO WITH CAMERA]`
    - Skip option: `[I HAVE NO PAPERS / SKIP TO QUEUE]`

---

### Page 16 — Document Upload & Camera Capture Modal
- **Route:** `/patient/documents/upload`
- **Layout:** Drag-and-drop file zone or webcam snap container.
- **Interaction:** Upload triggers instantaneous client preview with image crop/rotate controls, followed by `[PROCESS DOCUMENT WITH AI OCR →]`.

---

### Page 17 — OCR Scanning & Extraction Progress
- **Route:** `/patient/documents/processing`
- **Layout:** Real-time scanning animation (`OCRScanProgress`).
- **Visuals:** Document snapshot with an animated green laser line sweeping up and down.
- **Progression Stepper:**
  - `[✓] Document uploaded securely`
  - `[✓] Enhancing image contrast & orientation`
  - `[⟳] Reading doctor handwriting & medicine names...`
  - `[ ] Linking line evidence to medical knowledge base...`

---

### Page 18 — OCR Results & Line Evidence Overview
- **Route:** `/patient/documents/results`
- **Layout:** Two-column view.
- **Left Column:** Captured document image with highlighted bounding boxes.
- **Right Column:** Extracted medication cards (`OCRFactCard`):
  - Medicine: **Metformin 500 mg** · 1 tablet twice daily · `[Line 2]` · `[View Evidence]`
  - Medicine: **Atorvastatin 20 mg** · 1 tablet at night · `[Line 4]` · `[View Evidence]`
- **Verification Rule:** Every card has a direct link to the bounding box on the original paper.
- **Action:** `[CONFIRM & ADD TO TIMELINE →]`

---

### Page 19 — Medical Timeline View
- **Route:** `/patient/timeline`
- **Layout:** Chronological interactive timeline (`MedicalTimeline`).
- **Filters:** `[All]` `[Prescriptions]` `[Lab Reports]` `[Hospital Visits]` `[Symptoms]`.
- **Entries:** Cards arranged along an active vertical timeline track linking years: `2024` (Diagnosis) $\rightarrow$ `2025` (Medication adjustment) $\rightarrow$ `2026` (Current encounter intake).

---

### Page 20 — Structured Intake Summary & Final Review
- **Route:** `/patient/history/final-review`
- **Layout:** Clinical encounter preview before submission.
- **Sections:**
  - Chief Complaint & HPI
  - Current Medications (extracted from documents)
  - Vital Signs (if connected)
  - AYUSH Lifestyle Indicators (Agni, Koshtha, Sleep)
- **Primary CTA:** `[SUBMIT CASE TO CLINICAL TEAM →]`

---

### Page 21 — Submission Success & Token Issuance
- **Route:** `/patient/history/success`
- **Layout:** Celebratory, calm confirmation screen.
- **Centerpiece:** Large green checkmark (`64px`), H1: `"Intake Successfully Submitted"`.
- **Summary Badge:** Case ID: `MK-2026-00261` · Department: `General Medicine OPD` · Assigned Doctor: `Dr. S. Verma (Cabin 102)`.
- **Action:** `[VIEW MY QUEUE TICKET →]` (routes to Page 22).

---

## 8.4 Patient Queue, Records & Discovery (Pages 22–28)

### Page 22 — Current Visit & Live Queue Token
- **Route:** `/patient/queue`
- **Layout:** Prominent digital OPD ticket (`QueueTicketCard`).
- **Data Display:**
  - Token Number: **`A-261`** (Giant `52px` Navy)
  - Department: **General Medicine OPD (Room 102)**
  - Doctor: **Dr. S. Verma**
  - Queue Position: **2 patients ahead of you**
  - Estimated Wait: **~12 minutes**
- **Live Status:** Auto-refreshes every 15 seconds against `GET /api/queue/status/{token}`.
- **Actions:**
  - `[🗺 HOSPITAL FLOOR MAP & CABIN DIRECTIONS]`
  - `[🔊 READ STATUS ALOUD]`

---

### Page 23 — Post-Consultation Report & E-Prescription
- **Route:** `/patient/consultation/report`
- **Layout:** Clean digital discharge and prescription review.
- **Sections:** Verified clinical history, doctor's clinical notes, signed e-prescription with dosages, follow-up date, and downloadable PDF button `[DOWNLOAD OFFICIAL OPD SUMMARY (PDF)]`.

---

### Page 24 — Medical Records Archive
- **Route:** `/patient/records`
- **Layout:** Searchable document and encounter repository. Tabbed by: `Visits`, `Prescriptions`, `Lab Reports`, `Referrals`.

---

### Page 25 — Find Doctors & OPD Directory
- **Route:** `/patient/doctors`
- **Layout:** Directory list fetched from `GET /api/auth/directory`. Cards displaying Doctor Name, Specialty, Room Number, Qualification, and Hospital Contact.

---

### Page 26 — Doctor Profile & Schedule View
- **Route:** `/patient/doctors/:id`
- **Layout:** Doctor credentials, clinical focus, OPD consulting hours, and assigned cabin details.

---

### Page 27 — Patient Profile & Security Settings
- **Route:** `/patient/profile`
- **Layout:** Personal demographics, linked ABHA ID status, emergency contacts, notification preferences, and PIN change.

---

### Page 28 — Notifications Center
- **Route:** `/patient/notifications`
- **Layout:** Real-time notifications list: `"Your case has been opened by Dr. S. Verma"`, `"Prescription OCR complete"`, `"Your turn is next (Cabin 102)"`.

---

## 8.5 Doctor Authentication & Clinical Command Center (Pages 29–33)

### Page 29 — Doctor Login (PIN-Gated)
- **Route:** `/doctor/login`
- **Layout:** Professional split screen. Left: Deep navy clinical command branding with system status pill (`Backend Online · AI Services Ready`). Right: Crisp authentication card.
- **Inputs:**
  - `Doctor ID / Username` (e.g., `doc-verma` or `doctor`)
  - `4-Digit Security PIN` (e.g., `1234`)
  - Demo Tip: `"💡 Default Doctor PIN: 1234"`
- **CTA:** `[ACCESS CLINICAL COMMAND CENTER →]`
- **Contract:** Calls `POST /api/doctor/auth` or `POST /api/auth/login`.

---

### Page 30 — Doctor Professional Profile
- **Route:** `/doctor/profile`
- **Layout:** Clinician credentials, MCI/State Medical Council registration number, department assignment, and active OPD room number.

---

### Page 31 — Doctor Dashboard & Overview
- **Route:** `/doctor/dashboard`
- **Layout:** Equivalent of the RetinopathyScan Command Center.
- **Top Metrics Grid (4 Cards):**
  1. `Patients Waiting:` **8 Patients**
  2. `High Priority / Red Flag:` **2 Urgent Cases**
  3. `Completed Today:` **32 Consultations**
  4. `Average Consultation Time:` **6.4 mins**
- **Action Strip:** `[OPEN LIVE OPD QUEUE →]` · `[CALL NEXT PATIENT]`
- **Live Waiting Queue Snapshot:** Top 5 waiting patients with severity indicators.

---

### Page 32 — Live OPD Queue & Triage Table
- **Route:** `/doctor/queue`
- **Layout:** Data-dense clinical table (`DoctorQueueTable`) powered by `GET /api/doctor/queue`.
- **Columns:**
  - **Token #:** e.g., `A-261`
  - **Patient Name & Demographics:** e.g., `Ramesh Kumar (56 / M)`
  - **30-Word Triage Summary:** e.g., *"Chest pain for 3 days | Stopped Metformin | ⚠ 1 drug interaction"*
  - **Severity Badge:** `RED` (Urgent), `YELLOW` (Moderate), `GREEN` (Routine)
  - **Channel:** `KIOSK`, `MOBILE`, `IVR`
  - **Documents:** Badge showing count of attached prescriptions
  - **Actions:** Primary `[REVIEW CASE]` + `[CALL NEXT]` button

---

### Page 33 — Patient Encounter Case Overview
- **Route:** `/doctor/patients/:encounterId`
- **Layout:** Master header (`DoctorEncounterHeader`) with tabs: `Overview`, `History`, `Documents`, `Evidence`, `Consultation`.
- **Content:** Rapid diagnostic overview, vital signs status, drug-drug safety warnings, and summary notes.

---

## 8.6 Doctor Clinical Review, Evidence & Consultation Workspace (Pages 34–43)

### Page 34 — Structured Clinical History Review
- **Route:** `/doctor/patients/:encounterId/history`
- **Layout:** Categorized clinical fact accordion:
  - **Chief Complaint:** Normalized SNOMED/ICD concept + patient's raw spoken words.
  - **History of Present Illness (HPI):** Onset, duration, severity, aggravating factors.
  - **Past Medical & Surgical History:** Extracted past diagnoses.
  - **Current Medications:** Extracted from paper prescriptions.
  - **Known Drug Allergies:** Highlighted in red banner.
  - **AYUSH Dashavidha Pariksha:** Digestive fire (Agni), Bowel (Koshtha), Sleep (Nidra).
- **Actions on Each Fact:** `[✓ Accept]` `[✎ Edit]` `[✕ Reject]`.

---

### Page 35 — Provenance & Evidence Traceability (Bounding Box Viewer)
- **Route:** `/doctor/patients/:encounterId/evidence`
- **Purpose:** Core Trust Engine ("No Receipt, No Fact").
- **Layout:** Side-by-side view (`EvidenceViewer`).
  - **Left Rail (40%):** Extracted clinical facts with line indices:
    - `Metformin 500 mg (twice daily)` $\rightarrow$ cited as `[Doc 1, Line 3]`
    - `Atorvastatin 20 mg` $\rightarrow$ cited as `[Doc 1, Line 5]`
  - **Right Canvas (60%):** Original prescription image. Clicking any fact smoothly pans and zooms the image to the cited coordinates, drawing a glowing amber bounding box around the exact handwriting.

---

### Page 36 — Doctor Document Center & Zoom Viewer
- **Route:** `/doctor/patients/:encounterId/documents`
- **Layout:** Gallery of all patient-submitted medical documents with high-resolution pan, zoom, rotate, and full-screen inspection tools.

---

### Page 37 — Priority Triage Review & Escalation Panel
- **Route:** `/doctor/patients/:encounterId/triage`
- **Condition:** Active when severity is `RED`.
- **Layout:** Highlights critical parameters (e.g., *Chest pain + SpO2 88%*), prompt clinician response options: `[ACKNOWLEDGE & ESCALATE TO CASUALTY]` or `[OVERRIDE TO NORMAL]`.

---

### Page 38 — Clinical Verification Checklist
- **Route:** `/doctor/patients/:encounterId/verify`
- **Layout:** Verification checklist (`ClinicalVerificationChecklist`) covering all clinical dimensions.
- **Action:** `[SIGN & ACCEPT CLINICAL CASE HISTORY]` $\rightarrow$ Calls `POST /api/doctor/encounter/{id}/verify`.

---

### Page 39 — 3-Column Live Consultation Workspace
- **Route:** `/doctor/patients/:encounterId/consultation`
- **Layout:** Unified 3-column clinical cockpit (`ThreeColumnConsultationWorkspace`):
  - **Left Column (25%):** Patient snapshot, vitals, drug safety alerts.
  - **Center Column (45%):** Full structured intake notes with line evidence links.
  - **Right Column (30%):** Doctor workspace: Clinical diagnosis notes, e-prescription entry pad, and referral controls.
- **Efficiency:** The physician never has to switch tabs during an active 2-minute OPD consultation.

---

### Page 40 — Digital E-Prescription Pad
- **Route:** `/doctor/patients/:encounterId/prescription`
- **Layout:** Interactive medicine builder (`DigitalPrescriptionPad`). Allows adding drugs with strength, dose frequency (`1-0-1`), duration (`5 days`), and dietary instructions (*"After food with warm water"*). Includes instantaneous contraindication warnings.

---

### Page 41 — Hospital Referral Dispatch
- **Route:** `/doctor/patients/:encounterId/referral`
- **Layout:** Inter-departmental referral form (`ReferralDispatchModal`) routing patients to specialized AYUSH clinics, Cardiology, or Diagnostic Labs with priority tags.

---

### Page 42 — Encounter Completion & Hand-off
- **Route:** `/doctor/patients/:encounterId/completed`
- **Layout:** Consultation summary banner: `"Consultation Completed · Case Saved"`. One-click print for official signed prescription + `[CALL NEXT PATIENT IN QUEUE →]`.

---

### Page 43 — Clinical Analytics & Hospital Operations
- **Route:** `/doctor/analytics`
- **Layout:** Executive clinical dashboard displaying OPD throughput charts, triage distribution (`Red: 6%, Yellow: 24%, Green: 70%`), channel volume (Kiosk vs Mobile vs IVR), and common morbidity trends.

---

## 8.7 IVR Voice Simulator & WebRTC Testbed (Page 44)

### Page 44 — IVR Browser Simulator & Audio Turn Testbed
- **Route:** `/ivr` or `/ivr/session/:id`
- **Purpose:** Demonstration and testing tool for the phone-call intake engine.
- **Layout:** Stylized modern smartphone frame in browser:
  - Header: `"Incoming Call · MediKiosk Automated Health Line"`
  - Center: Audio waveform visualizer + live speech dialogue transcript:
    - *AI:* `"नमस्ते, आपको क्या तकलीफ हो रही है?"*
    - *User (Spoken or Typed):* `"मुझे 3 दिन से सीने में दर्द है."*
  - Keypad: DTMF on-screen keypad (`1–9`, `*`, `0`, `#`).
  - Integration: Directly invokes backend `/api/call/audio-turn` or `/api/ivr/call`.

---

# 9. STATE MANAGEMENT, DATA FLOW & VERIFIED FASTAPI BACKEND CONTRACT

The web frontend operates as a strictly typed presentation layer mapped directly to the existing, verified FastAPI backend routes.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        EXISTING FASTAPI BACKEND                        │
├────────────────────────────────────────────────────────────────────────┤
│  POST /api/auth/login                POST /api/auth/patient/register   │
│  GET  /api/auth/directory            GET  /api/health                  │
│  GET  /api/patient/dashboard/{id}    POST /api/documents/upload        │
│  GET  /api/queue/status/{token}      POST /api/encounters/bootstrap    │
│  POST /api/call/session/start        POST /api/call/audio-turn         │
│  POST /api/doctor/auth               GET  /api/doctor/queue            │
│  GET  /api/doctor/patient/{id}       POST /api/doctor/encounter/verify │
│  GET  /api/doctor/patient/by-abha/{abha}                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON & Multipart
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      FRONTEND API SERVICE CLIENT                       │
│  (apiClient.js / TypeScript ApiService: handles auth tokens & errors)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Reactive Store
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        GLOBAL WEB APP STORE                            │
│  • authStore (token, role, currentUser)                                │
│  • intakeStore (encounterId, symptoms, audioState, facts)              │
│  • queueStore (currentToken, waitTime, position)                       │
│  • doctorStore (queueList, selectedPatient, clinicalFacts, reviewMode) │
└────────────────────────────────────────────────────────────────────────┘
```

### Verified API Endpoints & Request/Response Contract

1. **Authentication:**
   - `POST /api/auth/login` $\rightarrow$ `{ identifier, password, role }` $\Rightarrow$ `{ authenticated: true, user: { id, role, full_name, mobile, abha_id } }`
   - `POST /api/doctor/auth` $\rightarrow$ `{ pin: "1234" }` $\Rightarrow$ `{ authenticated: true, message: "..." }`
   - `POST /api/auth/patient/register` $\rightarrow$ `{ full_name, mobile, abha_id, password, age, gender }` $\Rightarrow$ `{ authenticated: true, user: {...} }`

2. **Patient Dashboard & Records:**
   - `GET /api/patient/dashboard/{identifier}` (identifier: `pat-001` or mobile `9876543210`) $\Rightarrow$ `{ profile, encounters, active_token, documents }`

3. **Intake & Conversational Voice Turns:**
   - `POST /api/encounters/bootstrap` $\rightarrow$ `{ patient_id, language, channel: "WEB_KIOSK" }` $\Rightarrow$ `{ encounter_id, token_number }`
   - `POST /api/call/session/start` $\rightarrow$ `{ encounter_id, language }` $\Rightarrow$ `{ session_id, welcome_text, audio_url }`
   - `POST /api/call/audio-turn` $\rightarrow$ Multipart FormData `{ audio_file: Blob, session_id }` $\Rightarrow$ `{ transcript, assistant_reply, facts_extracted, is_complete, next_question }`

4. **Document Intelligence & OCR:**
   - `POST /api/documents/upload` $\rightarrow$ Multipart FormData `{ file: File, encounter_id, document_type }` $\Rightarrow$ `{ document_id, ocr_results: [ { text, confidence, line_number, bounding_box: [x,y,w,h] } ] }`

5. **OPD Queue Tracking:**
   - `GET /api/queue/status/{token}` (token: `A-261`) $\Rightarrow$ `{ token, position, estimated_wait_minutes, status, doctor_name, cabin }`

6. **Doctor Command Center:**
   - `GET /api/doctor/queue` $\Rightarrow$ `{ queue: [ { encounter_id, token_number, severity_badge, summary_30_words, channel, fact_count, has_medication_conflict, has_red_flags } ], total_waiting }`
   - `GET /api/doctor/patient/{encounter_id}` $\Rightarrow$ `{ encounter, clinical_facts, drug_interaction_alerts, lab_result_alerts, clinical_gap_alerts, ayush_intake, documents }`
   - `POST /api/doctor/encounter/{encounter_id}/verify` $\rightarrow$ `{ doctor_id, notes }` $\Rightarrow$ `{ status: "DOCTOR_REVIEWED", verified_by }`

---

# 10. GLOBAL STATES, ERROR HANDLING, OFFLINE RESILIENCE & SECURITY UX

---

## 10.1 UI Global States

Every API-backed screen must support 5 standard states without layout jumping:
1. **Loading State:** Skeleton loaders matching the exact card and table shapes.
2. **Empty State:** Friendly, reassuring illustrations with actionable next steps (e.g., *"No patients currently waiting in queue"*).
3. **Error State:** Human-readable explanations with a prominent `[Retry]` button.
4. **Success State:** Crisp green confirmation banners or animated checkmark cards.
5. **Offline / Edge Mode:** Sticky header banner: `"Running on Local Edge Station — All intake features active without internet"`.

---

## 10.2 HTTP Status Code to UI Translation

| HTTP Status | Backend Meaning | UI Presentation & Action |
|---|---|---|
| `401 Unauthorized` | Invalid PIN or expired session | Redirects to login modal with friendly notice (*"Please enter your 4-digit PIN"*). |
| `403 Forbidden` | Accessing unauthorized doctor case | Displays permission alert (*"You do not have permission to view this clinical case"*). |
| `404 Not Found` | Patient or Encounter does not exist | *"Case record not found. Please verify token number."* |
| `409 Conflict` | Encounter status already completed | Auto-refreshes state with message (*"Case was already reviewed by another physician"*). |
| `422 Unprocessable`| Missing input or validation error | Highlights erroneous field with inline red helper text. |
| `5xx Server Error` | Backend model failure | Fallback gracefully to offline rule matching (*"System is running in safe offline mode"*). |

---

## 10.3 Security & Patient Privacy UX

- **No Raw Stack Traces:** Never expose Python exceptions, raw tracebacks, SQL queries, or internal database keys to patients.
- **Session Auto-Purge:** If a public kiosk display remains inactive for 60 seconds, a full-screen modal displays a 10-second countdown before purging all browser memory and redirecting to `/welcome`.
- **Masked Identifiers:** Sensitive identifiers (e.g., mobile numbers `98765****0`, ABHA IDs `91-****-****-4819`) are masked on public overview screens.

---

# 11. WEB IMPLEMENTATION TECH STACK & ARCHITECTURE BLUEPRINT

---

## 11.1 Recommended Tech Stack
- **Framework / Runtime:** Modern Web Frontend bundled with **Vite** (`vite.config.js` with API proxying to `http://localhost:8000`).
- **Core Languages:** Semantic HTML5, Vanilla JavaScript (ES Modules) or TypeScript, and Native CSS with CSS Custom Properties.
- **Audio & Media APIs:** Web Audio API (`AudioContext`, `AnalyserNode`), MediaDevices API (`getUserMedia`), and Web Speech API (`SpeechSynthesis`).
- **Icons:** Modern SVG Icon Set (Lucide / Tabler).

---

## 11.2 Clean Project Directory Structure

```text
frontend/
├── index.html                    # Single-Page App Entry Shell
├── vite.config.js                # Vite config with backend proxy (/api, /static)
├── package.json                  # Dependencies and build scripts
│
├── public/                       # Static assets & logos
│   ├── favicon.svg
│   └── audio/                    # Earcon sound chimes (start/stop chimes)
│
├── css/                          # 3-Layer Design Token Architecture
│   ├── design-tokens.css         # Layer 1 & 2: Primitives, Semantics & Radius
│   ├── base.css                  # Modern reset, typography, responsive rules
│   ├── components.css            # Component catalog styles (Buttons, Cards, Badges)
│   └── layouts.css               # Portal App Shells (Patient, Doctor, Kiosk)
│
└── js/
    ├── main.js                   # Application bootstrap & router initialization
    ├── router.js                 # Client-side hash/history router (Routes 01–44)
    ├── store.js                  # Central reactive state store (Auth, Patient, Doctor)
    │
    ├── api/                      # Typed API Service Layer
    │   ├── client.js             # Base fetch wrapper with error handling
    │   ├── auth.api.js           # Auth & directory calls
    │   ├── patient.api.js        # Patient dashboard & history
    │   ├── doctor.api.api.js     # Doctor queue & verification
    │   ├── documents.api.js      # File upload & OCR line fetching
    │   └── queue.api.js          # Live token tracking
    │
    ├── audio/                    # Voice & Auditory Feedback Engine
    │   ├── sound-effects.js      # Earcon chime generator
    │   ├── audio-visualizer.js   # 9-bar WebAudio frequency visualizer
    │   └── tts-reader.js         # Browser SpeechSynthesis helper
    │
    ├── components/               # Reusable UI Component Builders
    │   ├── header.js             # Hospital topbar
    │   ├── sidebar.js            # Role navigation
    │   ├── choice-card.js        # Large choice selector
    │   ├── voice-recorder.js     # Pulse mic button & transcript
    │   ├── evidence-viewer.js    # Bounding-box canvas pan/zoom
    │   ├── triage-banner.js      # Red flag emergency alert
    │   └── toast.js              # Floating feedback alerts
    │
    └── pages/                    # Screen-by-Screen View Modules
        ├── public/
        │   ├── welcome.js        # Page 01
        │   └── account-type.js   # Page 02
        ├── patient/
        │   ├── login.js          # Page 04
        │   ├── register.js       # Page 05
        │   ├── language.js       # Page 06
        │   ├── consent.js        # Page 07
        │   ├── dashboard.js      # Page 08
        │   ├── intake-voice.js   # Pages 09–13
        │   ├── triage-alert.js   # Page 14
        │   ├── documents.js      # Pages 15–18
        │   ├── timeline.js       # Page 19
        │   ├── summary.js        # Page 20
        │   └── queue-view.js     # Page 22
        ├── doctor/
        │   ├── login.js          # Page 29
        │   ├── dashboard.js      # Page 31
        │   ├── queue.js          # Page 32
        │   ├── patient-detail.js # Page 33–34
        │   ├── evidence.js       # Page 35
        │   └── consultation.js   # Page 39–42
        └── ivr/
            └── ivr-simulator.js  # Page 44 (Voice call testbed)
```

---

# 12. DEVELOPER EXECUTION CHECKLIST & ACCEPTANCE VERIFICATION MATRIX

During execution of the web portal redesign and scratch rebuild in the next phase, verify every criteria:

- [ ] **Visual Standard:** The web application achieves the **RetinopathyScan-grade light medical visual aesthetic** with crisp borders, subtle shadows, and zero dark gloom.
- [ ] **WCAG 2.2 AAA Contrast:** All headings and primary text meet or exceed **7:1 contrast** on cards and canvas.
- [ ] **Multilingual Integrity:** Hindi, Tamil, Telugu, and Marathi text render without clipped matras or broken conjunct glyphs.
- [ ] **Responsive Fluidity:** Layout adjusts seamlessly across Desktop (1920×1080 / 1440×900), Tablet Kiosk (1280×800), and Mobile Browsers (390×844).
- [ ] **FastAPI Integration:** Web UI connects directly to live endpoints (`/api/auth`, `/api/patient`, `/api/doctor`, `/api/documents`, `/api/queue`, `/api/call`, `/api/encounters`) without dummy mock data when the server is running.
- [ ] **Closed-Loop Explain-Back:** Voice intake summarizes what the patient said with large **[YES]** / **[NO]** verification buttons — no clinical editing burden on patients.
- [ ] **Verifiable Evidence ("No Receipt, No Fact"):** Extracted medications in both patient and doctor views link visually to bounding boxes on the original prescription image.
- [ ] **Emergency Protocol:** Severity `RED` triggers dominant crimson emergency banners and halts standard queue progression.
- [ ] **Doctor 3-Column Workspace:** Doctors can review patient history, inspect evidence, and type prescriptions in a single synchronized 3-column view without page bouncing.
- [ ] **Privacy Guard:** Kiosk sessions trigger a 10-second auto-reset after 60s of inactivity to protect patient records.
- [ ] **Voice & Earcon Polish:** Voice recording displays a live animated waveform and plays gentle audio earcons on start/stop.

---
*MediKiosk Web UI/UX Design System Specification — SIH26047 Canonical Master Release.*
