import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';
import '../../core/widgets/secondary_button.dart';

/// Screen 14 — OCR Processing Animation
/// Laser scanner line simulation during optical character recognition.
/// If the upload fails (network error), shows a Retry / Skip card instead of
/// silently pushing an empty result screen.
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 14)
class OcrProcessingScreen extends StatefulWidget {
  const OcrProcessingScreen({super.key});

  @override
  State<OcrProcessingScreen> createState() => _OcrProcessingScreenState();
}

class _OcrProcessingScreenState extends State<OcrProcessingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  bool _showError = false;

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

    if (!mounted) return;

    // D-05c: If network call failed, show error state instead of empty result
    if (intake.ocrFailed) {
      setState(() => _showError = true);
      return;
    }

    Navigator.of(context).pushReplacementNamed('/ocr_result');
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();

    if (_showError) {
      return _buildErrorState(context, lang);
    }

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
              'Identifying medicine names, dosages and doctor notes...',
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

  Widget _buildErrorState(BuildContext context, LanguageProvider lang) {
    return MediScaffold(
      title: 'Upload Failed',
      currentLanguage: lang.currentLanguage,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(MediDimensions.space24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: MediColors.triageTint,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.cloud_off_rounded, size: 44, color: MediColors.triageRed),
              ),
              const SizedBox(height: MediDimensions.space24),
              Text(
                'Could Not Read Prescription',
                style: MediTypography.headlineLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: MediDimensions.space12),
              const Text(
                'The document could not be uploaded. This may be a network issue or the backend service may be unavailable.\n\nPlease check your connection and try again.',
                style: TextStyle(fontSize: 16, color: MediColors.textMuted),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: 'Try Again (दोबारा कोशिश करें)',
            icon: Icons.refresh_rounded,
            onPressed: () => Navigator.of(context).pop(),
          ),
          const SizedBox(height: MediDimensions.space8),
          SecondaryActionButton(
            label: 'Skip — Continue Without Document',
            onPressed: () => Navigator.of(context).pushNamedAndRemoveUntil(
              '/vitals',
              (route) => route.settings.name == '/welcome',
            ),
          ),
        ],
      ),
    );
  }
}
