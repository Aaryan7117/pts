import 'package:flutter/material.dart';
import 'colors.dart';
import 'dimensions.dart';
import 'typography.dart';

/// MediKiosk Master ThemeData
/// Material 3 Foundation with Custom Healthcare Design System Tokens
/// Meets WCAG 2.2 Level AAA (Contrast >= 7:1)
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 10.2
abstract class MediKioskTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: MediColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: MediColors.brandPrimary,
        onPrimary: MediColors.textInverse,
        primaryContainer: MediColors.brandTint,
        onPrimaryContainer: MediColors.brandPrimary,
        surface: MediColors.surface,
        onSurface: MediColors.textPrimary,
        surfaceContainerHighest: MediColors.surfaceSubtle,
        error: MediColors.triageRed,
        onError: MediColors.white,
        errorContainer: MediColors.triageTint,
        onErrorContainer: MediColors.triageRed,
        outline: MediColors.border,
        outlineVariant: MediColors.borderStrong,
      ),
      fontFamily: 'Roboto',
      fontFamilyFallback: MediTypography.fontFallbacks,
      textTheme: const TextTheme(
        displayLarge: MediTypography.displayLarge,
        headlineLarge: MediTypography.headlineLarge,
        headlineMedium: MediTypography.headlineMedium,
        bodyLarge: MediTypography.bodyLarge,
        bodyMedium: MediTypography.bodyMedium,
        labelLarge: MediTypography.buttonLarge,
        labelMedium: MediTypography.buttonMedium,
        bodySmall: MediTypography.caption,
      ),
      cardTheme: CardThemeData(
        color: MediColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: MediDimensions.borderLg,
          side: const BorderSide(color: MediColors.border, width: 1.5),
        ),
        margin: EdgeInsets.zero,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: MediColors.brandPrimary,
          foregroundColor: MediColors.white,
          minimumSize: const Size(double.infinity, MediDimensions.primaryCtaHeight),
          shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderXl),
          elevation: 2,
          textStyle: MediTypography.buttonLarge,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: MediColors.textPrimary,
          minimumSize: const Size(double.infinity, MediDimensions.secondaryCtaHeight),
          side: const BorderSide(color: MediColors.borderStrong, width: 1.5),
          shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
          textStyle: MediTypography.buttonMedium,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: MediColors.surface,
        foregroundColor: MediColors.textPrimary,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: MediTypography.headlineMedium,
      ),
      dividerTheme: const DividerThemeData(
        color: MediColors.border,
        thickness: 1.0,
        space: MediDimensions.space24,
      ),
    );
  }
}
