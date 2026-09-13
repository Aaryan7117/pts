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

/// Screen 15 — OCR Result & Evidence Highlighting
/// Displays extracted medicines with line citations and evidence grounding
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 15)
class OcrResultScreen extends StatelessWidget {
  const OcrResultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<LanguageProvider>();
    final intake = context.watch<IntakeProvider>();

    final medications = intake.extractedMedications;
    final flaggedInteractions = intake.lastDocumentResult?.flaggedInteractions ?? const [];

    return MediScaffold(
      title: 'Extracted Medications',
      currentLanguage: lang.currentLanguage,
      onLanguageChanged: (l) => lang.setLanguage(l),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Medications Found in Prescription',
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'Extracted from your scanned document. Please verify these match your medicines.',
            style: TextStyle(fontSize: 16, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space16),
          if (flaggedInteractions.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(MediDimensions.space12),
              decoration: BoxDecoration(
                color: MediColors.amber50,
                borderRadius: MediDimensions.borderMd,
                border: Border.all(color: MediColors.amber800),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: MediColors.amber800, size: 28),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Drug Interaction Advisory',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: MediColors.amber900),
                        ),
                        const SizedBox(height: 4),
                        ...flaggedInteractions.map((alert) => Text('• $alert', style: const TextStyle(fontSize: 13, color: MediColors.textPrimary))),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: MediDimensions.space16),
          ],
          Expanded(
            child: medications.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.description_outlined, size: 64, color: MediColors.slate400),
                        const SizedBox(height: 16),
                        const Text(
                          'No Medications Detected\n(कोई दवा नहीं मिली)',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: MediColors.textMuted),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'You can continue to vitals or rescan a clearer photo.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 14, color: MediColors.textMuted),
                        ),
                      ],
                    ),
                  )
                : ListView.separated(
                    itemCount: medications.length,
                    separatorBuilder: (_, _) => const SizedBox(height: MediDimensions.space12),
                    itemBuilder: (context, index) {
                final med = medications[index];
                return Container(
                  padding: const EdgeInsets.all(MediDimensions.space16),
                  decoration: BoxDecoration(
                    color: MediColors.surface,
                    borderRadius: MediDimensions.borderLg,
                    border: Border.all(color: MediColors.border),
                    boxShadow: MediDimensions.elevation1,
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: MediColors.emerald50,
                          borderRadius: MediDimensions.borderMd,
                        ),
                        child: const Icon(Icons.medication_rounded, color: MediColors.emerald800, size: 28),
                      ),
                      const SizedBox(width: MediDimensions.space16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              med.name,
                              style: MediTypography.headlineMedium.copyWith(fontSize: 20),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '${med.dose ?? ''} • ${med.frequency ?? ''}',
                              style: MediTypography.bodyMedium,
                            ),
                            const SizedBox(height: 6),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: MediColors.blue50,
                                    borderRadius: MediDimensions.borderSm,
                                  ),
                                  child: Text(
                                    'OCR Line ${med.sourceLines.join(", ")}',
                                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: MediColors.brandPrimary),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Confidence: ${(med.confidence * 100).toInt()}%',
                                  style: const TextStyle(fontSize: 12, color: MediColors.textMuted),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const Icon(Icons.check_circle, color: MediColors.emerald700, size: 28),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
      bottomBar: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          PrimaryActionButton(
            label: 'Confirm & Continue (दवाएँ सही हैं)',
            icon: Icons.check_circle_outline,
            onPressed: () => Navigator.of(context).pushNamed('/vitals'),
          ),
          const SizedBox(height: MediDimensions.space8),
          SecondaryActionButton(
            label: 'Inspect Source Document (मूल पर्ची देखें)',
            icon: Icons.image_search_rounded,
            onPressed: () => Navigator.of(context).pushNamed('/doc_view'),
          ),
        ],
      ),
    );
  }
}
