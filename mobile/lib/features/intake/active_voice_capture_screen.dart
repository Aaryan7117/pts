import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/listening_wave.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 07 — Active Voice Capture
/// Real-time audio waveform and live speech transcription
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 07)
class ActiveVoiceCaptureScreen extends StatefulWidget {
  const ActiveVoiceCaptureScreen({super.key});

  @override
  State<ActiveVoiceCaptureScreen> createState() => _ActiveVoiceCaptureScreenState();
}

class _ActiveVoiceCaptureScreenState extends State<ActiveVoiceCaptureScreen> {
  final TextEditingController _textController = TextEditingController(
    text: 'मुझे दो दिन से तेज सिरदर्द और हल्का बुखार है',
  );

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    return MediScaffold(
      title: 'Listening...',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          children: [
          const SizedBox(height: MediDimensions.space24),
          Text(
            lang.translate('listening'),
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space12),
          const Text(
            'Speak clearly near the microphone (माइक के पास बोलें)',
            style: TextStyle(fontSize: 16, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space40),

          // Active 5-Bar Waveform
          const ListeningWave(
            isActive: true,
            color: MediColors.brandPrimary,
            height: 64,
          ),

          const SizedBox(height: MediDimensions.space40),

          // Live Transcript Container
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(MediDimensions.space20),
            decoration: BoxDecoration(
              color: MediColors.surface,
              borderRadius: MediDimensions.borderLg,
              border: Border.all(color: MediColors.brandPrimary, width: 2.0),
              boxShadow: MediDimensions.elevation2,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: const BoxDecoration(
                        color: MediColors.red600,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Live ASR Transcript:',
                      style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: MediColors.textMuted),
                    ),
                  ],
                ),
                const SizedBox(height: MediDimensions.space12),
                TextField(
                  controller: _textController,
                  maxLines: 3,
                  style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w500, height: 1.4),
                  decoration: const InputDecoration(
                    border: InputBorder.none,
                    hintText: 'Recognized patient speech will appear here...',
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: MediDimensions.space24),
        ],
      ),
    ),
    bottomBar: PrimaryActionButton(
        label: 'Done Speaking (बोलना समाप्त)',
        icon: Icons.check_circle,
        onPressed: () {
          intake.submitTurn(patientSpeech: _textController.text);
          Navigator.of(context).pushNamed('/processing');
        },
      ),
    );
  }
}
