import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/active_call_card.dart';

/// Screen A-06B / 06B — Active Conversational Voice Call Interface
/// Simulates hands-free telephone intake session connected to same backend session
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

  @override
  void initState() {
    super.initState();
    _startCallTimer();
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

    return MediScaffold(
      title: 'Active Intake Call',
      showHeader: false,
      currentLanguage: lang.currentLanguage,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: ActiveCallCard(
            durationText: _formatDuration(_callSeconds),
            transcript: intake.currentTranscript.isNotEmpty
                ? intake.currentTranscript
                : 'AI Intake Doctor: "नमस्ते, कृपया अपने लक्षण विस्तार से बताएं..."',
            activeSymptoms: const ['Headache', 'Fever', '2 Days'],
            isListening: true,
            isMuted: _isMuted,
            isSpeakerOn: _isSpeaker,
            onToggleMute: () => setState(() => _isMuted = !_isMuted),
            onToggleSpeaker: () => setState(() => _isSpeaker = !_isSpeaker),
            onEndCall: () {
              _timer?.cancel();
              intake.submitTurn(patientSpeech: 'दो दिन से सिरदर्द और बुखार');
              Navigator.of(context).pushReplacementNamed('/summary');
            },
          ),
        ),
      ),
    );
  }
}
