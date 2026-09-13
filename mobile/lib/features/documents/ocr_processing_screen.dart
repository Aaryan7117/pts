import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';

/// Screen 14 — OCR Processing Animation
/// Laser scanner line simulation during optical character recognition
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 14)
class OcrProcessingScreen extends StatefulWidget {
  const OcrProcessingScreen({super.key});

  @override
  State<OcrProcessingScreen> createState() => _OcrProcessingScreenState();
}

class _OcrProcessingScreenState extends State<OcrProcessingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _waitForOcrCompletion();
  }

  void _waitForOcrCompletion() async {
    final intake = context.read<IntakeProvider>();
    // Show scanning animation for at least 1400ms
    await Future.delayed(const Duration(milliseconds: 1400));

    // Wait until document upload & OCR parsing finishes
    while (mounted && intake.isProcessingTurn) {
      await Future.delayed(const Duration(milliseconds: 200));
    }

    if (mounted) {
      Navigator.of(context).pushReplacementNamed('/ocr_result');
    }
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    return MediScaffold(
      title: 'Reading Prescription',
      showBack: false,
      currentLanguage: lang.currentLanguage,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                Container(
                  width: 140,
                  height: 190,
                  decoration: BoxDecoration(
                    color: MediColors.surface,
                    borderRadius: MediDimensions.borderMd,
                    border: Border.all(color: MediColors.borderStrong, width: 2),
                    boxShadow: MediDimensions.elevation2,
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: List.generate(
                      5,
                      (_) => Container(
                        width: 100,
                        height: 6,
                        decoration: BoxDecoration(
                          color: MediColors.slate300,
                          borderRadius: MediDimensions.borderSm,
                        ),
                      ),
                    ),
                  ),
                ),
                // Moving Laser Scan Line
                Positioned(
                  top: 20,
                  child: AnimatedBuilder(
                    animation: _animController,
                    builder: (context, child) {
                      return Transform.translate(
                        offset: Offset(0, _animController.value * 150),
                        child: Container(
                          width: 140,
                          height: 3,
                          decoration: const BoxDecoration(
                            color: MediColors.brandInteractive,
                            boxShadow: [
                              BoxShadow(color: MediColors.brandInteractive, blurRadius: 6),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: MediDimensions.space32),
            Text(
              'Analyzing Prescription with OCR',
              style: MediTypography.headlineLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space8),
            const Text(
              'Identifying doctor handwriting, medicine names, and dosages...',
              style: TextStyle(fontSize: 16, color: MediColors.textMuted),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: MediDimensions.space24),
            const SizedBox(
              width: 36,
              height: 36,
              child: CircularProgressIndicator(
                strokeWidth: 3.5,
                valueColor: AlwaysStoppedAnimation<Color>(MediColors.brandPrimary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
