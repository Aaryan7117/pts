import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 01 — Welcome
/// Calm, trustworthy healthcare welcome screen with 72dp primary CTA
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 01)
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final encounter = context.read<EncounterProvider>();

    return MediScaffold(
      title: 'MediKiosk',
      showHeader: true,
      showBack: false,
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) {
        lang.setLanguage(l);
        encounter.updateLanguage(l);
      },
      onEmergencyTap: () => Navigator.of(context).pushNamed('/emergency'),
      body: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(height: MediDimensions.space24),
            // Medical Brand Hero Mark
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: MediColors.brandPrimary,
                borderRadius: MediDimensions.borderXl,
                boxShadow: MediDimensions.elevation3,
              ),
              child: const Icon(
                Icons.local_hospital_rounded,
                size: 56,
                color: MediColors.white,
              ),
            ),
            const SizedBox(height: MediDimensions.space24),
            Text(
              lang.translate('welcome_title'),
              style: MediTypography.displayLarge.copyWith(fontSize: 28),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space12),
            Text(
              lang.translate('welcome_subtitle'),
              style: MediTypography.bodyLarge.copyWith(color: MediColors.textMuted, fontSize: 18),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space24),

            // 1-Tap Voice AI Fast Track Card
            InkWell(
              onTap: () async {
                await encounter.bootstrap(channel: 'android_byod', language: lang.currentLanguage);
                if (!context.mounted) return;
                await context.read<IntakeProvider>().startSession(
                  encounterId: encounter.encounterId ?? 'enc-001',
                  language: lang.currentLanguage,
                );
                if (!context.mounted) return;
                Navigator.of(context).pushNamed('/active_call');
              },
              borderRadius: MediDimensions.borderLg,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(MediDimensions.space16),
                decoration: BoxDecoration(
                  color: MediColors.emerald50,
                  borderRadius: MediDimensions.borderLg,
                  border: Border.all(color: MediColors.emerald800, width: 1.5),
                  boxShadow: MediDimensions.elevation2,
                ),
                child: Row(
                  children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: const BoxDecoration(
                        color: MediColors.emerald800,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.phone_in_talk_rounded, color: MediColors.white, size: 28),
                    ),
                    const SizedBox(width: MediDimensions.space16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            lang.translate('voice_call_fast_track_title'),
                            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: MediColors.emerald900),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            lang.translate('voice_call_fast_track_sub'),
                            style: MediTypography.bodySmall.copyWith(color: MediColors.emerald800),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.arrow_forward_ios_rounded, color: MediColors.emerald800, size: 18),
                  ],
                ),
              ),
            ),
            const SizedBox(height: MediDimensions.space16),
          ],
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: lang.translate('start_button'),
            icon: Icons.play_arrow_rounded,
            onPressed: () async {
              await encounter.bootstrap(
                channel: 'android_byod',
                language: lang.currentLanguage,
              );
              if (context.mounted) {
                Navigator.of(context).pushNamed('/language');
              }
            },
          ),
          const SizedBox(height: MediDimensions.space8),
          TextButton.icon(
            onPressed: () => Navigator.of(context).pushNamed('/emergency'),
            icon: const Icon(Icons.emergency, color: MediColors.triageRed, size: 22),
            label: Text(
              lang.translate('emergency_assistance_btn'),
              style: MediTypography.bodyMedium.copyWith(
                color: MediColors.triageRed,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
