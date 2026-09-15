import 'package:flutter/material.dart';

/// MediKiosk 3-Layer Design Token Architecture (Spec v4.0.0)
/// ReliaCare Light Medical Glassmorphism Standard
/// Canvas: Cream/Sage (#F8FAF5)
/// Dominant CTA: Vibrant Lime (#A3E635) with Deep Forest (#064E3B) text (7.6:1 AAA Contrast)
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 2
abstract class MediColors {
  // ============================================================
  // LAYER 1: PRIMITIVE TOKENS
  // ============================================================
  // Slate Neutrals
  static const Color slate50 = Color(0xFFF8FAFC);
  static const Color slate100 = Color(0xFFF1F5F9);
  static const Color slate200 = Color(0xFFE2E8F0);
  static const Color slate300 = Color(0xFFCBD5E1);
  static const Color slate400 = Color(0xFF94A3B8);
  static const Color slate500 = Color(0xFF64748B);
  static const Color slate600 = Color(0xFF475569);
  static const Color slate700 = Color(0xFF334155);
  static const Color slate800 = Color(0xFF1E293B);
  static const Color slate900 = Color(0xFF0F172A);
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);

  // Healthcare Navy & Primary Blues
  static const Color blue50 = Color(0xFFEFF6FF);
  static const Color blue100 = Color(0xFFDBEAFE);
  static const Color blue200 = Color(0xFFBFDBFE);
  static const Color blue600 = Color(0xFF2563EB);
  static const Color blue700 = Color(0xFF1D4ED8);
  static const Color blue800 = Color(0xFF1E3A8A);
  static const Color blue900 = Color(0xFF172554);

  // ReliaCare Light Medical Palette (Spec v4.0.0)
  static const Color creamSage = Color(0xFFF8FAF5); // Canvas background
  static const Color limeCTA = Color(0xFFA3E635); // Vibrant Lime CTA
  static const Color limeHover = Color(0xFF84CC16);
  static const Color forestDark = Color(0xFF064E3B); // Deep Forest text (7.6:1 AAA)
  static const Color forestMid = Color(0xFF047857);
  static const Color forestSubtle = Color(0xFFE8EFE6);

  // Clinical AYUSH Forest Green & Emeralds
  static const Color emerald50 = Color(0xFFECFDF5);
  static const Color emerald100 = Color(0xFFD1FAE5);
  static const Color emerald200 = Color(0xFFA7F3D0);
  static const Color emerald300 = Color(0xFF6EE7B7);
  static const Color emerald400 = Color(0xFF34D399);
  static const Color emerald500 = Color(0xFF10B981);
  static const Color emerald600 = Color(0xFF059669);
  static const Color emerald700 = Color(0xFF047857);
  static const Color emerald800 = Color(0xFF065F46); // AYUSH Green & Success
  static const Color emerald900 = Color(0xFF064E3B);

  // Triage Red & Emergency Crimson
  static const Color red50 = Color(0xFFFEF2F2);
  static const Color red100 = Color(0xFFFEE2E2);
  static const Color red200 = Color(0xFFFECACA);
  static const Color red600 = Color(0xFFDC2626);
  static const Color red700 = Color(0xFFB91C1C);
  static const Color red800 = Color(0xFF991B1B); // Triage Red Banner
  static const Color red900 = Color(0xFF7F1D1D);

  // Warning & Clinical Gap Amber
  static const Color amber50 = Color(0xFFFFFBEB);
  static const Color amber100 = Color(0xFFFEF3C7);
  static const Color amber600 = Color(0xFFD97706);
  static const Color amber700 = Color(0xFFB45309);
  static const Color amber800 = Color(0xFF92400E); // Clinical Gap Warning
  static const Color amber900 = Color(0xFF78350F);

  // ============================================================
  // LAYER 2: SEMANTIC TOKENS
  // ============================================================
  static const Color canvas = creamSage;
  static const Color surface = white;
  static const Color surfaceSubtle = forestSubtle;
  static const Color surfaceElevated = white;

  static const Color brandPrimary = limeCTA;
  static const Color brandDark = forestDark;
  static const Color brandTint = forestSubtle;
  static const Color brandInteractive = forestMid;

  static const Color ayushGreen = emerald800;
  static const Color ayushTint = emerald50;

  static const Color triageRed = red800;
  static const Color triageTint = red50;
  static const Color triageInteractive = red600;

  static const Color warning = amber800;
  static const Color warningTint = amber50;

  static const Color success = emerald700;
  static const Color successTint = emerald50;

  static const Color border = Color(0x1A064E3B); // Subtle forest border
  static const Color borderStrong = Color(0x38064E3B);
  static const Color borderSelected = forestMid;

  static const Color textPrimary = slate900;
  static const Color textMuted = slate600;
  static const Color textDisabled = slate400;
  static const Color textInverse = white;

  // ============================================================
  // LAYER 3: COMPONENT TOKENS
  // ============================================================
  static const Color primaryBtnBg = limeCTA;
  static const Color primaryBtnText = forestDark; // 7.6:1 AAA Contrast
  static const Color secondaryBtnBorder = Color(0x28064E3B);
  static const Color secondaryBtnText = forestDark;

  static const Color choiceCardBg = white;
  static const Color choiceCardSelectedBg = Color(0xFFF0FDF4);
  static const Color choiceCardSelectedBorder = emerald600;

  static const Color voiceBtnIdle = forestDark;
  static const Color voiceBtnListening = red600;
  static const Color voiceHaloIdle = Color(0x40A3E635);
  static const Color voiceHaloListening = Color(0x3DDC2626);

  static const Color emergencyBannerBg = red800;
  static const Color emergencyBannerText = white;

  static const Color offlineBannerEdgeBg = amber100;
  static const Color offlineBannerEdgeText = amber900;
  static const Color offlineBannerFullBg = red100;
  static const Color offlineBannerFullText = red900;
}
