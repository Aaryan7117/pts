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
      {'name': lang.translate('bp_label'), 'val': intake.vitals['Blood Pressure'] ?? '120/80 mmHg', 'icon': Icons.favorite_rounded, 'status': lang.translate('normal_status')},
      {'name': lang.translate('hr_label'), 'val': intake.vitals['Heart Rate'] ?? '72 bpm', 'icon': Icons.monitor_heart_rounded, 'status': lang.translate('normal_status')},
      {'name': lang.translate('spo2_label'), 'val': intake.vitals['SpO2'] ?? '98%', 'icon': Icons.air_rounded, 'status': lang.translate('normal_status')},
      {'name': lang.translate('temp_label'), 'val': intake.vitals['Temperature'] ?? '98.6 °F', 'icon': Icons.thermostat_rounded, 'status': lang.translate('normal_status')},
      {'name': lang.translate('sugar_label'), 'val': intake.vitals['Blood Sugar'] ?? '110 mg/dL', 'icon': Icons.bloodtype_rounded, 'status': lang.translate('normal_status')},
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
