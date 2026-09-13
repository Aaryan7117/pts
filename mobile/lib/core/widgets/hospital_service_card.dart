import 'package:flutter/material.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';

/// Hospital Service / Facility Card
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.12
class HospitalServiceCard extends StatelessWidget {
  final String title;
  final String floor;
  final String waitTime;
  final IconData icon;
  final VoidCallback onDirectionsTap;

  const HospitalServiceCard({
    super.key,
    required this.title,
    required this.floor,
    required this.waitTime,
    required this.icon,
    required this.onDirectionsTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: MediDimensions.space16),
      padding: const EdgeInsets.all(MediDimensions.space20),
      decoration: BoxDecoration(
        color: MediColors.surface,
        borderRadius: MediDimensions.borderLg,
        border: Border.all(color: MediColors.border, width: 1.5),
        boxShadow: MediDimensions.elevation1,
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: MediColors.blue50,
              borderRadius: MediDimensions.borderMd,
            ),
            child: Icon(icon, size: 32, color: MediColors.brandPrimary),
          ),
          const SizedBox(width: MediDimensions.space16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: MediTypography.headlineMedium.copyWith(fontSize: 20),
                ),
                const SizedBox(height: MediDimensions.space4),
                Wrap(
                  spacing: MediDimensions.space8,
                  runSpacing: MediDimensions.space4,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text(
                      floor,
                      style: MediTypography.bodyMedium.copyWith(fontSize: 15),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: MediColors.emerald50,
                        borderRadius: MediDimensions.borderSm,
                      ),
                      child: Text(
                        'Wait: $waitTime',
                        style: const TextStyle(
                          color: MediColors.emerald800,
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: MediDimensions.space12),
          IconButton.filled(
            onPressed: onDirectionsTap,
            icon: const Icon(Icons.directions, color: MediColors.white),
            style: IconButton.styleFrom(
              backgroundColor: MediColors.brandPrimary,
              padding: const EdgeInsets.all(12),
            ),
          ),
        ],
      ),
    );
  }
}
