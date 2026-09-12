import 'package:flutter/material.dart';
import 'colors.dart';

/// MediKiosk Typography Architecture
/// High-contrast typography optimized for 68+ year-old rural patients
/// Diacritic clearance (height: 1.30-1.45) to prevent Indic vowel matra clipping
/// Fallbacks for Devanagari (Hindi/Marathi), Tamil, Telugu
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 3
abstract class MediTypography {
  static const List<String> fontFallbacks = [
    'NotoSansDevanagari',
    'NotoSansTamil',
    'NotoSansTelugu',
    'sans-serif',
  ];

  static const TextStyle displayLarge = TextStyle(
    fontSize: 36,
    fontWeight: FontWeight.w700,
    color: MediColors.textPrimary,
    height: 1.25,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle headlineLarge = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w600,
    color: MediColors.textPrimary,
    height: 1.30,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    color: MediColors.textPrimary,
    height: 1.35,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w400,
    color: MediColors.textPrimary,
    height: 1.40,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w400,
    color: MediColors.textMuted,
    height: 1.45,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle buttonLarge = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w600,
    color: MediColors.textInverse,
    height: 1.25,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle buttonMedium = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: MediColors.textPrimary,
    height: 1.25,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle caption = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w500,
    color: MediColors.textMuted,
    height: 1.35,
    fontFamilyFallback: fontFallbacks,
  );

  static const TextStyle triageAlert = TextStyle(
    fontSize: 26,
    fontWeight: FontWeight.w700,
    color: MediColors.white,
    height: 1.30,
    letterSpacing: 0.5,
    fontFamilyFallback: fontFallbacks,
  );
}
