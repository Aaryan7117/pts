import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/voice_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 06 — Voice Intake
/// Voice-first symptom capture with touch fallback and AI Call Intake shortcut
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 06)
class VoiceIntakeScreen extends StatelessWidget {
  const VoiceIntakeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final quickChips = [
      {'key': 'chip_fever', 'label': lang.translate('chip_fever')},
      {'key': 'chip_headache', 'label': lang.translate('chip_headache')},
      {'key': 'chip_cough', 'label': lang.translate('chip_cough')},
      {'key': 'chip_stomach_pain', 'label': lang.translate('chip_stomach_pain')},
      {'key': 'chip_joint_pain', 'label': lang.translate('chip_joint_pain')},
    ];

    return MediScaffold(
      title: lang.translate('voice_intake_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: MediDimensions.space16),
            Text(
              lang.translate('voice_intake_title'),
              style: MediTypography.headlineLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space12),

            // AI Question Speech Bubble
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(MediDimensions.space20),
              decoration: BoxDecoration(
                color: MediColors.blue50,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.blue200),
              ),
              child: Row(
                children: [
                  const Icon(Icons.volume_up, color: MediColors.brandPrimary, size: 28),
                  const SizedBox(width: MediDimensions.space16),
                  Expanded(
                    child: Text(
                      intake.activeQuestion,
                      style: MediTypography.bodyLarge.copyWith(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space40),

            // Pulsing Voice Button
            VoiceButton(
              isListening: intake.isListening,
              label: intake.isListening ? lang.translate('listening') : lang.translate('tap_to_speak'),
              onTap: () {
                Navigator.of(context).pushNamed('/active_capture');
              },
            ),

            const SizedBox(height: MediDimensions.space32),

            // Secondary Option: Launch Simulated Phone Call Intake
            Container(
              padding: const EdgeInsets.all(MediDimensions.space16),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: const BoxDecoration(
                      color: MediColors.emerald800,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.call, color: MediColors.white, size: 24),
                  ),
                  const SizedBox(width: MediDimensions.space16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          lang.translate('call_intake_shortcut_title'),
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                        ),
                        Text(
                          lang.translate('voice_call_fast_track_sub'),
                          style: const TextStyle(fontSize: 13, color: MediColors.textMuted),
                        ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pushNamed('/active_call'),
                    child: Text(lang.translate('call_intake_shortcut_btn'), style: const TextStyle(fontWeight: FontWeight.w800)),
                  ),
                ],
              ),
            ),

            const SizedBox(height: MediDimensions.space24),

            // Quick Symptom Touch Chips (Touch fallback)
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                lang.translate('tap_symptom_chip_prompt'),
                style: MediTypography.caption.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
            const SizedBox(height: MediDimensions.space12),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: quickChips.map((chip) {
                return ActionChip(
                  label: Text(chip['label']!, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  backgroundColor: MediColors.slate100,
                  side: const BorderSide(color: MediColors.border),
                  onPressed: () {
                    intake.submitTurn(patientSpeech: chip['label']!);
                    Navigator.of(context).pushNamed('/processing');
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
      bottomBar: SecondaryActionButton(
        label: lang.translate('type_symptoms_link'),
        icon: Icons.keyboard_alt_outlined,
        onPressed: () => Navigator.of(context).pushNamed('/text_intake'),
      ),
    );
  }
}
