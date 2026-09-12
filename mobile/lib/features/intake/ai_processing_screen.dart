import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';

/// Screen 09 — AI Processing
/// Calming clinical animation during concept extraction and semantic normalization
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 09)
class AiProcessingScreen extends StatefulWidget {
  const AiProcessingScreen({super.key});

  @override
  State<AiProcessingScreen> createState() => _AiProcessingScreenState();
}

class _AiProcessingScreenState extends State<AiProcessingScreen> {
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _timer = Timer(const Duration(milliseconds: 1400), () {
      if (mounted) {
        final intake = context.read<IntakeProvider>();
        if (intake.isInterviewCompleted) {
          Navigator.of(context).pushReplacementNamed('/summary');
        } else {
          Navigator.of(context).pushReplacementNamed('/followup');
        }
      }
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: 'Analyzing Symptoms',
      showBack: false,
      currentLanguage: lang.currentLanguage,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: MediColors.blue50,
                shape: BoxShape.circle,
                boxShadow: MediDimensions.voiceGlow,
              ),
              child: const Icon(
                Icons.psychology_rounded,
                size: 56,
                color: MediColors.brandPrimary,
              ),
            ),
            const SizedBox(height: MediDimensions.space32),
            Text(
              lang.translate('processing'),
              style: MediTypography.headlineLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space12),
            const Text(
              'Structuring facts and checking clinical safety guidelines...',
              style: TextStyle(fontSize: 16, color: MediColors.textMuted),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space40),
            const SizedBox(
              width: 48,
              height: 48,
              child: CircularProgressIndicator(
                strokeWidth: 4.0,
                valueColor: AlwaysStoppedAnimation<Color>(MediColors.brandPrimary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
