import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/active_call_card.dart';
import '../../core/services/speech_service.dart';

/// Screen A-06B / 06B — Active Conversational Voice Call Interface
/// Hands-free telephone intake session connected to live backend session
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen A-06B)
class CallIntakeScreen extends StatefulWidget {
  const CallIntakeScreen({super.key});

  @override
  State<CallIntakeScreen> createState() => _CallIntakeScreenState();
}

class _CallIntakeScreenState extends State<CallIntakeScreen> {
  int _callSeconds = 0;
  Timer? _timer;
  bool _isMuted = false;
  bool _isSpeaker = true;
  final SpeechService _speech = SpeechService();
  String _liveTranscript = '';
  late final TextEditingController _transcriptController;

  final List<String> _quickCallSymptoms = [
    'सिरदर्द (Headache)',
    'बुखार (Fever)',
    'खांसी (Cough)',
    'पेट दर्द (Stomach Pain)',
    'उल्टी (Vomiting)',
    'कमर दर्द (Back Pain)',
    'चक्कर आना (Dizziness)',
  ];

  @override
  void initState() {
    super.initState();
    _transcriptController = TextEditingController();
    _startCallTimer();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startListening();
    });
  }

  void _startListening() async {
    final lang = context.read<LanguageProvider>();
    await _speech.startListening(
      languageCode: lang.currentLanguage,
      onResult: (text) {
        if (mounted) {
          setState(() {
            _liveTranscript = text;
            _transcriptController.text = text;
          });
        }
      },
    );
  }

  void _startCallTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() {
          _callSeconds++;
        });
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _speech.stopListening();
    _transcriptController.dispose();
    super.dispose();
  }

  String _formatDuration(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  Future<void> _endCallAndSubmit() async {
    final text = _transcriptController.text.trim();
    if (text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('कृपया अपने लक्षण बोलें या नीचे से चुनें (Please speak or select a symptom below)'),
          backgroundColor: MediColors.amber800,
        ),
      );
      return;
    }

    _timer?.cancel();
    await _speech.stopListening();
    if (!mounted) return;
    final intake = context.read<IntakeProvider>();
    await intake.submitTurn(patientSpeech: text);
    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/summary');
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final displayTranscript = _liveTranscript.isNotEmpty
        ? 'You: "$_liveTranscript"'
        : (intake.activeQuestion.isNotEmpty
            ? 'AI Doctor: "${intake.activeQuestion}"'
            : 'AI Doctor: "नमस्ते, कृपया अपने लक्षण विस्तार से बताएं..."');

    return MediScaffold(
      title: 'Active Intake Call',
      showHeader: false,
      currentLanguage: lang.currentLanguage,
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Column(
          children: [
            ActiveCallCard(
              durationText: _formatDuration(_callSeconds),
              transcript: displayTranscript,
              activeSymptoms: _liveTranscript.isNotEmpty
                  ? [_liveTranscript]
                  : const ['Listening for symptoms... बोलिए, हम सुन रहे हैं...'],
              isListening: !_isMuted,
              isMuted: _isMuted,
              isSpeakerOn: _isSpeaker,
              onToggleMute: () {
                setState(() => _isMuted = !_isMuted);
                if (_isMuted) {
                  _speech.stopListening();
                } else {
                  _startListening();
                }
              },
              onToggleSpeaker: () => setState(() => _isSpeaker = !_isSpeaker),
              onEndCall: _endCallAndSubmit,
            ),
            const SizedBox(height: MediDimensions.space16),

            // Quick Touch Selection if microphone is silent
            Container(
              padding: const EdgeInsets.all(MediDimensions.space16),
              decoration: BoxDecoration(
                color: MediColors.surface,
                borderRadius: MediDimensions.borderLg,
                border: Border.all(color: MediColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Tap symptoms if mic is quiet (या लक्षण चुनें):',
                        style: MediTypography.caption.copyWith(fontWeight: FontWeight.w700),
                      ),
                      if (_transcriptController.text.isNotEmpty)
                        GestureDetector(
                          onTap: () {
                            setState(() {
                              _liveTranscript = '';
                              _transcriptController.clear();
                            });
                          },
                          child: const Text('Clear', style: TextStyle(color: MediColors.red600, fontWeight: FontWeight.bold, fontSize: 13)),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _quickCallSymptoms.map((symptom) {
                      final label = symptom.split('(').first.trim();
                      return ActionChip(
                        label: Text(symptom, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                        backgroundColor: MediColors.slate100,
                        side: const BorderSide(color: MediColors.border),
                        onPressed: () {
                          setState(() {
                            _liveTranscript = label;
                            _transcriptController.text = label;
                          });
                        },
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
