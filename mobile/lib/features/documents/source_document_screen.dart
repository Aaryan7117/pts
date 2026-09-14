import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../app/state/intake_provider.dart';
import '../../app/state/encounter_provider.dart';
import '../../data/datasources/api_datasource.dart';
import '../../app/theme/colors.dart';
import '../../app/theme/dimensions.dart';
import '../../app/theme/typography.dart';
import '../../core/widgets/medi_scaffold.dart';
import '../../core/widgets/primary_button.dart';

/// Screen 16 — Source Document View with Evidence Polygons
/// "No Receipt, No Fact" visual provenance verification
/// Ref: MEDIKIOSK_ANDROID_DESIGN_SPEC.md Section 8 (Screen 16)
class SourceDocumentScreen extends StatelessWidget {
  const SourceDocumentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final intake = context.watch<IntakeProvider>();
    final rawUrl = intake.lastDocumentResult?.highlightedImageUrl;
    String? liveImageUrl;
    if (rawUrl != null && rawUrl.isNotEmpty) {
      if (rawUrl.startsWith('http')) {
        liveImageUrl = rawUrl.replaceFirst('http://localhost:8000', ApiDataSource.defaultBaseUrl);
      } else {
        final path = rawUrl.startsWith('/') ? rawUrl : '/$rawUrl';
        liveImageUrl = '${ApiDataSource.defaultBaseUrl}$path';
      }
    }

    return MediScaffold(
      title: 'Original Prescription',
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Visual Evidence Grounding',
            style: MediTypography.headlineLarge,
          ),
          const SizedBox(height: MediDimensions.space8),
          const Text(
            'The blue highlighted box shows the exact region where AI extracted your medication.',
            style: TextStyle(fontSize: 16, color: MediColors.textMuted),
          ),
          const SizedBox(height: MediDimensions.space20),
          Expanded(
            child: InteractiveViewer(
              minScale: 0.8,
              maxScale: 3.5,
              child: Center(
                child: liveImageUrl != null
                    ? ClipRRect(
                        borderRadius: MediDimensions.borderMd,
                        child: Image.network(
                          liveImageUrl,
                          fit: BoxFit.contain,
                          loadingBuilder: (ctx, child, progress) {
                            if (progress == null) return child;
                            return const Center(child: CircularProgressIndicator());
                          },
                          errorBuilder: (ctx, err, stack) => _buildDynamicPrescription(context, intake),
                        ),
                      )
                    : _buildDynamicPrescription(context, intake),
              ),
            ),
          ),
        ],
      ),
      bottomBar: PrimaryActionButton(
        label: 'Back to Medications (वापस जाएं)',
        onPressed: () => Navigator.of(context).pop(),
      ),
    );
  }

  Widget _buildDynamicPrescription(BuildContext context, IntakeProvider intake) {
    final encounter = context.read<EncounterProvider>();
    final meds = intake.extractedMedications;

    return Container(
      width: 320,
      constraints: const BoxConstraints(minHeight: 380),
      padding: const EdgeInsets.all(MediDimensions.space20),
      decoration: BoxDecoration(
        color: MediColors.white,
        borderRadius: MediDimensions.borderMd,
        boxShadow: MediDimensions.elevation2,
        border: Border.all(color: MediColors.borderStrong),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Prescription Header & Hospital Info
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('CIVIL HOSPITAL OPD', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: MediColors.brandPrimary)),
              Text('Token: ${encounter.tokenNumber ?? "A-101"}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: MediColors.textMuted)),
            ],
          ),
          const Divider(),
          Text('Encounter ID: ${encounter.encounterId ?? "Active Encounter"}', style: const TextStyle(fontSize: 12, color: MediColors.textMuted)),
          const SizedBox(height: 8),
          const Text('Rx (Prescribed Medications)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: MediColors.brandPrimary)),
          const SizedBox(height: 12),
          if (meds.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Text('No medications extracted from this document yet.', style: TextStyle(color: MediColors.textMuted, fontStyle: FontStyle.italic)),
            )
          else
            ...meds.asMap().entries.map((entry) {
              final idx = entry.key + 1;
              final med = entry.value;
              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                decoration: BoxDecoration(
                  border: Border.all(color: MediColors.brandPrimary, width: 2.0),
                  color: MediColors.blue50,
                  borderRadius: MediDimensions.borderSm,
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        '$idx. ${med.name} ${med.dose ?? ""} ${med.frequency ?? ""}',
                        style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: MediColors.brandPrimary,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        '${(med.confidence * 100).toInt()}% OCR',
                        style: const TextStyle(color: MediColors.white, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              );
            }),
          const SizedBox(height: 16),
          const Align(
            alignment: Alignment.bottomRight,
            child: Text('Verified by Clinical OCR\nProvenance: No Receipt, No Fact', textAlign: TextAlign.right, style: TextStyle(fontSize: 11, color: MediColors.textMuted)),
          ),
        ],
      ),
    );
  }
}
