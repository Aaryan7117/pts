import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 17 — Vitals Capture
/// Blood Pressure, Heart Rate, SpO2, Temperature, and Blood Sugar cards
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 17)
class VitalsScreen extends StatelessWidget {
  const VitalsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();
    final encounter = context.read<EncounterProvider>();

    final vitalsList = [
      {'name': lang.translate('bp_label'), 'val': intake.vitals['Blood Pressure'] ?? 'Pending (लंबित)', 'icon': Icons.favorite_rounded, 'status': intake.vitals['Blood Pressure'] != null ? lang.translate('normal_status') : 'Awaiting Check'},
      {'name': lang.translate('hr_label'), 'val': intake.vitals['Heart Rate'] ?? 'Pending (लंबित)', 'icon': Icons.monitor_heart_rounded, 'status': intake.vitals['Heart Rate'] != null ? lang.translate('normal_status') : 'Awaiting Check'},
      {'name': lang.translate('spo2_label'), 'val': intake.vitals['SpO2'] ?? 'Pending (लंबित)', 'icon': Icons.air_rounded, 'status': intake.vitals['SpO2'] != null ? lang.translate('normal_status') : 'Awaiting Check'},
      {'name': lang.translate('temp_label'), 'val': intake.vitals['Temperature'] ?? 'Pending (लंबित)', 'icon': Icons.thermostat_rounded, 'status': intake.vitals['Temperature'] != null ? lang.translate('normal_status') : 'Awaiting Check'},
      {'name': lang.translate('sugar_label'), 'val': intake.vitals['Blood Sugar'] ?? 'Pending (लंबित)', 'icon': Icons.bloodtype_rounded, 'status': intake.vitals['Blood Sugar'] != null ? lang.translate('normal_status') : 'Awaiting Check'},
    ];

    return MediScaffold(
      title: lang.translate('vitals_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang.translate('vitals_title'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          Text(
            lang.translate('vitals_sub'),
            style: const TextStyle(fontSize: 16, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: ListView.separated(
              itemCount: vitalsList.length,
              separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space12),
              itemBuilder: (context, index) {
                final v = vitalsList[index];
                return Container(
                  padding: const EdgeInsets.all(MediDimensions.space16),
                  decoration: BoxDecoration(
                    color: MediColors.surface,
                    borderRadius: MediDimensions.borderLg,
                    border: Border.all(color: MediColors.border),
                    boxShadow: MediDimensions.elevation1,
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 52,
                        height: 52,
                        decoration: BoxDecoration(
                          color: MediColors.blue50,
                          borderRadius: MediDimensions.borderMd,
                        ),
                        child: Icon(v['icon'] as IconData, color: MediColors.brandPrimary, size: 28),
                      ),
                      const SizedBox(width: MediDimensions.space16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              v['name'] as String,
                              style: const TextStyle(fontSize: 16, color: MediColors.textMuted),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              v['val'] as String,
                              style: MediTypography.headlineMedium.copyWith(fontSize: 22, fontWeight: FontWeight.w700),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: MediColors.emerald50,
                          borderRadius: MediDimensions.borderSm,
                        ),
                        child: Text(
                          v['status'] as String,
                          style: const TextStyle(color: MediColors.emerald800, fontWeight: FontWeight.w700, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('confirm_vitals_next'),
        icon: Icons.arrow_forward_rounded,
        onPressed: () {
          if (encounter.department.contains('AYUSH')) {
            Navigator.of(context).pushNamed('/ayush');
          } else {
            Navigator.of(context).pushNamed('/queue');
          }
        },
      ),
    );
  }
}
