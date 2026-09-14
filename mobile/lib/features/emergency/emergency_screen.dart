import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 22 — Emergency Assistance & SOS Trigger
/// Immediate emergency hotline and ambulance escalation
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 22)
class EmergencyScreen extends StatelessWidget {
  const EmergencyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: lang.translate('emergency_title'),
      backgroundColor: MediColors.red50,
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(height: MediDimensions.space20),
            // Massive Pulsing SOS Emergency Button
            GestureDetector(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Hospital Casualty Ward & Code Blue Alert Dispatched!'),
                    backgroundColor: MediColors.red800,
                  ),
                );
              },
              child: Container(
                width: 130,
                height: 130,
                decoration: const BoxDecoration(
                  color: MediColors.red800,
                  shape: BoxShape.circle,
                  boxShadow: MediDimensions.emergencyGlow,
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.emergency_rounded, color: MediColors.white, size: 48),
                    SizedBox(height: 6),
                    Text(
                      'SOS ALERT',
                      style: TextStyle(color: MediColors.white, fontSize: 16, fontWeight: FontWeight.w900, letterSpacing: 1.5),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: MediDimensions.space24),
            Text(
              lang.translate('immediate_emergency_help'),
              style: MediTypography.headlineLarge.copyWith(color: MediColors.red900),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space12),
            Text(
              lang.translate('immediate_emergency_sub'),
              style: const TextStyle(fontSize: 16, color: MediColors.textPrimary),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space20),
            Container(
              padding: const EdgeInsets.all(MediDimensions.space16),
              decoration: BoxDecoration(
                color: MediColors.white,
                borderRadius: MediDimensions.borderMd,
                border: Border.all(color: MediColors.red200),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.phone_in_talk_rounded, color: MediColors.red800, size: 28),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Text(
                      lang.translate('casualty_line'),
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: MediColors.red900),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MediDimensions.space20),
          ],
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: lang.translate('ambulance_dispatch_btn'),
            backgroundColor: MediColors.red800,
            icon: Icons.airport_shuttle_rounded,
            onPressed: () => Navigator.of(context).pushNamed('/ambulance'),
          ),
          const SizedBox(height: MediDimensions.space12),
          SecondaryActionButton(
            label: lang.translate('return_to_intake'),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }
}
