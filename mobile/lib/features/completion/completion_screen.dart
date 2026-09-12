import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/privacy_reset_overlay.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 24 — Completion & Automatic Privacy Reset
/// Enforces mandatory 10-second RAM privacy wipe on public kiosks
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 24)
class CompletionScreen extends StatelessWidget {
  const CompletionScreen({super.key});

  void _wipeAndReturn(BuildContext context) {
    context.read<EncounterProvider>().resetSession();
    context.read<IntakeProvider>().clearIntake();
    Navigator.of(context).pushNamedAndRemoveUntil('/welcome', (route) => false);
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final encounter = context.watch<EncounterProvider>();

    return MediScaffold(
      title: 'Intake Completed',
      showBack: false,
      currentLanguage: lang.currentLanguage,
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: MediDimensions.space20),
            // Success Checkmark
            Container(
              width: 84,
              height: 84,
              decoration: const BoxDecoration(
                color: MediColors.emerald800,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.check_rounded, color: MediColors.white, size: 52),
            ),
            const SizedBox(height: MediDimensions.space24),
            Text(
              lang.translate('completion_title'),
              style: MediTypography.headlineLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space8),
            Text(
              'Your summary and prescription data have been forwarded to Doctor Room 102.',
              style: MediTypography.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space24),

            // Token Confirmation Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border),
                boxShadow: MediDimensions.elevation1,
              ),
              child: Column(
                children: [
                  const Text('OPD TICKET ISSUED', style: TextStyle(fontSize: 13, color: MediColors.textMuted, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Text(
                    encounter.tokenNumber ?? 'A-104',
                    style: const TextStyle(fontSize: 48, fontWeight: FontWeight.w900, color: MediColors.brandPrimary),
                  ),
                  Text(
                    'Department: ${encounter.department}',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Privacy Reset 10-Second Countdown Overlay
            PrivacyResetOverlay(
              countdownSeconds: 10,
              onReset: () => _wipeAndReturn(context),
            ),

            const SizedBox(height: MediDimensions.space20),
          ],
        ),
      ),
      bottomBar: PrimaryActionButton(
        label: 'Finish & Reset Screen Now (समाप्त)',
        icon: Icons.power_settings_new_rounded,
        onPressed: () => _wipeAndReturn(context),
      ),
    );
  }
}
