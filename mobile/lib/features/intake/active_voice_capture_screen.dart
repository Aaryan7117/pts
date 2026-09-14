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
import '../../core/services/speech_service.dart';

/// Screen 07 — Active Voice Capture
/// Real-time audio waveform and live speech transcription
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 07)
class ActiveVoiceCaptureScreen extends StatefulWidget {
  const ActiveVoiceCaptureScreen({super.key});

  @override
  State<ActiveVoiceCaptureScreen> createState() => _ActiveVoiceCaptureScreenState();
}

class _ActiveVoiceCaptureScreenState extends State<ActiveVoiceCaptureScreen> {
  final TextEditingController _textController = TextEditingController();
  final SpeechService _speech = SpeechService();
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startListening();
    });
  }

  void _startListening() async {
    final lang = context.read<LanguageProvider>();
    setState(() => _isListening = true);
    final ok = await _speech.startListening(
      languageCode: lang.currentLanguage,
      onResult: (text) {
        if (mounted) {
          setState(() {
            _textController.text = text;
          });
        }
      },
    );
    if (!ok && mounted) {
      setState(() => _isListening = false);
    }
  }

  void _stopListening() async {
    await _speech.stopListening();
    if (mounted) {
      setState(() => _isListening = false);
    }
  }

  @override
  void dispose() {
    _speech.stopListening();
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final chipKeys = [
      'chip_chest_pain',
      'chip_stomach_pain',
      'chip_cough',
      'chip_vomiting',
      'chip_back_pain',
      'chip_joint_pain',
      'chip_breathlessness',
      'chip_dizziness',
    ];

    return MediScaffold(
      title: _isListening ? lang.translate('listening') : lang.translate('voice_intake_title'),
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: MediDimensions.space24),
            Text(
              _isListening ? lang.translate('listening') : lang.translate('tap_to_speak'),
              style: MediTypography.headlineLarge,
            ),
            const SizedBox(height: MediDimensions.space12),
            Text(
              _isListening
                  ? lang.translate('speak_clearly_mic')
                  : lang.translate('tap_wave_resume'),
              style: const TextStyle(fontSize: 16, color: MediColors.textMuted),
            ),
            const SizedBox(height: MediDimensions.space32),

            // Active 5-Bar Waveform (tappable to start/stop listening)
            GestureDetector(
              onTap: () {
                if (_isListening) {
                  _stopListening();
                } else {
                  _startListening();
                }
              },
              child: ListeningWave(
                isActive: _isListening,
                color: _isListening ? MediColors.brandPrimary : MediColors.slate400,
                height: 64,
              ),
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
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
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
                          Text(
                            lang.translate('speech_symptom_input'),
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: MediColors.textMuted),
                          ),
                        ],
                      ),
                      if (_textController.text.isNotEmpty)
                        GestureDetector(
                          onTap: () => setState(() => _textController.clear()),
                          child: const Text('Clear', style: TextStyle(color: MediColors.red600, fontWeight: FontWeight.w600, fontSize: 13)),
                        ),
                    ],
                  ),
                  const SizedBox(height: MediDimensions.space12),
                  TextField(
                    controller: _textController,
                    maxLines: 3,
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w500, height: 1.4),
                    decoration: InputDecoration(
                      border: InputBorder.none,
                      hintText: lang.translate('type_or_select_hint'),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MediDimensions.space16),

            // Quick Symptom Chips to test any concept in Concept Bank
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                lang.translate('tap_symptom_chip_prompt'),
                style: MediTypography.caption.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
            const SizedBox(height: MediDimensions.space8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: chipKeys.map((key) {
                final label = lang.translate(key);
                return ActionChip(
                  label: Text(label, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                  backgroundColor: MediColors.slate100,
                  side: const BorderSide(color: MediColors.border),
                  onPressed: () {
                    setState(() {
                      _textController.text = label;
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: MediDimensions.space24),
          ],
        ),
      ),
      bottomBar: PrimaryActionButton(
        label: lang.translate('done_speaking'),
        icon: Icons.check_circle,
        onPressed: () async {
          await _speech.stopListening();
          final text = _textController.text.trim();
          if (text.isEmpty) {
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(lang.translate('type_or_select_hint')),
                  backgroundColor: MediColors.amber800,
                ),
              );
            }
            return;
          }
          await intake.submitTurn(patientSpeech: text);
          if (context.mounted) {
            Navigator.of(context).pushNamed('/processing');
          }
        },
      ),
    );
  }
}
