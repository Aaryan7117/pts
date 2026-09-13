import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
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

  @override
  void initState() {
    super.initState();
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
    super.dispose();
  }

  String _formatDuration(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
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
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: ActiveCallCard(
            durationText: _formatDuration(_callSeconds),
            transcript: displayTranscript,
            activeSymptoms: _liveTranscript.isNotEmpty
                ? [_liveTranscript]
                : const ['Listening for symptoms...'],
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
            onEndCall: () async {
              _timer?.cancel();
              await _speech.stopListening();
              final speechToSubmit = _liveTranscript.isNotEmpty
                  ? _liveTranscript
                  : 'छाती में दर्द';
              await intake.submitTurn(patientSpeech: speechToSubmit);
              if (context.mounted) {
                Navigator.of(context).pushReplacementNamed('/summary');
              }
            },
          ),
        ),
      ),
    );
  }
}
