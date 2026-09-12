import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// Flashing Red Flag / Triage Emergency Banner
/// Visually dominates UI in deep crimson (#991B1B)
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.11
class EmergencyBanner extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback? onAlertStaff;

  const EmergencyBanner({
    super.key,
    required this.title,
    required this.message,
    this.onAlertStaff,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(MediDimensions.space24),
      decoration: BoxDecoration(
        color: MediColors.red800,
        borderRadius: MediDimensions.borderLg,
        boxShadow: MediDimensions.emergencyGlow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(MediDimensions.space8),
                decoration: const BoxDecoration(
                  color: MediColors.white,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.warning_amber_rounded, size: 32, color: MediColors.red800),
              ),
              const SizedBox(width: MediDimensions.space16),
              Expanded(
                child: Text(
                  title,
                  style: MediTypography.triageAlert,
                ),
              ),
            ],
          ),
          const SizedBox(height: MediDimensions.space16),
          Text(
            message,
            style: MediTypography.bodyLarge.copyWith(color: MediColors.white, height: 1.35),
          ),
          if (onAlertStaff != null) ...[
            const SizedBox(height: MediDimensions.space20),
            SizedBox(
              height: 56,
              child: ElevatedButton.icon(
                onPressed: onAlertStaff,
                icon: const Icon(Icons.notification_important, size: 28, color: MediColors.red800),
                label: const Text('ALERT OPD NURSE / ATTENDANT'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: MediColors.white,
                  foregroundColor: MediColors.red800,
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
                  textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
