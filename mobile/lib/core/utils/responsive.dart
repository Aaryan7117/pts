import 'package:flutter/material.dart';

/// Breakpoint and responsive grid helpers for MediKiosk
/// Supports Android Phone (Portrait) and Tablet/Kiosk (1280 × 800 Landscape)
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 4
class Responsive {
  static const double mobileMaxWidth = 600.0;
  static const double tabletMaxWidth = 1024.0;
  static const double kioskReferenceWidth = 1280.0;
  static const double kioskReferenceHeight = 800.0;

  static bool isMobile(BuildContext context) =>
      MediaQuery.of(context).size.width < mobileMaxWidth;

  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobileMaxWidth && width < tabletMaxWidth;
  }

  static bool isKiosk(BuildContext context) =>
      MediaQuery.of(context).size.width >= tabletMaxWidth ||
      (MediaQuery.of(context).orientation == Orientation.landscape &&
          MediaQuery.of(context).size.width >= 800);

  static bool isLandscape(BuildContext context) =>
      MediaQuery.of(context).orientation == Orientation.landscape;

  static double horizontalPadding(BuildContext context) {
    if (isKiosk(context)) return 48.0;
    if (isTablet(context)) return 32.0;
    return 20.0;
  }

  static double verticalPadding(BuildContext context) {
    if (isKiosk(context)) return 32.0;
    if (isTablet(context)) return 24.0;
    return 16.0;
  }

  static double maxContentWidth(BuildContext context) {
    if (isKiosk(context)) return 1100.0;
    if (isTablet(context)) return 720.0;
    return double.infinity;
  }
}
