import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../data/models/clinical_fact.dart';

/// Closed-Loop Explain-Back Fact Review Card
/// Patients confirm with simple [YES] / [NO] — no complex typing
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 7.10
class SummaryCard extends StatelessWidget {
  final ClinicalFact fact;
  final VoidCallback onConfirm;
  final VoidCallback onReject;

  const SummaryCard({
    super.key,
    required this.fact,
    required this.onConfirm,
    required this.onReject,
  });

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final isConfirmed = fact.status == 'patient_confirmed' || fact.status == 'explain_back_verified';

    return Container(
      margin: const EdgeInsets.only(bottom: MediDimensions.space16),
      padding: const EdgeInsets.all(MediDimensions.space20),
      decoration: BoxDecoration(
        color: isConfirmed ? MediColors.emerald50 : MediColors.surface,
        borderRadius: MediDimensions.borderLg,
        border: Border.all(
          color: isConfirmed ? MediColors.emerald700 : MediColors.border,
          width: isConfirmed ? 2.0 : 1.5,
        ),
        boxShadow: MediDimensions.elevation1,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: MediDimensions.space12,
                  vertical: MediDimensions.space4,
                ),
                decoration: BoxDecoration(
                  color: isConfirmed ? MediColors.emerald100 : MediColors.blue100,
                  borderRadius: MediDimensions.borderSm,
                ),
                child: Text(
                  fact.category.toUpperCase().replaceAll('_', ' '),
                  style: MediTypography.caption.copyWith(
                    color: isConfirmed ? MediColors.emerald900 : MediColors.brandPrimary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const Spacer(),
              if (isConfirmed)
                Row(
                  children: [
                    const Icon(Icons.check_circle, color: MediColors.emerald800, size: 20),
                    const SizedBox(width: 4),
                    Text(
                      lang.translate('verified_badge'),
                      style: const TextStyle(
                        color: MediColors.emerald800,
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
            ],
          ),
          const SizedBox(height: MediDimensions.space12),
          Text(
            fact.normalizedConcept ?? fact.value,
            style: MediTypography.headlineMedium.copyWith(fontSize: 22),
          ),
          if (fact.patientWords != null && fact.patientWords!.isNotEmpty) ...[
            const SizedBox(height: MediDimensions.space8),
            Text(
              '${lang.translate('patient_said')} "${fact.patientWords}"',
              style: MediTypography.bodyMedium.copyWith(fontStyle: FontStyle.italic),
            ),
          ],
          const SizedBox(height: MediDimensions.space16),
          Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 52,
                  child: ElevatedButton.icon(
                    onPressed: onConfirm,
                    icon: const Icon(Icons.check, size: 22),
                    label: Text(lang.translate('confirm_yes')),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isConfirmed ? MediColors.emerald800 : MediColors.brandPrimary,
                      foregroundColor: MediColors.white,
                      shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
                      textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: MediDimensions.space12),
              Expanded(
                child: SizedBox(
                  height: 52,
                  child: OutlinedButton.icon(
                    onPressed: onReject,
                    icon: const Icon(Icons.close, size: 22),
                    label: Text(lang.translate('confirm_no')),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: MediColors.triageRed,
                      side: const BorderSide(color: MediColors.triageRed, width: 1.5),
                      shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderMd),
                      textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
