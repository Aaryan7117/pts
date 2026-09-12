import 'package:flutter/material.dart';
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
                child: Container(
                  width: 320,
                  height: 440,
                  padding: const EdgeInsets.all(MediDimensions.space20),
                  decoration: BoxDecoration(
                    color: MediColors.white,
                    borderRadius: MediDimensions.borderMd,
                    boxShadow: MediDimensions.elevation2,
                    border: Border.all(color: MediColors.borderStrong),
                  ),
                  child: Stack(
                    children: [
                      // Prescription Header & Doctor Info
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text('CITY CIVIL HOSPITAL OPD', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              Text('Date: 10/09/2026', style: TextStyle(fontSize: 12, color: MediColors.textMuted)),
                            ],
                          ),
                          const Divider(),
                          const Text('Patient: Ram Lal (M/45)', style: TextStyle(fontSize: 13)),
                          const SizedBox(height: 12),
                          const Text('Rx', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: MediColors.brandPrimary)),
                          const SizedBox(height: 12),
                          const Text('1. Tab Paracetamol 650mg BD', style: TextStyle(fontSize: 15)),
                          const SizedBox(height: 16),
                          const Text('2. Tab Cetirizine 10mg HS', style: TextStyle(fontSize: 15)),
                          const SizedBox(height: 16),
                          const Text('3. Syp Antacid 10ml TDS', style: TextStyle(fontSize: 15)),
                          const Spacer(),
                          const Align(
                            alignment: Alignment.bottomRight,
                            child: Text('Dr. S. Sharma\nReg: 48291', textAlign: TextAlign.right, style: TextStyle(fontSize: 12)),
                          ),
                        ],
                      ),
                      // Evidence Bounding Box Highlight Overlay
                      Positioned(
                        top: 110,
                        left: 0,
                        right: 40,
                        height: 36,
                        child: Container(
                          decoration: BoxDecoration(
                            border: Border.all(color: MediColors.brandPrimary, width: 2.5),
                            color: MediColors.blue600.withValues(alpha: 0.15),
                            borderRadius: MediDimensions.borderSm,
                          ),
                          alignment: Alignment.centerRight,
                          padding: const EdgeInsets.only(right: 6),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            color: MediColors.brandPrimary,
                            child: const Text('Paracetamol 650mg', style: TextStyle(color: MediColors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
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
}
