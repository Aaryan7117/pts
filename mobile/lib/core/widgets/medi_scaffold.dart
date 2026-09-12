import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../utils/responsive.dart';
import 'medi_header.dart';
import 'offline_banner.dart';

/// Standardized Responsive Scaffold for all MediKiosk Patient Screens
/// Provides automatic SafeArea, responsive centering, and optional sticky footer
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.1
class MediScaffold extends StatelessWidget {
  final Widget body;
  final String title;
  final bool showHeader;
  final bool showBack;
  final VoidCallback? onBack;
  final String currentLanguage;
  final ValueChanged<String>? onLanguageChanged;
  final VoidCallback? onEmergencyTap;
  final String? tokenNumber;
  final Widget? bottomBar;
  final NetworkStatus networkStatus;
  final VoidCallback? onRetryNetwork;
  final Color backgroundColor;

  const MediScaffold({
    super.key,
    required this.body,
    this.title = 'MediKiosk',
    this.showHeader = true,
    this.showBack = true,
    this.onBack,
    this.currentLanguage = 'hi',
    this.onLanguageChanged,
    this.onEmergencyTap,
    this.tokenNumber,
    this.bottomBar,
    this.networkStatus = NetworkStatus.online,
    this.onRetryNetwork,
    this.backgroundColor = MediColors.canvas,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: showHeader
          ? MediHeader(
              title: title,
              showBack: showBack,
              onBack: onBack ?? (Navigator.of(context).canPop() ? () => Navigator.of(context).pop() : null),
              currentLanguage: currentLanguage,
              onLanguageChanged: onLanguageChanged,
              onEmergencyTap: onEmergencyTap,
              tokenNumber: tokenNumber,
            )
          : null,
      body: SafeArea(
        child: Column(
          children: [
            // Offline / Edge status notification
            OfflineBanner(
              status: networkStatus,
              onRetry: onRetryNetwork,
            ),
            // Responsive Centered Content Area
            Expanded(
              child: Center(
                child: ConstrainedBox(
                  constraints: BoxConstraints(
                    maxWidth: Responsive.maxContentWidth(context),
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: Responsive.horizontalPadding(context),
                      vertical: Responsive.verticalPadding(context),
                    ),
                    child: body,
                  ),
                ),
              ),
            ),
            if (bottomBar != null)
              Container(
                decoration: const BoxDecoration(
                  color: MediColors.surface,
                  border: Border(top: BorderSide(color: MediColors.border, width: 1.0)),
                  boxShadow: MediDimensions.elevation2,
                ),
                padding: EdgeInsets.symmetric(
                  horizontal: Responsive.horizontalPadding(context),
                  vertical: MediDimensions.space16,
                ),
                child: Center(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      maxWidth: Responsive.maxContentWidth(context),
                    ),
                    child: bottomBar,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
