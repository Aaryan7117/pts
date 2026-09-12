import 'package:flutter/material.dart';

/// MediKiosk Dimensions & Spacing Architecture
/// 4dp / 8dp Base Spacing Grid, Radius Tokens, Elevation Tokens & Touch Targets
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 2.1 & 4.2
abstract class MediDimensions {
  // ============================================================
  // SPACING SCALE (4dp / 8dp Grid)
  // ============================================================
  static const double space2 = 2.0;
  static const double space4 = 4.0;
  static const double space8 = 8.0;
  static const double space12 = 12.0;
  static const double space16 = 16.0;
  static const double space20 = 20.0;
  static const double space24 = 24.0;
  static const double space32 = 32.0;
  static const double space40 = 40.0;
  static const double space48 = 48.0;
  static const double space64 = 64.0;
  static const double space80 = 80.0;

  // ============================================================
  // TOUCH TARGET SIZES (Elderly & High-Stress Friendly)
  // ============================================================
  static const double minTouchTarget = 64.0; // Hard minimum for any clickable area
  static const double primaryCtaHeight = 72.0; // Standard primary action button height
  static const double secondaryCtaHeight = 64.0;
  static const double voiceButtonSize = 100.0; // Large circular microphone button
  static const double choiceCardMinHeight = 84.0;

  // ============================================================
  // BORDER RADIUS SCALE
  // ============================================================
  static const double radiusNone = 0.0;
  static const double radiusSm = 6.0; // Badges, evidence tags
  static const double radiusMd = 12.0; // Secondary buttons, input fields
  static const double radiusLg = 16.0; // Standard cards, choice cards, dialogs
  static const double radiusXl = 24.0; // Primary CTA buttons, hero containers
  static const double radiusFull = 999.0; // Circular buttons, pills

  static final BorderRadius borderSm = BorderRadius.circular(radiusSm);
  static final BorderRadius borderMd = BorderRadius.circular(radiusMd);
  static final BorderRadius borderLg = BorderRadius.circular(radiusLg);
  static final BorderRadius borderXl = BorderRadius.circular(radiusXl);
  static final BorderRadius borderFull = BorderRadius.circular(radiusFull);

  // ============================================================
  // ELEVATIONS & SHADOWS
  // Crisp slate-900 tinted shadows, no muddy blurs
  // ============================================================
  static const List<BoxShadow> elevation0 = [];

  static const List<BoxShadow> elevation1 = [
    BoxShadow(
      offset: Offset(0, 2),
      blurRadius: 4,
      color: Color(0x0D0F172A), // rgba(15, 23, 42, 0.05)
    ),
  ];

  static const List<BoxShadow> elevation2 = [
    BoxShadow(
      offset: Offset(0, 4),
      blurRadius: 8,
      color: Color(0x140F172A), // rgba(15, 23, 42, 0.08)
    ),
  ];

  static const List<BoxShadow> elevation3 = [
    BoxShadow(
      offset: Offset(0, 8),
      blurRadius: 16,
      color: Color(0x1F0F172A), // rgba(15, 23, 42, 0.12)
    ),
  ];

  static const List<BoxShadow> voiceGlow = [
    BoxShadow(
      offset: Offset(0, 8),
      blurRadius: 24,
      color: Color(0x331E3A8A), // rgba(30, 58, 138, 0.20)
    ),
  ];

  static const List<BoxShadow> emergencyGlow = [
    BoxShadow(
      offset: Offset(0, 8),
      blurRadius: 24,
      color: Color(0x40991B1B), // rgba(153, 27, 27, 0.25)
    ),
  ];
}
