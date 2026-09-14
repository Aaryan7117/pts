import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/emergency_banner.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 11 — Red Flag / Triage Safety Screen
/// Deep crimson visual alert with immediate clinical escalation
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 11)
class TriageScreen extends StatelessWidget {
  const TriageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('triage_alert_title'),
      backgroundColor: MediColors.red50,
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          children: [
            EmergencyBanner(
              title: lang.translate('emergency_title'),
              message: lang.translate('triage_alert_sub'),
              onAlertStaff: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('OPD Staff Terminal Alerted! Attendant is approaching.'),
                    backgroundColor: MediColors.red800,
                  ),
                );
              },
            ),
            const SizedBox(height: MediDimensions.space24),
            Container(
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.triageRed, width: 2.0),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lang.translate('triage_steps_title'),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: MediColors.triageRed),
                  ),
                  const SizedBox(height: MediDimensions.space12),
                  _buildTriageStep('1', lang.translate('triage_step_1')),
                  _buildTriageStep('2', lang.translate('triage_step_2')),
                  _buildTriageStep('3', lang.translate('triage_step_3')),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: lang.translate('go_emergency_room'),
            backgroundColor: MediColors.triageRed,
            icon: Icons.local_hospital_rounded,
            onPressed: () => Navigator.of(context).pushNamed('/emergency'),
          ),
          const SizedBox(height: MediDimensions.space12),
          SecondaryActionButton(
            label: lang.translate('continue_routine_intake'),
            onPressed: () => Navigator.of(context).pushNamed('/doc_intro'),
          ),
        ],
      ),
    );
  }

  Widget _buildTriageStep(String number, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MediDimensions.space8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 12,
            backgroundColor: MediColors.red100,
            child: Text(number, style: const TextStyle(color: MediColors.red800, fontSize: 13, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: MediDimensions.space12),
          Expanded(child: Text(text, style: MediTypography.bodyMedium.copyWith(color: MediColors.textPrimary))),
        ],
      ),
    );
  }
}
