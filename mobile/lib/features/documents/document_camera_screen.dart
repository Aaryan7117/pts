import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/language_provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';

/// Screen 13 — Document Camera Capture
/// 4:3 alignment frame guide with high-tactile shutter CTA
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 13)
class DocumentCameraScreen extends StatelessWidget {
  const DocumentCameraScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.read<IntakeProvider>();

    final encounter = context.read<EncounterProvider>();

    return MediScaffold(
      title: 'Align Document',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        children: [
          const SizedBox(height: MediDimensions.space12),
          Text(
            'Hold prescription within the frame',
            style: MediTypography.headlineMedium.copyWith(fontSize: 22),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'Avoid glare and keep corners visible (पर्ची को सीधा रखें)',
            style: TextStyle(fontSize: 15, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space24),

          // 4:3 Camera Viewfinder Mock Frame with Corner Reticles
          Expanded(
            child: AspectRatio(
              aspectRatio: 3 / 4,
              child: Container(
                decoration: BoxDecoration(
                  color: MediColors.slate900,
                  borderRadius: MediDimensions.borderLg,
                  boxShadow: MediDimensions.elevation2,
                ),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // Simulated Prescription Document Silhouette
                    Container(
                      width: 200,
                      height: 280,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: MediColors.white,
                        borderRadius: MediDimensions.borderSm,
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(width: 60, height: 8, color: MediColors.slate300),
                          const SizedBox(height: 12),
                          Container(width: 140, height: 6, color: MediColors.slate200),
                          const SizedBox(height: 6),
                          Container(width: 110, height: 6, color: MediColors.slate200),
                          const SizedBox(height: 16),
                          const Text('Rx', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: MediColors.brandPrimary)),
                          const SizedBox(height: 8),
                          Container(width: 120, height: 6, color: MediColors.blue200),
                          const SizedBox(height: 6),
                          Container(width: 90, height: 6, color: MediColors.blue200),
                        ],
                      ),
                    ),
                    // Reticles / Border Box
                    Container(
                      margin: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        border: Border.all(color: MediColors.white.withValues(alpha: 0.8), width: 2.5),
                        borderRadius: MediDimensions.borderMd,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: MediDimensions.space24),
        ],
      ),
      bottomBar: SizedBox(
        height: 72,
        child: ElevatedButton.icon(
          onPressed: () {
            final encId = encounter.encounterId ?? 'enc-001';
            intake.processDocument(encId);
            Navigator.of(context).pushNamed('/ocr_processing');
          },
          icon: const Icon(Icons.camera_rounded, size: 32),
          label: const Text('Capture Document (फोटो खींचें)', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
          style: ElevatedButton.styleFrom(
            backgroundColor: MediColors.brandPrimary,
            foregroundColor: MediColors.white,
            shape: RoundedRectangleBorder(borderRadius: MediDimensions.borderXl),
          ),
        ),
      ),
    );
  }
}
